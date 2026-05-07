"""
============================================================================
COMPREHENSIVE IDEA EMBEDDING SCRIPT
============================================================================
Embeds all idea evolutions and conversation turns using two models:
- Qwen/Qwen3-Embedding-0.6B (lightweight)
- Qwen/Qwen3-Embedding-4B (robust)

Output: Parquet files with embeddings indexed by original idea file_id
============================================================================
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm
import torch
import gc
import argparse
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration for embedding pipeline."""
    
    # Paths (update these for your environment)
    IDEAS_PARQUET_PATH = os.getenv('IDEAS_PARQUET_PATH', 'processed/ideas_with_conversations_refactored.parquet')
    OUTPUT_DIR = os.getenv('EMBEDDINGS_DIR', 'data_external/embeddings')
    HUGGINGFACE_CACHE = os.getenv('HUGGINGFACE_CACHE')
    
    # Models to use
    MODELS = {
        'qwen3_0.6b': 'Qwen/Qwen3-Embedding-0.6B',
        'qwen3_4b': 'Qwen/Qwen3-Embedding-4B'
    }
    
    # Batch sizes (adjust based on GPU memory)
    BATCH_SIZES = {
        'qwen3_0.6b': 128,  # Increased for better GPU utilization
        'qwen3_4b': 32      # Increased from 8 to 32
    }
    
    # Use half precision for efficiency
    USE_FP16 = True
    
    # Maximum text length (characters) to embed
    MAX_TEXT_LENGTH = 16384
    INSTRUCTION_STYLE = 'none'  # <-- Start with this!
    
    # Debug mode: only process a few sentences for testing
    DEBUG_MODE = False
    DEBUG_LIMIT = 5  # Number of ideas to process in debug mode


# ============================================================================
# EMBEDDING PIPELINE
# ============================================================================

class IdeaEmbeddingPipeline:
    """Pipeline to embed all ideas, their evolutions, and conversation turns."""
    
    def __init__(self, config: Config):
        self.config = config
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🔧 Device: {self.device}")
        
        # Create output directory
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    def load_ideas(self) -> pd.DataFrame:
        """Load the ideas dataframe with conversation data."""
        print(f"\n📥 Loading ideas from: {self.config.IDEAS_PARQUET_PATH}")
        ideas = pd.read_parquet(self.config.IDEAS_PARQUET_PATH)
        
        if self.config.DEBUG_MODE:
            print(f"   🐛 DEBUG MODE: Limiting to {self.config.DEBUG_LIMIT} ideas")
            ideas = ideas.head(self.config.DEBUG_LIMIT)
        
        print(f"   Loaded {len(ideas)} ideas")
        return ideas
    
    def load_model(self, model_key: str):
        """Load a sentence transformer model."""
        from sentence_transformers import SentenceTransformer
        
        model_name = self.config.MODELS[model_key]
        print(f"\n📥 Loading model: {model_name}")
        
        model = SentenceTransformer(
            model_name,
            cache_folder=self.config.HUGGINGFACE_CACHE,
            trust_remote_code=True,
            device=self.device
        )
        
        if self.config.USE_FP16 and self.device == 'cuda':
            model.half()
            print("   Using FP16 precision")
            # Set model to eval mode for inference optimization
            model.eval()
            # Disable gradient computation for faster inference
            for param in model.parameters():
                param.requires_grad = False
        
        print(f"   Embedding dimension: {model.get_sentence_embedding_dimension()}")
        return model
    
    def unload_model(self, model):
        """Free GPU memory after using a model."""
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        print("   Model unloaded, GPU memory freed")
    
    @staticmethod
    def get_qwen3_prompt(text: str, task: str = 'similarity', style: str = 'none') -> str:
        """
        Format text with Qwen3's instruction-aware prompt.
        
        Args:
            text: The text to embed
            task: 'similarity' for turns, 'evolution' for idea evolution
            style: 'none' | 'minimal' | 'task_specific'
        
        Instruction Strategy Rationale:
        - 'none': Raw text. Best for trajectory analysis where you want 
                  pure semantic positioning without retrieval bias.
        - 'minimal': Just 'Query: {text}'. Activates instruction-following
                     but doesn't bias toward specific retrieval tasks.
        - 'task_specific': Full instructions. May bias embeddings toward
                           similarity rather than preserving distances.
        
        For volatility/drift analysis, 'none' or 'minimal' recommended
        to avoid instruction leakage in short texts.
        """
        if style == 'none':
            return text
        
        elif style == 'minimal':
            return f'Query: {text}'
        
        elif style == 'task_specific':
            if task == 'evolution':
                instruction = "Given an idea statement, encode its conceptual content"
            else:  # similarity
                instruction = "Given a discussion turn, encode its semantic meaning"
            return f'Instruct: {instruction}\nQuery: {text}'
        
        else:
            raise ValueError(f"Unknown instruction style: {style}")
    
    def parse_json_field(self, json_str: Optional[str]) -> List[Dict]:
        """Safely parse a JSON string field."""
        if pd.isna(json_str) or json_str is None or json_str == '':
            return []
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def extract_texts_from_idea(self, row: pd.Series) -> Dict[str, List[Dict]]:
        """
        Extract all embeddable texts from an idea row.
        
        Returns dict with:
        - 'idea': the main idea text
        - 'conversation_turns': list of {turn_idx, text}
        - 'idea_evolution': list of {step_idx, text}
        """
        file_id = row['file_id']
        # Handle both question_id (lowercase) and question_ID (uppercase)
        question_id = row.get('question_id', row.get('question_ID', None))
        texts = {
            'file_id': file_id,
            'question_id': question_id,
            'idea': None,
            'conversation_turns': [],
            'idea_evolution': []
        }
        
        # Main idea text
        idea_col = 'paraphrased_idea' if 'paraphrased_idea' in row.index else 'final_idea'
        if idea_col in row.index and pd.notna(row[idea_col]):
            idea_text = str(row[idea_col]).strip()
            if len(idea_text) > 10:
                texts['idea'] = idea_text[:self.config.MAX_TEXT_LENGTH]
        
        # Conversation turns from conversation_history (new preprocessing format)
        conversation_col = 'conversation_history' if 'conversation_history' in row.index else 'conversation_turns'
        turns_data = self.parse_json_field(row.get(conversation_col))
        
        # Handle different conversation formats
        if isinstance(turns_data, list):
            # Direct list of turns
            turns = turns_data
        elif isinstance(turns_data, dict):
            # Nested format: {'turns': [...]} or direct dict with turn fields
            turns = turns_data.get('turns', [turns_data] if 'response' in turns_data or 'text' in turns_data else [])
        else:
            turns = []
        
        for idx, turn in enumerate(turns):
            if isinstance(turn, dict):
                # Try multiple field names for the text content
                text = turn.get('response') or turn.get('text') or turn.get('message') or turn.get('content') or ''
                text = str(text).strip()
                if len(text.split()) >= 5:
                    texts['conversation_turns'].append({
                        'turn_idx': idx,
                        'text': text[:self.config.MAX_TEXT_LENGTH],
                        'phase': turn.get('phase', ''),
                        'agent_id': turn.get('agent_id', turn.get('speaker', turn.get('role', '')))
                    })
        
        # Idea evolution
        evolution_data = self.parse_json_field(row.get('idea_evolution'))
        
        # Handle different evolution formats
        if isinstance(evolution_data, list):
            evolution = evolution_data
        elif isinstance(evolution_data, dict):
            # Nested format: {'ideas': [...]} or direct dict
            evolution = evolution_data.get('ideas', [evolution_data] if 'idea' in evolution_data or 'idea_content' in evolution_data else [])
        else:
            evolution = []
        
        for idx, step in enumerate(evolution):
            if isinstance(step, dict):
                # Try multiple field names for idea text
                text = step.get('idea_content') or step.get('idea') or step.get('text') or step.get('content') or ''
                text = str(text).strip()
                if len(text.split()) >= 5: 
                    texts['idea_evolution'].append({
                        'step_idx': idx,
                        'text': text[:self.config.MAX_TEXT_LENGTH],
                        'round': step.get('round', step.get('round_num', idx)),
                        'is_initial': step.get('is_initial', idx == 0)
                    })
        
        return texts
    
    def embed_batch(self, model, texts: List[str], task: str = 'similarity') -> np.ndarray:
        """Embed a batch of texts with proper prompting and optimized inference."""
        prompted = [
            self.get_qwen3_prompt(t, task, style=self.config.INSTRUCTION_STYLE) 
            for t in texts
        ]
        
        # Use torch.no_grad() for faster inference and less memory
        with torch.no_grad():
            embeddings = model.encode(
                prompted,
                normalize_embeddings=True,
                show_progress_bar=False,
                convert_to_numpy=True,
                batch_size=len(texts),  # Process entire batch at once
                convert_to_tensor=False  # Directly to numpy for efficiency
            )
        
        return embeddings
    
    def embed_all_ideas(self, ideas: pd.DataFrame, model, model_key: str) -> Dict[str, pd.DataFrame]:
        """
        Embed all ideas, their conversation turns, and evolutions.
        
        Returns dict with three DataFrames:
        - 'ideas': embeddings for main idea texts
        - 'turns': embeddings for conversation turns
        - 'evolution': embeddings for idea evolution steps
        """
        batch_size = self.config.BATCH_SIZES[model_key]
        
        # Extract all texts first (optimized with list comprehension prep)
        print("\n📊 Extracting texts from all ideas...")
        all_texts_data = []
        # Convert to dict records for faster access
        idea_records_list = ideas.to_dict('records')
        for row_dict in tqdm(idea_records_list, desc="Extracting"):
            all_texts_data.append(self.extract_texts_from_idea(pd.Series(row_dict)))
        
        # Debug: Count how many have conversation/evolution data
        if self.config.DEBUG_MODE:
            n_with_convs = sum(1 for d in all_texts_data if len(d['conversation_turns']) > 0)
            n_with_evo = sum(1 for d in all_texts_data if len(d['idea_evolution']) > 0)
            print(f"\n   🐛 DEBUG: Found {n_with_convs} ideas with conversations, {n_with_evo} with evolution")
            if n_with_convs == 0:
                # Show sample data structure for debugging
                sample = ideas.iloc[0] if len(ideas) > 0 else None
                if sample is not None:
                    print(f"   🐛 Sample columns: {list(sample.index)}")
                    if 'conversation_history' in sample.index:
                        conv = sample['conversation_history']
                        print(f"   🐛 conversation_history type: {type(conv)}")
                        if pd.notna(conv):
                            print(f"   🐛 conversation_history preview: {str(conv)[:200]}...")
        
        # ====================================================================
        # EMBED MAIN IDEAS
        # ====================================================================
        print("\n🔄 Embedding main ideas...")
        
        idea_records = []
        idea_texts = []
        idea_file_ids = []
        idea_question_ids = []
        
        for data in all_texts_data:
            if data['idea'] is not None:
                idea_texts.append(data['idea'])
                idea_file_ids.append(data['file_id'])
                idea_question_ids.append(data['question_id'])
        
        if idea_texts:
            # Batch embed with pre-allocation
            print(f"   Embedding {len(idea_texts)} ideas in batches of {batch_size}...")
            n_batches = (len(idea_texts) + batch_size - 1) // batch_size
            all_embeddings = []
            
            for i in tqdm(range(0, len(idea_texts), batch_size), desc="Ideas", total=n_batches):
                batch = idea_texts[i:i+batch_size]
                batch_emb = self.embed_batch(model, batch, task='similarity')
                all_embeddings.append(batch_emb)
                
                # Clear GPU cache periodically to prevent memory buildup
                if (i // batch_size) % 10 == 0 and torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            # Efficient stacking
            all_embeddings = np.vstack(all_embeddings) if len(all_embeddings) > 1 else all_embeddings[0]
            
            # Pre-allocate records list for efficiency
            idea_records = [
                {
                    'file_id': file_id,
                    'question_id': question_id,
                    'embedding': embedding
                }
                for file_id, question_id, embedding in zip(idea_file_ids, idea_question_ids, all_embeddings)
            ]
        
        ideas_df = pd.DataFrame(idea_records)
        print(f"   Embedded {len(ideas_df)} ideas")
        
        # ====================================================================
        # EMBED CONVERSATION TURNS
        # ====================================================================
        print("\n🔄 Embedding conversation turns...")
        
        turn_records = []
        turn_texts = []
        turn_meta = []  # (file_id, turn_idx, phase, agent_id)
        
        for data in all_texts_data:
            for turn in data['conversation_turns']:
                turn_texts.append(turn['text'])
                turn_meta.append({
                    'file_id': data['file_id'],
                    'question_id': data['question_id'],
                    'turn_idx': turn['turn_idx'],
                    'phase': turn['phase'],
                    'agent_id': turn['agent_id']
                })
        
        if turn_texts:
            print(f"   Embedding {len(turn_texts)} turns in batches of {batch_size}...")
            n_batches = (len(turn_texts) + batch_size - 1) // batch_size
            all_embeddings = []
            
            for i in tqdm(range(0, len(turn_texts), batch_size), desc="Turns", total=n_batches):
                batch = turn_texts[i:i+batch_size]
                batch_emb = self.embed_batch(model, batch, task='similarity')
                all_embeddings.append(batch_emb)
                
                # Clear GPU cache periodically
                if (i // batch_size) % 10 == 0 and torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            all_embeddings = np.vstack(all_embeddings) if len(all_embeddings) > 1 else all_embeddings[0]
            
            # Pre-allocate with list comprehension
            turn_records = [
                {**meta, 'embedding': embedding}
                for meta, embedding in zip(turn_meta, all_embeddings)
            ]
        
        turns_df = pd.DataFrame(turn_records)
        print(f"   Embedded {len(turns_df)} conversation turns")
        
        # ====================================================================
        # EMBED IDEA EVOLUTION
        # ====================================================================
        print("\n🔄 Embedding idea evolution steps...")
        
        evo_records = []
        evo_texts = []
        evo_meta = []
        
        for data in all_texts_data:
            for step in data['idea_evolution']:
                evo_texts.append(step['text'])
                evo_meta.append({
                    'file_id': data['file_id'],
                    'question_id': data['question_id'],
                    'step_idx': step['step_idx'],
                    'round': step['round'],
                    'is_initial': step['is_initial']
                })
        
        if evo_texts:
            print(f"   Embedding {len(evo_texts)} evolution steps in batches of {batch_size}...")
            n_batches = (len(evo_texts) + batch_size - 1) // batch_size
            all_embeddings = []
            
            for i in tqdm(range(0, len(evo_texts), batch_size), desc="Evolution", total=n_batches):
                batch = evo_texts[i:i+batch_size]
                batch_emb = self.embed_batch(model, batch, task='evolution')
                all_embeddings.append(batch_emb)
                
                # Clear GPU cache periodically
                if (i // batch_size) % 10 == 0 and torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            all_embeddings = np.vstack(all_embeddings) if len(all_embeddings) > 1 else all_embeddings[0]
            
            # Pre-allocate with list comprehension
            evo_records = [
                {**meta, 'embedding': embedding}
                for meta, embedding in zip(evo_meta, all_embeddings)
            ]
        
        evolution_df = pd.DataFrame(evo_records)
        print(f"   Embedded {len(evolution_df)} evolution steps")
        
        return {
            'ideas': ideas_df,
            'turns': turns_df,
            'evolution': evolution_df
        }
    
    def save_embeddings(self, embeddings: Dict[str, pd.DataFrame], model_key: str):
        """Save embeddings to parquet files."""
        print(f"\n💾 Saving embeddings for {model_key}...")
        
        for name, df in embeddings.items():
            if len(df) == 0:
                print(f"   ⚠️ No data for {name}, skipping")
                continue
            
            # Convert embedding arrays to lists for parquet storage
            df = df.copy()
            df['embedding'] = df['embedding'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
            
            output_path = os.path.join(
                self.config.OUTPUT_DIR, 
                f'{name}_embeddings_{model_key}.parquet'
            )
            df.to_parquet(output_path, index=False)
            print(f"   ✅ Saved: {output_path}")
            print(f"      Shape: {df.shape}")
    
    def create_index_file(self, ideas: pd.DataFrame):
        """Create an index file mapping file_id to idea metadata."""
        print("\n📋 Creating index file...")
        
        # Select key columns for the index (use lowercase question_id if available)
        question_col = 'question_id' if 'question_id' in ideas.columns else 'question_ID'
        index_cols = ['file_id', question_col, 'source', 'models', 'discussion', 'discussion_plan',
                      'avg_creativity_rating', 'avg_novelty_rating', 'avg_usefulness_rating',
                      'conversation_turns', 'has_conversation_data', 'number_of_agents']
        
        available_cols = [c for c in index_cols if c in ideas.columns]
        index_df = ideas[available_cols].copy()
        
        # Standardize to lowercase question_id for consistency
        if 'question_ID' in index_df.columns and 'question_id' not in index_df.columns:
            index_df['question_id'] = index_df['question_ID']
            index_df = index_df.drop(columns=['question_ID'])
        
        output_path = os.path.join(self.config.OUTPUT_DIR, 'embedding_index.parquet')
        index_df.to_parquet(output_path, index=False)
        print(f"   ✅ Saved: {output_path}")
        print(f"      Contains {len(index_df)} ideas with metadata")
    
    def run(self, models_to_run: Optional[List[str]] = None):
        """Run the full embedding pipeline."""
        start_time = datetime.now()
        print("="*80)
        print("COMPREHENSIVE IDEA EMBEDDING PIPELINE")
        print(f"Started: {start_time}")
        print("="*80)
        
        # Load ideas
        ideas = self.load_ideas()
        
        # Create index file
        self.create_index_file(ideas)
        
        # Determine which models to run
        if models_to_run is None:
            models_to_run = list(self.config.MODELS.keys())
        
        # Run embedding for each model
        for model_key in models_to_run:
            print(f"\n{'='*80}")
            print(f"PROCESSING WITH: {model_key}")
            print(f"{'='*80}")
            
            try:
                # Load model
                model = self.load_model(model_key)
                
                # Embed all texts
                embeddings = self.embed_all_ideas(ideas, model, model_key)
                
                # Save embeddings
                self.save_embeddings(embeddings, model_key)
                
                # Unload model to free memory
                self.unload_model(model)
                
            except Exception as e:
                print(f"❌ Error with {model_key}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "="*80)
        print("✅ EMBEDDING PIPELINE COMPLETE")
        print(f"   Duration: {duration}")
        print(f"   Output directory: {self.config.OUTPUT_DIR}")
        print("="*80)


# ============================================================================
# UTILITY FUNCTIONS FOR LOADING EMBEDDINGS
# ============================================================================

def load_embeddings(output_dir: str, model_key: str, data_type: str = 'ideas') -> pd.DataFrame:
    """
    Load embeddings from parquet file.
    
    Args:
        output_dir: Directory where embeddings are saved
        model_key: Model key (e.g., 'qwen3_0.6b' or 'qwen3_4b')
        data_type: 'ideas', 'turns', or 'evolution'
    
    Returns:
        DataFrame with embeddings (embedding column as numpy arrays)
    """
    path = os.path.join(output_dir, f'{data_type}_embeddings_{model_key}.parquet')
    df = pd.read_parquet(path)
    
    # Convert embedding lists back to numpy arrays
    df['embedding'] = df['embedding'].apply(lambda x: np.array(x))
    
    return df


def load_embedding_index(output_dir: str) -> pd.DataFrame:
    """Load the embedding index file with idea metadata."""
    path = os.path.join(output_dir, 'embedding_index.parquet')
    return pd.read_parquet(path)


def merge_embeddings_with_index(embeddings_df: pd.DataFrame, index_df: pd.DataFrame) -> pd.DataFrame:
    """Merge embeddings with the index to get full metadata."""
    return embeddings_df.merge(index_df, on='file_id', how='left')


def get_embeddings_for_idea(file_id: str, output_dir: str, model_key: str) -> Dict:
    """
    Get all embeddings for a specific idea.
    
    Returns dict with:
    - 'idea_embedding': numpy array
    - 'turn_embeddings': list of (turn_idx, embedding) tuples
    - 'evolution_embeddings': list of (step_idx, embedding) tuples
    """
    result = {
        'file_id': file_id,
        'idea_embedding': None,
        'turn_embeddings': [],
        'evolution_embeddings': []
    }
    
    # Load idea embedding
    ideas_df = load_embeddings(output_dir, model_key, 'ideas')
    idea_row = ideas_df[ideas_df['file_id'] == file_id]
    if len(idea_row) > 0:
        result['idea_embedding'] = idea_row['embedding'].values[0]
    
    # Load turn embeddings
    turns_df = load_embeddings(output_dir, model_key, 'turns')
    turn_rows = turns_df[turns_df['file_id'] == file_id].sort_values('turn_idx')
    for _, row in turn_rows.iterrows():
        result['turn_embeddings'].append((row['turn_idx'], row['embedding']))
    
    # Load evolution embeddings
    evo_df = load_embeddings(output_dir, model_key, 'evolution')
    evo_rows = evo_df[evo_df['file_id'] == file_id].sort_values('step_idx')
    for _, row in evo_rows.iterrows():
        result['evolution_embeddings'].append((row['step_idx'], row['embedding']))
    
    return result


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Embed all ideas with Qwen3 models')
    parser.add_argument('--ideas-path', type=str, default=None,
                        help='Path to ideas parquet file')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Output directory for embeddings')
    parser.add_argument('--cache-dir', type=str, default=None,
                        help='HuggingFace cache directory')
    parser.add_argument('--models', type=str, nargs='+', 
                        choices=['qwen3_0.6b', 'qwen3_4b'],
                        default=['qwen3_0.6b', 'qwen3_4b'],
                        help='Models to run')
    parser.add_argument('--batch-size-0_6b', type=int, default=32,
                        help='Batch size for 0.6B model', dest='batch_size_0_6b')
    parser.add_argument('--batch-size-4b', type=int, default=8,
                        help='Batch size for 4B model')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode (only process 5 ideas)')
    parser.add_argument('--debug-limit', type=int, default=5,
                        help='Number of ideas to process in debug mode')
    
    args = parser.parse_args()
    
    # Update config with command line arguments
    config = Config()
    
    if args.ideas_path:
        config.IDEAS_PARQUET_PATH = args.ideas_path
    if args.output_dir:
        config.OUTPUT_DIR = args.output_dir
    if args.cache_dir:
        config.HUGGINGFACE_CACHE = args.cache_dir
    
    config.BATCH_SIZES['qwen3_0.6b'] = args.batch_size_0_6b
    config.BATCH_SIZES['qwen3_4b'] = args.batch_size_4b
    
    if args.debug:
        config.DEBUG_MODE = True
        config.DEBUG_LIMIT = args.debug_limit
    
    # Run pipeline
    pipeline = IdeaEmbeddingPipeline(config)
    pipeline.run(models_to_run=args.models)


if __name__ == '__main__':
    main()


# ============================================================================
# EXAMPLE USAGE (for interactive use)
# ============================================================================

"""
# Run from command line:
python embed_all_ideas.py --models qwen3_0.6b qwen3_4b

# Or in Python:

from embed_all_ideas import Config, IdeaEmbeddingPipeline

config = Config()
config.IDEAS_PARQUET_PATH = '/path/to/your/ideas.parquet'
config.OUTPUT_DIR = '/path/to/output'

pipeline = IdeaEmbeddingPipeline(config)
pipeline.run()

# Loading embeddings later:

from embed_all_ideas import load_embeddings, load_embedding_index, merge_embeddings_with_index

# Load embeddings for ideas
ideas_emb = load_embeddings(config.OUTPUT_DIR, 'qwen3_0.6b', 'ideas')

# Load index with metadata
index = load_embedding_index(config.OUTPUT_DIR)

# Merge to get full data
full_data = merge_embeddings_with_index(ideas_emb, index)

# Get all embeddings for a specific idea
from embed_all_ideas import get_embeddings_for_idea
idea_data = get_embeddings_for_idea('some_file_id', config.OUTPUT_DIR, 'qwen3_0.6b')
"""
