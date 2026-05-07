#!/usr/bin/env python3
# paraphrase_ideas_csv.py
import argparse
import pandas as pd
from azure_paraphrase_service import AzureParaphraseService
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os
import time

def paraphrase_idea(idea, paraphrase_service, max_words=100):
    """
    Paraphrase a single idea using the specialized paraphrase service.
    
    Args:
        idea (str): The original idea to paraphrase
        paraphrase_service: The paraphrase service to use
        max_words (int): Maximum word count for the paraphrased idea
        
    Returns:
        dict: Dictionary containing original idea, paraphrased text, and word count
    """
    paraphrased_text = paraphrase_service.paraphrase_idea(idea, max_words)
    
    if paraphrased_text is None:
        # Content was filtered or failed
        return {
            "original": idea,
            "paraphrased": None,
            "word_count": 0
        }
    
    return {
        "original": idea,
        "paraphrased": paraphrased_text,
        "word_count": len(paraphrased_text.split())
    }

def save_progress(output_df, output_file):
    """Save progress to the main output file"""
    output_df.to_csv(output_file, index=False, encoding='utf-8')
    completed_count = output_df['paraphrased_idea'].notna().sum()
    print(f"Progress saved: {completed_count} ideas completed")

def load_existing_progress(output_file):
    """Load existing progress from output file if it exists"""
    if os.path.exists(output_file):
        try:
            existing_df = pd.read_csv(output_file)
            if 'paraphrased_idea' in existing_df.columns:
                completed_mask = existing_df['paraphrased_idea'].notna()
                completed_count = completed_mask.sum()
                print(f"Found existing progress: {completed_count} ideas already completed")
                return existing_df, completed_mask
        except Exception as e:
            print(f"Error loading existing progress: {e}")
    
    return None, None

def main():
    parser = argparse.ArgumentParser(description='Paraphrase ideas from a CSV file using GPT-4.1')
    parser.add_argument('input_file', help='CSV file containing ideas in the "final_idea" column')
    parser.add_argument('output_file', help='Output CSV file to save paraphrased ideas')
    parser.add_argument('--max-words', type=int, default=100, help='Maximum words per paraphrased idea')
    parser.add_argument('--max-workers', type=int, default=10, help='Maximum number of concurrent API calls')
    parser.add_argument('--save-interval', type=int, default=50, help='Save progress every N completed ideas')
    parser.add_argument('--resume', action='store_true', help='Resume from existing output file if it exists')
    
    args = parser.parse_args()
    
    # Initialize the paraphrase service
    paraphrase_service = AzureParaphraseService()
    
    # Load ideas from CSV file
    try:
        df = pd.read_csv(args.input_file)

        if 'final_idea' not in df.columns:
            raise ValueError("Input CSV file must contain a 'final_idea' column")
        
        # Keep track of original dataframe and valid rows
        valid_rows = df['final_idea'].notna()
        ideas = df.loc[valid_rows, 'final_idea'].tolist()
        valid_indices = df.index[valid_rows].tolist()
    except Exception as e:
        print(f"Error loading ideas from {args.input_file}: {e}")
        return
    
    # Check for existing progress if resume is enabled
    existing_df = None
    completed_mask = None
    if args.resume:
        existing_df, completed_mask = load_existing_progress(args.output_file)
    
    # Create output dataframe
    if existing_df is not None:
        output_df = existing_df.copy()
        # Find which ideas still need processing
        already_completed = completed_mask & valid_rows
        remaining_mask = valid_rows & ~already_completed
        remaining_indices = df.index[remaining_mask].tolist()
        remaining_ideas = df.loc[remaining_mask, 'final_idea'].tolist()
        
        print(f"Resuming: {already_completed.sum()} already completed, {len(remaining_ideas)} remaining")
        
        # Update variables for remaining work ONLY (keep original for indexing)
        ideas_to_process = remaining_ideas
        indices_to_process = remaining_indices
    else:
        # Create a copy of the original dataframe
        output_df = df.copy()
        
        # Add new columns for paraphrased content
        output_df['paraphrased_idea'] = None
        output_df['paraphrased_word_count'] = None
        
        # Process all ideas
        ideas_to_process = ideas
        indices_to_process = valid_indices
    
    if len(ideas_to_process) == 0:
        print("All ideas have already been processed!")
        return
    
    # Process ideas in parallel with periodic saving
    print(f"Processing {len(ideas_to_process)} ideas with {args.max_workers} concurrent workers...")
    
    # Use ThreadPoolExecutor for parallel processing
    last_save_count = 0
    
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(paraphrase_idea, idea, paraphrase_service, args.max_words): i 
            for i, idea in enumerate(ideas_to_process)
        }
        
        # Collect results as they complete
        completed_count = 0
        results_dict = {}  # Store results by index
        
        for future in as_completed(future_to_index):
            completed_count += 1
            index = future_to_index[future]
            
            try:
                result = future.result(timeout=30)  # Add timeout to prevent hanging
                results_dict[index] = result
                
                # Fill in the result immediately
                valid_idx = indices_to_process[index]
                if result['paraphrased'] is not None:
                    output_df.loc[valid_idx, 'paraphrased_idea'] = result['paraphrased']
                    output_df.loc[valid_idx, 'paraphrased_word_count'] = result['word_count']
                    print(f"Completed {completed_count}/{len(ideas_to_process)} ideas...")
                else:
                    # Content was filtered - leave empty
                    output_df.loc[valid_idx, 'paraphrased_idea'] = None
                    output_df.loc[valid_idx, 'paraphrased_word_count'] = None
                    print(f"Completed {completed_count}/{len(ideas_to_process)} ideas... (content filtered)")
                
                # Save progress if needed
                if completed_count - last_save_count >= args.save_interval:
                    save_progress(output_df, args.output_file)
                    last_save_count = completed_count
                    
            except Exception as e:
                print(f"Error processing idea {index + 1}: {e}")
                # Add a placeholder result for failed processing
                valid_idx = indices_to_process[index]
                output_df.loc[valid_idx, 'paraphrased_idea'] = f"ERROR: {str(e)}"
                output_df.loc[valid_idx, 'paraphrased_word_count'] = 0
    
    # Save final results
    try:
        output_df.to_csv(args.output_file, index=False, encoding='utf-8')
        total_completed = output_df['paraphrased_idea'].notna().sum()
        print(f"Successfully completed! Final file saved with {total_completed} paraphrased ideas to {args.output_file}")
    except Exception as e:
        print(f"Error saving final results to {args.output_file}: {e}")

if __name__ == "__main__":
    main() 