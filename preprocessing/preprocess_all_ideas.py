"""
============================================================================
COMPREHENSIVE DATA PREPROCESSING PIPELINE
============================================================================
This script:
1. Loads raw ideas with human ratings
2. Cleans and standardizes column names
3. Filters out low-quality ratings (3+ zeros)
4. Computes creativity scores (novelty × usefulness, scaled within question)
5. Creates proper "discussion" column consolidating all discussion types
6. Extracts full conversation history + idea evolution (for parquet)
7. Exports clean CSV (summary) and parquet (with full conversations)
============================================================================
"""

import numpy as np
import pandas as pd
import glob
import os
import json
import re
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# OUTPUT FILE PATHS (modify these as needed)
# ============================================================================
RAW_DATA_PATH = os.getenv('RAW_DATA_PATH', 'processed/final_idea_with_conditions_matched.csv')
RESULTS_BASE_PATH = os.getenv('RESULTS_BASE_PATH', 'data_external/raw_chatlogs/llm/results')
HUMAN_TRANSCRIPTION_DIR = os.getenv('HUMAN_TRANSCRIPTION_DIR', 'data_external/raw_chatlogs/human/transcription_human_data')

# Output files
CSV_OUTPUT = os.getenv('CSV_OUTPUT', 'processed/ideas_with_ratings_clean.csv')
PARQUET_OUTPUT = os.getenv('PARQUET_OUTPUT', 'processed/ideas_with_conversations_refactored.parquet')
SUMMARY_OUTPUT = os.getenv('SUMMARY_OUTPUT', 'processed/discussion_summary_useless.csv')

print("="*80)
print("DATA PREPROCESSING PIPELINE")
print("="*80)

# ============================================================================
# STEP 1: LOAD RAW DATA
# ============================================================================

print("\n📥 Loading raw data...")
merged = pd.read_csv(RAW_DATA_PATH)
print(f"   Loaded {len(merged)} raw ideas")
print(f"   Columns: {len(merged.columns)}")

# ============================================================================
# STEP 2: CLEAN COLUMN NAMES
# ============================================================================

print("\n🧹 Cleaning columns...")

# Remove all "Unnamed: X" columns
unnamed_cols = [col for col in merged.columns if 'Unnamed:' in str(col)]
if unnamed_cols:
    print(f"   Removing {len(unnamed_cols)} unnamed columns: {unnamed_cols}")
    merged = merged.drop(columns=unnamed_cols)

print(f"   Cleaned to {len(merged.columns)} columns")

# ============================================================================
# STEP 3: FILTER LOW-QUALITY RATINGS (3+ zeros)
# ============================================================================

print("\n🔍 Filtering low-quality ratings...")

# Rule: If 3+ raters give 0 score, remove the idea
# If 1-2 raters give 0, replace with NaN

c_cols = ['C2', 'C4', 'C5', 'C7', 'C9']
n_cols = ['N2', 'N4', 'N5', 'N7', 'N9']
u_cols = ['U2', 'U4', 'U5', 'U7', 'U9']

def process_row(row):
    zero_count = (row[c_cols] == 0).sum()
    if zero_count >= 3:
        return None  # Mark for removal
    elif zero_count > 0:
        row[c_cols] = row[c_cols].replace(0, np.nan)
    return row

# Apply processing
filtered_merged = merged.apply(process_row, axis=1)
filtered_merged = filtered_merged.dropna(how='all')

# Replace 0s with NaN in ALL rating columns
cols_to_replace = c_cols + n_cols + u_cols
filtered_merged[cols_to_replace] = filtered_merged[cols_to_replace].replace(0, np.nan)

print(f"   Filtered from {len(merged)} → {len(filtered_merged)} ideas")
print(f"   Removed {len(merged) - len(filtered_merged)} ideas with 3+ zero scores")

# ============================================================================
# STEP 4: COMPUTE CREATIVITY SCORES
# ============================================================================

print("\n📊 Computing creativity scores...")

# Compute raw means
filtered_merged['avg_novelty_rating'] = filtered_merged[n_cols].mean(axis=1, skipna=True)
filtered_merged['avg_usefulness_rating'] = filtered_merged[u_cols].mean(axis=1, skipna=True)

# MinMax scale within each question (to normalize difficulty)
scaler = MinMaxScaler()

def scale_group(group):
    if len(group) > 1:
        return scaler.fit_transform(group.values.reshape(-1, 1)).flatten()
    else:
        return np.zeros(len(group))

filtered_merged['avg_novelty_rating'] = filtered_merged.groupby('question_ID')['avg_novelty_rating'].transform(scale_group)
filtered_merged['avg_usefulness_rating'] = filtered_merged.groupby('question_ID')['avg_usefulness_rating'].transform(scale_group)

# Creativity = Novelty × Usefulness (both scaled 0-1)
filtered_merged['avg_creativity_rating'] = (
    filtered_merged['avg_novelty_rating'] * filtered_merged['avg_usefulness_rating']
)

print(f"   ✅ Creativity scores computed")
print(f"   Mean creativity: {filtered_merged['avg_creativity_rating'].mean():.3f}")
print(f"   Mean novelty: {filtered_merged['avg_novelty_rating'].mean():.3f}")
print(f"   Mean usefulness: {filtered_merged['avg_usefulness_rating'].mean():.3f}")

# ============================================================================
# STEP 5: CREATE UNIFIED "DISCUSSION" COLUMN
# ============================================================================

print("\n🔧 Creating unified discussion column...")

# The problem: discussion info is spread across multiple columns
# - discussion_plan: the discussion method (open, instructed, iterative, etc.)
# - additional_idea_generation_plan: may contain "creative" 
# - idea_generation_plan: baseline generation method

# Strategy: Create a unified "discussion" column that captures the actual discussion type

def create_discussion_column(row):
    """
    Create a single "discussion" column that consolidates:
    - discussion_plan (primary source)
    - additional_idea_generation (may contain "creative")
    - Handles "none", NaN, and empty values
    """
    # Check discussion_plan first
    if pd.notna(row.get('discussion_plan')) and str(row.get('discussion_plan')).strip() not in ['', 'none']:
        return str(row['discussion_plan']).strip()
    
    # Check discussion (old column) 
    if pd.notna(row.get('discussion')) and str(row.get('discussion')).strip() not in ['', 'none']:
        return str(row['discussion']).strip()
    
    # Check if this is a "creative" additional generation condition
    if pd.notna(row.get('additional_idea_generation_plan')) and \
       'creative' in str(row.get('additional_idea_generation_plan')).lower():
        return 'creative'
    
    if pd.notna(row.get('additional_idea_generation')) and \
       'creative' in str(row.get('additional_idea_generation')).lower():
        return 'creative'
    
    # Default: no discussion
    return 'none'

filtered_merged['discussion'] = filtered_merged.apply(create_discussion_column, axis=1)

print(f"   Discussion types:")
print(filtered_merged['discussion'].value_counts())

# ============================================================================
# STEP 6: SPLIT HUMAN VS LLM DATA
# ============================================================================

print("\n📂 Splitting human vs LLM data...")

human_written_data_df = filtered_merged[filtered_merged['source'] == 'human_data'].copy()
llm_written_data_df = filtered_merged[filtered_merged['source'] != 'human_data'].copy()

print(f"   Human ideas: {len(human_written_data_df)}")
print(f"   LLM ideas: {len(llm_written_data_df)}")

# ============================================================================
# STEP 7: SUMMARY STATISTICS
# ============================================================================

print("\n" + "="*80)
print("📊 SUMMARY STATISTICS")
print("="*80)

print("\n1. HUMAN-WRITTEN IDEAS - Overall:")
human_stats_overall = human_written_data_df[
    ['avg_creativity_rating', 'avg_novelty_rating', 'avg_usefulness_rating']
].agg(['mean', 'std', 'count'])
print(human_stats_overall)

print("\n2. LLM-WRITTEN IDEAS - Overall:")
llm_stats_overall = llm_written_data_df[
    ['avg_creativity_rating', 'avg_novelty_rating', 'avg_usefulness_rating']
].agg(['mean', 'std', 'count'])
print(llm_stats_overall)

print("\n3. BY QUESTION (Human):")
human_stats_by_q = human_written_data_df.groupby('question_ID')[
    ['avg_creativity_rating', 'avg_novelty_rating', 'avg_usefulness_rating']
].agg(['mean', 'std', 'count'])
print(human_stats_by_q)

print("\n4. BY QUESTION (LLM):")
llm_stats_by_q = llm_written_data_df.groupby('question_ID')[
    ['avg_creativity_rating', 'avg_novelty_rating', 'avg_usefulness_rating']
].agg(['mean', 'std', 'count'])
print(llm_stats_by_q)

# ============================================================================
# STEP 8: EXTRACT FULL CONVERSATION DATA (for parquet only)
# ============================================================================

print("\n" + "="*80)
print("📝 EXTRACTING FULL CONVERSATION DATA")
print("="*80)

def parse_llm_chat_history(content: str, model_name: str) -> list:
    """Parse chat history from LLM log file."""
    turns = []
    
    chat_history_match = re.search(r'=== Chat History ===\s*\n(.*?)(?:===|$)', content, re.DOTALL)
    if not chat_history_match:
        return turns
    
    chat_content = chat_history_match.group(1)
    
    # Pattern: Agent X(model, phase, Idea Index: ..., Round: Y)
    entry_pattern = re.compile(
        r'(?P<agent>Agent \d+)\s*\(\s*[^,]+,\s*(?P<phase>[^,]+),\s*Idea Index:\s*[^,]+,\s*Round:\s*(?P<round>\d+)\s*\)\s*\n'
        r'-+\s*\n'
        r'Prompt:\s*\n(?P<prompt>.*?)\nResponse:\s*\n(?P<response>.*?)(?=\nAgent \d+\s*\(|$)',
        re.DOTALL
    )
    
    for match in entry_pattern.finditer(chat_content):
        phase = match.group('phase').strip().lower()
        
        # Skip idea_generation and selection phases
        if phase in ['idea_generation', 'selection']:
            continue
        
        turns.append({
            'agent_id': match.group('agent').strip(),
            'model': model_name,
            'phase': phase,
            'round': int(match.group('round')),
            'prompt': match.group('prompt').strip(),
            'response': match.group('response').strip()
        })
    
    return turns

def parse_llm_idea_evolution(content: str, model_name: str, discussion_method: str) -> list:
    """Parse idea evolution from LLM log file."""
    evolution_steps = []
    
    evolution_match = re.search(r'=== Idea Evolution History ===\s*\n(.*?)(?:===|$)', content, re.DOTALL)
    if not evolution_match:
        return evolution_steps
    
    evolution_content = evolution_match.group(1)
    
    # Pattern for round-based evolution (instructed/iterative)
    round_pattern = re.compile(
        r'-- Round (?P<round>\d+) --\s*\n'
        r'Agent:\s*(?P<agent>[^\n]+)\s*\n'
        r'Current Ideas?:\s*\n(?P<idea>.*?)(?=-- Round|-- Idea|$)',
        re.DOTALL
    )
    
    for match in round_pattern.finditer(evolution_content):
        agent_str = match.group('agent').strip()
        evolution_steps.append({
            'round': int(match.group('round')),
            'agent_id': agent_str if agent_str.lower() != 'initial idea' else None,
            'idea_content': match.group('idea').strip(),
            'is_initial': agent_str.lower() == 'initial idea',
            'model': model_name,
            'discussion_method': discussion_method
        })
    
    # Pattern for open discussion (no rounds)
    idea_pattern = re.compile(
        r'-- Idea #(?P<idea_num>[^\n]+) --\s*\n'
        r'Agent:\s*(?P<agent>[^\n]+)\s*\n'
        r'Current Idea:\s*\n(?P<idea>.*?)(?=-- Idea|-- Round|$)',
        re.DOTALL
    )
    
    for match in idea_pattern.finditer(evolution_content):
        evolution_steps.append({
            'round': None,
            'idea_num': match.group('idea_num').strip(),
            'agent_id': match.group('agent').strip(),
            'idea_content': match.group('idea').strip(),
            'is_initial': False,
            'model': model_name,
            'discussion_method': discussion_method
        })
    
    return evolution_steps

def extract_full_conversation_data(file_id, question_ID, row):
    """Extract FULL conversation history + idea evolution from LLM log file."""
    try:
        # Get model and discussion info from the row
        model = row.get('models', 'unknown')
        discussion_plan = row.get('discussion_plan', 'none')
        
        # Skip if no discussion
        if pd.isna(discussion_plan) or str(discussion_plan).lower() in ['none', '', 'nan']:
            return {
                'has_conversation_data': False,
                'conversation_turns': 0,
                'conversation_history': None,
                'idea_evolution': None
            }
        
        # Construct log file path: {RESULTS_BASE_PATH}/{question_ID}/{file_id}.txt
        log_path = os.path.join(RESULTS_BASE_PATH, str(question_ID), f'{file_id}.txt')
        
        if not os.path.exists(log_path):
            # Debug: print first few missing files
            if not hasattr(extract_full_conversation_data, '_missing_count'):
                extract_full_conversation_data._missing_count = 0
            if extract_full_conversation_data._missing_count < 5:
                print(f"      ⚠️ File not found: {log_path}")
                extract_full_conversation_data._missing_count += 1
            return {
                'has_conversation_data': False,
                'conversation_turns': 0,
                'conversation_history': None,
                'idea_evolution': None
            }
        
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata
        metadata = {}
        metadata['has_conversation_data'] = True
        
        # Parse conversation turns
        turns = parse_llm_chat_history(content, model)
        if turns:
            metadata['conversation_history'] = json.dumps(turns, ensure_ascii=False)
            metadata['conversation_turns'] = len(turns)
        else:
            metadata['conversation_history'] = None
            metadata['conversation_turns'] = 0
        
        # Parse idea evolution (skip for 'open' discussion)
        if str(discussion_plan).lower() != 'open':
            evolution = parse_llm_idea_evolution(content, model, discussion_plan)
            if evolution:
                metadata['idea_evolution'] = json.dumps(evolution, ensure_ascii=False)
            else:
                metadata['idea_evolution'] = None
        else:
            metadata['idea_evolution'] = None
        
        return metadata
        
    except Exception as e:
        print(f"      Warning: Failed to extract conversation for {file_id}: {e}")
        import traceback
        traceback.print_exc()
        return {
            'has_conversation_data': False,
            'conversation_turns': 0,
            'conversation_history': None,
            'idea_evolution': None
        }

def extract_human_conversation_data(file_id, question_ID, row):
    """Extract conversation history from human Excel transcripts."""
    try:
        # Extract session ID from file_id (e.g., 'i35328_159' -> '35328')
        match = re.search(r'i(\d+)_', str(file_id))
        if not match:
            return {
                'has_conversation_data': False,
                'conversation_turns': 0,
                'conversation_history': None,
                'idea_evolution': None
            }
        
        session_id = match.group(1)
        
        # Map question to PS number
        TASK_TO_PS = {
            'sorry_pandemic': 'PS1',
            'supply_chain': 'PS2',
            'plastic_waste': 'PS3',
            'education_inequality': 'PS4',
            'employee_attrition': 'PS5',
            'singing_shower': 'PS6'
        }
        
        ps_number = TASK_TO_PS.get(question_ID)
        if not ps_number:
            return {
                'has_conversation_data': False,
                'conversation_turns': 0,
                'conversation_history': None,
                'idea_evolution': None
            }
        
        # Construct transcript file path
        # Find matching file (format: {session_id}_{PS#}_{num_participants}.xlsx)
        pattern = os.path.join(HUMAN_TRANSCRIPTION_DIR, f'{session_id}_{ps_number}_*.xlsx')
        matching_files = glob.glob(pattern)
        
        if not matching_files:
            return {
                'has_conversation_data': False,
                'conversation_turns': 0,
                'conversation_history': None,
                'idea_evolution': None
            }
        
        transcript_path = matching_files[0]
        
        # Read Excel file
        df_transcript = pd.read_excel(transcript_path)
        
        # Extract turns
        turns = []
        speaker_cols = [col for col in df_transcript.columns if col.startswith('Speaker')]
        
        for idx, t_row in df_transcript.iterrows():
            for speaker_col in speaker_cols:
                content = t_row.get(speaker_col)
                if pd.notna(content) and str(content).strip():
                    turns.append({
                        'agent_id': speaker_col,
                        'model': 'human',
                        'phase': 'discussion',
                        'round': idx + 1,
                        'prompt': '',
                        'response': str(content).strip()
                    })
                    break  # Only one speaker per turn
        
        if turns:
            return {
                'has_conversation_data': True,
                'conversation_turns': len(turns),
                'conversation_history': json.dumps(turns, ensure_ascii=False),
                'idea_evolution': None  # Humans don't have idea evolution
            }
        else:
            return {
                'has_conversation_data': False,
                'conversation_turns': 0,
                'conversation_history': None,
                'idea_evolution': None
            }
            
    except Exception as e:
        print(f"      Warning: Failed to extract human conversation for {file_id}: {e}")
        return {
            'has_conversation_data': False,
            'conversation_turns': 0,
            'conversation_history': None,
            'idea_evolution': None
        }

print("\n📊 Extracting full conversation data for ideas...")

# Process each row that needs conversation data (no deduplication, preserve row order)
print(f"   Processing ideas with discussions...")

# Initialize columns
filtered_merged['has_conversation_data'] = False
filtered_merged['conversation_turns'] = 0
filtered_merged['conversation_history'] = None
filtered_merged['idea_evolution'] = None

# Process only LLM ideas with discussion
llm_discussion_mask = (
    (filtered_merged['discussion'] != 'none') &
    (filtered_merged['source'] != 'human_data')
)

print(f"   Found {llm_discussion_mask.sum()} LLM ideas with discussions")

# Extract conversation data row by row - LLM
for idx in filtered_merged[llm_discussion_mask].index:
    if idx % 100 == 0:
        print(f"      Processing LLM row {idx}...")
    
    row = filtered_merged.loc[idx]
    file_id = row['file_id']
    question_ID = row['question_ID']
    
    conv_data = extract_full_conversation_data(file_id, question_ID, row)
    
    # Update the row directly
    filtered_merged.at[idx, 'has_conversation_data'] = conv_data['has_conversation_data']
    filtered_merged.at[idx, 'conversation_turns'] = conv_data['conversation_turns']
    filtered_merged.at[idx, 'conversation_history'] = conv_data['conversation_history']
    filtered_merged.at[idx, 'idea_evolution'] = conv_data['idea_evolution']

# Extract conversation data - HUMAN
human_mask = filtered_merged['source'] == 'human_data'
print(f"\n   Processing {human_mask.sum()} human ideas...")

for idx in filtered_merged[human_mask].index:
    if idx % 100 == 0:
        print(f"      Processing human row {idx}...")
    
    row = filtered_merged.loc[idx]
    file_id = row['file_id']
    question_ID = row['question_ID']
    
    conv_data = extract_human_conversation_data(file_id, question_ID, row)
    
    # Update the row directly
    filtered_merged.at[idx, 'has_conversation_data'] = conv_data['has_conversation_data']
    filtered_merged.at[idx, 'conversation_turns'] = conv_data['conversation_turns']
    filtered_merged.at[idx, 'conversation_history'] = conv_data['conversation_history']
    filtered_merged.at[idx, 'idea_evolution'] = conv_data['idea_evolution']

print(f"\n   ✅ Ideas with conversation data found: {filtered_merged['has_conversation_data'].sum()}")
print(f"   Ideas with conversation_history: {filtered_merged['conversation_history'].notna().sum()}")
print(f"   Ideas with idea_evolution: {filtered_merged['idea_evolution'].notna().sum()}")
print(f"   Ideas without conversation data: {(~filtered_merged['has_conversation_data']).sum()}")

# ============================================================================
# STEP 9: EXPORT CLEAN DATA
# ============================================================================

print("\n" + "="*80)
print("💾 EXPORTING CLEAN DATA")
print("="*80)

# Standardize question_ID to question_id (lowercase) now that all processing is done
if 'question_ID' in filtered_merged.columns:
    filtered_merged['question_id'] = filtered_merged['question_ID']
    filtered_merged = filtered_merged.drop(columns=['question_ID'])
    print("\n✅ Standardized: question_ID → question_id")

# Define core columns for CSV (summary only, NO conversation text)
csv_columns = [
    # Identifiers
    'file_id', 'question_id', 'row_ID', 'run_num',
    
    # Condition metadata
    'condition_code', 'condition_number', 'data_type',
    
    # Discussion configuration
    'discussion', 'discussion_plan', 'discussion_order_plan',
    'idea_generation_plan', 'additional_idea_generation_plan',
    
    # Agent configuration
    'number_of_agents', 'models', 'persona', 'temperature',
    
    # Task configuration
    'task_type', 'replacement_pool_size',
    
    # Results
    'final_idea', 'final_idea_length', 'paraphrased_idea', 'paraphrased_word_count',
    'source', 'final_round', 'total_rounds',
    
    # Conversation metadata (counts only)
    'has_conversation_data', 'conversation_turns',
    
    # Ratings (individual)
    'C2', 'C4', 'C5', 'C7', 'C9',
    'N2', 'N4', 'N5', 'N7', 'N9',
    'U2', 'U4', 'U5', 'U7', 'U9',
    
    # Ratings (aggregated)
    'avg_creativity_rating', 'avg_novelty_rating', 'avg_usefulness_rating',
    
    # Token usage
    'grand_total_tokens', 'total_prompt_tokens', 'total_completion_tokens',
]

# Define columns for PARQUET (everything including full conversations)
parquet_columns = csv_columns.copy() + [
    # Full conversation data (JSON strings)
    'conversation_history',  # Full conversation transcript
    'idea_evolution',        # All intermediate ideas
]

# Filter to columns that actually exist
csv_export_columns = [col for col in csv_columns if col in filtered_merged.columns]
parquet_export_columns = [col for col in parquet_columns if col in filtered_merged.columns]

# Add any important metadata columns we might have missed
metadata_cols = [col for col in filtered_merged.columns if 
                 'phase' in col.lower() or 
                 'method' in col.lower() or
                 'llm_count' in col.lower()]
csv_export_columns.extend([col for col in metadata_cols if col not in csv_export_columns])
parquet_export_columns.extend([col for col in metadata_cols if col not in parquet_export_columns])

# 1. Export clean CSV (summary only, NO conversation text)
print("\n1️⃣ Exporting CSV (summary data only)...")
csv_df = filtered_merged[csv_export_columns].copy()
csv_df.to_csv(CSV_OUTPUT, index=False)
print(f"   ✅ Saved: {CSV_OUTPUT}")
print(f"      Rows: {len(csv_df)}")
print(f"      Columns: {len(csv_df.columns)}")

# 2. Export parquet (WITH full conversation history + idea evolution)
print("\n2️⃣ Exporting Parquet (with full conversation data)...")
parquet_df = filtered_merged[parquet_export_columns].copy()
parquet_df.to_parquet(PARQUET_OUTPUT, index=False)
print(f"   ✅ Saved: {PARQUET_OUTPUT}")
print(f"      Rows: {len(parquet_df)}")
print(f"      Columns: {len(parquet_df.columns)}")
print(f"      Includes:")
print(f"         - conversation_history: {parquet_df['conversation_history'].notna().sum()} ideas")
print(f"         - idea_evolution: {parquet_df['idea_evolution'].notna().sum()} ideas")

# 3. Create a discussion breakdown summary
print("\n" + "="*80)
print("📊 DISCUSSION BREAKDOWN")
print("="*80)

discussion_summary = filtered_merged.groupby(['discussion', 'source']).agg({
    'file_id': 'count',
    'avg_creativity_rating': ['mean', 'std'],
    'avg_novelty_rating': ['mean', 'std'],
    'avg_usefulness_rating': ['mean', 'std']
}).round(3)

print(discussion_summary)

# Save this summary
discussion_summary.to_csv(SUMMARY_OUTPUT)
print(f"\n✅ Saved discussion summary: {SUMMARY_OUTPUT}")

print("\n" + "="*80)
print("✅ PREPROCESSING COMPLETE!")
print("="*80)
print(f"\nFiles created:")
print(f"  1. {CSV_OUTPUT}")
print(f"  2. {PARQUET_OUTPUT}")
print(f"  3. {SUMMARY_OUTPUT}")
print(f"\nKey differences:")
print(f"  - CSV: Summary data only (no full conversations)")
print(f"  - Parquet: Includes full conversation_history + idea_evolution")
print(f"\nReady for trajectory analysis!")



