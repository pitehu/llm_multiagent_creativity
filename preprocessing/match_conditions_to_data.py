#!/usr/bin/env python3
"""
match_conditions_to_data.py

Match experimental conditions from the study plan (Copy of study1_04062025.csv) 
to the actual data (final_idea_with_human_ratings_20251016.csv).

This script:
1. Loads the study plan CSV with condition definitions
2. Loads the actual data CSV with generated ideas
3. Matches each data row to its corresponding condition based on experimental parameters
4. Adds condition number and study design variables to the data
5. Saves the enriched dataset for downstream analysis (e.g., regressions)
"""

import pandas as pd
import numpy as np
import os
import re
from typing import Dict, List, Optional, Tuple
import argparse


def parse_filename_to_config(file_id: str) -> Dict[str, any]:
    """
    Parse the file_id (filename without extension) to extract configuration.
    
    Filename format: model_temp_count_persona_phases_gen_disc_order_pool_max_[min]
    Example: deepseek-R1_gemini-2.5-pro_o3_1_3_different_three_stage_independent_none_fixed_pool_0_60_None
    
    Returns a dict with extracted configuration parameters.
    """
    # Remove .txt extension and version suffix if present
    base_name = file_id.replace('.txt', '')
    base_name = re.sub(r'_v\d+$', '', base_name)  # Remove _v1, _v2, etc.
    
    parts = base_name.split('_')
    
    # Try to identify the parts by pattern matching
    config = {}
    
    # The tricky part is that model names can have underscores (e.g., deepseek-R1_gemini-2.5-pro_o3)
    # We need to work backwards from known fixed positions
    
    # From the end, we usually have:
    # ..._pool_X_maxresponses_[minresponses]
    # ..._pool_X_maxresponses (if no min)
    
    # Find 'pool_' pattern
    pool_idx = None
    for i in range(len(parts) - 1):
        if parts[i] == 'pool':
            pool_idx = i
            break
    
    if pool_idx is None:
        # Can't parse this filename
        return {}
    
    # Extract from the end
    try:
        # pool_size is right after 'pool'
        pool_size = parts[pool_idx + 1] if pool_idx + 1 < len(parts) else None
        
        # max_responses is after pool_size
        max_responses = parts[pool_idx + 2] if pool_idx + 2 < len(parts) else None
        
        # min_responses might be after max_responses (if not 'None')
        min_responses = None
        if pool_idx + 3 < len(parts):
            min_val = parts[pool_idx + 3]
            if min_val and min_val.lower() != 'none':
                min_responses = min_val
        
        # discussion_order is before 'pool'
        discussion_order = parts[pool_idx - 1] if pool_idx > 0 else None
        
        # discussion_method is before discussion_order
        discussion_method = parts[pool_idx - 2] if pool_idx > 1 else None
        
        # generation_method/phases is before discussion_method
        gen_or_phases = parts[pool_idx - 3] if pool_idx > 2 else None
        
        # phases is before that
        phases = parts[pool_idx - 4] if pool_idx > 3 else None
        
        # persona is before phases
        persona = parts[pool_idx - 5] if pool_idx > 4 else None
        
        # llm_count is before persona
        llm_count = parts[pool_idx - 6] if pool_idx > 5 else None
        
        # temperature is before llm_count
        temperature = parts[pool_idx - 7] if pool_idx > 6 else None
        
        # Everything before temperature is the model name (joined back together)
        model_parts = parts[:pool_idx - 7] if pool_idx > 7 else []
        model = '_'.join(model_parts) if model_parts else None
        
        config = {
            'model': model,
            'temperature': temperature,
            'llm_count': llm_count,
            'persona': persona,
            'phases': phases,
            'generation_method': gen_or_phases if phases == 'three_stage' else 'Direct',
            'discussion_method': discussion_method,
            'discussion_order': discussion_order,
            'pool_size': pool_size,
            'max_responses': max_responses,
            'min_responses': min_responses
        }
        
    except (IndexError, ValueError) as e:
        # If parsing fails, return empty config
        return {}
    
    return config


def map_filename_config_to_study1(config: Dict[str, any]) -> Dict[str, any]:
    """
    Map configuration from filename to study1 column format.
    This reverses the logic from map_to_study1_columns in extract_final_ideas.
    """
    # Extract values
    llm_count = config.get('llm_count', '')
    persona_type = config.get('persona', '')
    phases = config.get('phases', '')
    generation_method = config.get('generation_method', '')
    discussion_method = config.get('discussion_method', '')
    pool_size = config.get('pool_size', '0')
    max_responses = config.get('max_responses', '')
    min_responses = config.get('min_responses', '')
    discussion_order = config.get('discussion_order', '')
    
    # Map persona
    persona_map = {
        'none': 'no',
        'same': 'same',
        'different': 'different',
        'no': 'no'  # Already in correct format
    }
    persona = persona_map.get(persona_type, persona_type)
    
    # Map idea_generation
    if phases == 'three_stage':
        if generation_method == 'dependent':
            idea_generation = 'interactive'
        elif generation_method == 'independent':
            idea_generation = 'nominal'
        else:
            idea_generation = ''
    else:
        idea_generation = ''
    
    # Map discussion
    discussion_map = {
        'none': '',
        'all_at_once': 'instructed',
        'iterative_refinement': 'iterative',
        'creative': '',
        'open': 'open'
    }
    discussion = discussion_map.get(discussion_method, discussion_method)
    
    # Map replacement_pool
    if pool_size == '0':
        replacement_pool = 'no'
    elif pool_size == '5':
        replacement_pool = 'top5'
    else:
        replacement_pool = pool_size
    
    # Map additional_idea_generation
    additional_idea_gen = ''
    if discussion_method == 'creative':
        additional_idea_gen = 'creative'
    
    # Map conversation_length
    conversation_length = max_responses
    if min_responses and min_responses.lower() != 'none':
        conversation_length = f"{max_responses} (minimum {min_responses})"
    
    # Map discussion_order
    order_map = {
        'fixed': 'fix',
        'random': 'random',
        'hand_raising': 'raise'
    }
    disc_order = order_map.get(discussion_order, discussion_order)
    
    return {
        'number_of_agents': llm_count,
        'persona': persona,
        'idea_generation': idea_generation,
        'discussion': discussion,
        'replacement_pool': replacement_pool,
        'additional_idea_generation': additional_idea_gen,
        'conversation_length': conversation_length,
        'discussion_order': disc_order
    }


def normalize_value(value) -> str:
    """
    Normalize a value for comparison by converting to lowercase string and handling NaN/None.
    Handles pandas NaN, numpy NaN, None, empty strings, and 'nan' strings.
    """
    # Handle pandas/numpy NaN
    if pd.isna(value):
        return 'none'
    # Handle None
    if value is None:
        return 'none'
    # Convert to string
    str_value = str(value).strip().lower()
    # Handle empty string or 'nan' string
    if str_value == '' or str_value == 'nan':
        return 'none'
    return str_value


def load_study_plan(study_plan_path: str) -> pd.DataFrame:
    """
    Load and clean the study plan CSV.
    
    Returns a DataFrame with columns renamed to match the data file conventions.
    """
    print(f"\n📋 Loading study plan from: {study_plan_path}")
    
    # Load the CSV
    study_plan = pd.read_csv(study_plan_path)
    
    print(f"   ✅ Loaded {len(study_plan)} conditions")
    print(f"   Columns: {list(study_plan.columns)}")
    
    # Rename columns to match conventions (handle typo in original: "geneartion")
    column_mapping = {
        'condition': 'condition_number',
        'number of agents': 'number_of_agents_plan',
        'persona': 'persona_plan',
        'idea geneartion': 'idea_generation_plan',  # Note: typo in original
        'discussion': 'discussion_plan',
        'replacement pool': 'replacement_pool_plan',
        'additional idea generation': 'additional_idea_generation_plan',
        'conversation length': 'conversation_length_plan',
        'discussion order': 'discussion_order_plan'
    }
    
    study_plan = study_plan.rename(columns=column_mapping)
    
    # Remove completely empty rows
    study_plan = study_plan.dropna(how='all')
    
    # Normalize values for matching
    for col in study_plan.columns:
        if col != 'condition_number':
            study_plan[f'{col}_normalized'] = study_plan[col].apply(normalize_value)
    
    print(f"   Cleaned to {len(study_plan)} valid conditions")
    
    return study_plan


def load_data(data_path: str) -> pd.DataFrame:
    """
    Load the actual data CSV with generated ideas.
    """
    print(f"\n📊 Loading data from: {data_path}")
    
    data = pd.read_csv(data_path)
    
    print(f"   ✅ Loaded {len(data)} data rows")
    print(f"   Sample columns: {list(data.columns[:20])}")
    
    return data


def create_matching_key(row: pd.Series, columns: List[str]) -> str:
    """
    Create a normalized matching key from specified columns.
    """
    values = []
    for col in columns:
        if col in row:
            values.append(normalize_value(row[col]))
        else:
            values.append('none')
    return '|'.join(values)


def match_condition(data_row: pd.Series, study_plan: pd.DataFrame) -> Optional[int]:
    """
    Match a data row to a condition in the study plan.
    
    Uses the same mapping logic as map_to_study1_columns() from extract_final_ideas_from_task_configs.py:
    - number_of_agents: direct match
    - persona: 'no' in plan = 'no' in data, 'same' = 'same', 'different' = 'different'
    - idea_generation: 'interactive' in plan = 'interactive' in data, empty in plan = empty/nominal in data
    - discussion: 'instructed' in plan = 'instructed' in data, 'iterative' = 'iterative', 'open' = 'open', empty = empty
    - replacement_pool: empty in plan = 'no' in data, 'no' in plan = 'no' in data, 'top5' = 'top5'
    - additional_idea_generation: 'creative' in plan = 'creative' in data, empty = empty
    - conversation_length: handles "60 (minimum 30)" format
    - discussion_order: 'fix' in plan = 'fix' in data, 'random' = 'random', 'raise' = 'raise', empty = empty
    """
    
    # Extract values from data row (these come from the config mapping)
    num_agents = normalize_value(data_row.get('number_of_agents', ''))
    persona = normalize_value(data_row.get('persona', ''))
    idea_gen = normalize_value(data_row.get('idea_generation', ''))
    discussion = normalize_value(data_row.get('discussion', ''))
    replacement_pool = normalize_value(data_row.get('replacement_pool', ''))
    additional_idea_gen = normalize_value(data_row.get('additional_idea_generation', ''))
    conv_length = normalize_value(data_row.get('conversation_length', ''))
    disc_order = normalize_value(data_row.get('discussion_order', ''))
    
    # Try to find match in study plan
    for idx, plan_row in study_plan.iterrows():
        # 1. Match number_of_agents (direct match)
        plan_agents = plan_row.get('number_of_agents_plan_normalized', 'none')
        if num_agents != plan_agents:
            continue
        
        # 2. Match persona (direct match: no/same/different)
        plan_persona = plan_row.get('persona_plan_normalized', 'none')
        if persona != plan_persona:
            continue
        
        # 3. Match idea_generation
        # In data: 'interactive', 'nominal', or empty
        # In plan: 'interactive' or empty
        plan_idea_gen = plan_row.get('idea_generation_plan_normalized', 'none')
        
        if plan_idea_gen == 'interactive':
            # Plan has 'interactive', data must have 'interactive'
            if idea_gen != 'interactive':
                continue
        else:
            # Plan has empty/none, data can have 'nominal' or empty
            if idea_gen == 'interactive':
                continue
        
        # 4. Match discussion
        # In data: 'instructed', 'iterative', 'open', or empty
        # In plan: 'instructed', 'iterative', 'open', or empty
        plan_discussion = plan_row.get('discussion_plan_normalized', 'none')
        if discussion != plan_discussion:
            continue
        
        # 5. Match replacement_pool
        # CRITICAL: Empty in plan = 'no' in data (from map_to_study1_columns logic)
        # In data: 'no', 'top5', or numeric
        # In plan: empty (maps to 'no'), 'no', 'top5', or numeric
        plan_pool = plan_row.get('replacement_pool_plan_normalized', 'none')
        
        # If plan has empty/none, it maps to 'no' in data
        if plan_pool == 'none':
            if replacement_pool != 'no':
                continue
        else:
            # Otherwise direct match
            if replacement_pool != plan_pool:
                continue
        
        # 6. Match additional_idea_generation
        # In data: 'creative' or empty
        # In plan: 'creative' or empty
        plan_additional = plan_row.get('additional_idea_generation_plan_normalized', 'none')
        if additional_idea_gen != plan_additional:
            continue
        
        # 7. Match conversation_length (handle "60 (minimum 30)" format)
        # In data: '30', '60', '60 (minimum 30)', or may have value when plan is empty
        # In plan: '30', '60', '60 (minimum 30)', or empty
        plan_conv_length = plan_row.get('conversation_length_plan_normalized', 'none')
        
        # If plan has empty/none conversation length, skip this check (allow any value in data)
        if plan_conv_length != 'none':
            # Exact match first
            if conv_length == plan_conv_length:
                pass
            # Handle variations: "60" vs "60 (minimum 30)"
            elif '60' in conv_length and '60' in plan_conv_length:
                pass
            # Handle "30" appearing in longer string  
            elif conv_length == '30' and plan_conv_length == '30':
                pass
            else:
                continue
        
        # 8. Match discussion_order
        # In data: 'fix', 'random', 'raise', or may have value when plan is empty
        # In plan: 'fix', 'random', 'raise', or empty
        plan_disc_order = plan_row.get('discussion_order_plan_normalized', 'none')
        
        # If plan has empty/none discussion order, skip this check (allow any value in data)
        if plan_disc_order != 'none':
            if disc_order != plan_disc_order:
                continue
        
        # If all criteria match, return the condition number
        return int(plan_row['condition_number'])
    
    # No match found
    return None


def add_condition_columns(data: pd.DataFrame, study_plan: pd.DataFrame) -> pd.DataFrame:
    """
    Add condition number and study plan variables to the data.
    Uses filename parsing as a fallback when data columns have NaN values.
    """
    print(f"\n🔍 Matching data rows to conditions...")
    
    # Create a copy to avoid modifying original
    enriched_data = data.copy()
    
    # Initialize new columns
    enriched_data['condition_number'] = None
    enriched_data['data_type'] = None  # 'human', 'baseline', or 'experiment'
    
    # Match each row
    matched_count = 0
    filename_fallback_count = 0
    human_data_count = 0
    unmatched_rows = []
    
    for idx, row in enriched_data.iterrows():
        # Check if this is human data - if so, skip matching entirely
        source = row.get('source', '')
        if source == 'human_data':
            # Set condition_number to NaN for human data
            enriched_data.at[idx, 'condition_number'] = None
            enriched_data.at[idx, 'data_type'] = 'human'
            human_data_count += 1
            continue
        
        # Check if number_of_agents == 1 (single-agent baseline)
        # Single-agent baselines don't go through multi-agent discussion code
        # They are NOT part of the experimental conditions, treat like human data
        num_agents = row.get('number_of_agents', None)
        if pd.notna(num_agents) and str(num_agents) == '1':
            # Single agent baselines are not matched to conditions
            enriched_data.at[idx, 'condition_number'] = None
            enriched_data.at[idx, 'data_type'] = 'baseline'
            human_data_count += 1
            continue
        
        # Normal matching for multi-agent conditions
        condition_num = match_condition(row, study_plan)
        
        if condition_num is not None:
            enriched_data.at[idx, 'condition_number'] = condition_num
            enriched_data.at[idx, 'data_type'] = 'experiment'
            matched_count += 1
        else:
            # Try filename parsing as fallback
            file_id = row.get('file_id', '')
            if file_id and pd.notna(file_id) and '_' in str(file_id):
                # Parse filename to get config
                filename_config = parse_filename_to_config(str(file_id))
                if filename_config:
                    # Map to study1 format
                    filename_study1 = map_filename_config_to_study1(filename_config)
                    
                    # Create a mock row with filename-parsed data
                    mock_row = pd.Series(filename_study1)
                    
                    # Try matching with this row
                    condition_num = match_condition(mock_row, study_plan)
                    
                    if condition_num is not None:
                        enriched_data.at[idx, 'condition_number'] = condition_num
                        enriched_data.at[idx, 'data_type'] = 'experiment'
                        matched_count += 1
                        filename_fallback_count += 1
                    else:
                        enriched_data.at[idx, 'data_type'] = 'experiment'  # Still experimental, just unmatched
                        unmatched_rows.append(idx)
                else:
                    enriched_data.at[idx, 'data_type'] = 'experiment'  # Still experimental, just unmatched
                    unmatched_rows.append(idx)
            else:
                enriched_data.at[idx, 'data_type'] = 'experiment'  # Still experimental, just unmatched
                unmatched_rows.append(idx)
    
    print(f"   ✅ Matched {matched_count}/{len(enriched_data)} rows")
    print(f"   👤 Skipped {human_data_count} baseline/non-experimental rows (human data + single-agent)")
    if filename_fallback_count > 0:
        print(f"   📄 Matched {filename_fallback_count} rows using filename parsing")
    
    actual_unmatched = len(unmatched_rows)
    if actual_unmatched > 0:
        print(f"   ⚠️  {actual_unmatched} experimental rows could not be matched:")
        
        # Group unmatched rows by source to identify patterns
        unmatched_sources = {}
        for idx in unmatched_rows:
            source = enriched_data.iloc[idx].get('source', 'unknown')
            if source not in unmatched_sources:
                unmatched_sources[source] = []
            unmatched_sources[source].append(idx)
        
        print(f"\n   Unmatched rows by source:")
        for source, indices in sorted(unmatched_sources.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"      {source}: {len(indices)} rows")
        
        print(f"\n   Sample unmatched rows (first 20 for debugging):")
        for i, idx in enumerate(unmatched_rows[:20], 1):  # Show first 20
            row = enriched_data.iloc[idx]
            print(f"      [{i}] Row {idx}:")
            print(f"          agents={row.get('number_of_agents')}, "
                  f"persona={row.get('persona')}, "
                  f"idea_gen={row.get('idea_generation')}")
            print(f"          discussion={row.get('discussion')}, "
                  f"pool={row.get('replacement_pool')}, "
                  f"add_idea={row.get('additional_idea_generation')}")
            print(f"          length={row.get('conversation_length')}, "
                  f"order={row.get('discussion_order')}")
            file_id = row.get('file_id', 'N/A')
            if pd.notna(file_id):
                print(f"          file_id={file_id}")
            else:
                print(f"          file_id=N/A")
            print()
        if len(unmatched_rows) > 20:
            print(f"      ... and {len(unmatched_rows) - 20} more unmatched rows")
    
    # Merge study plan variables for matched rows
    print(f"\n📎 Adding study plan variables...")
    
    # Create a mapping dictionary from condition_number to study plan variables
    study_plan_dict = study_plan.set_index('condition_number').to_dict('index')
    
    # Add study plan columns (without the _normalized suffix)
    plan_columns = [col for col in study_plan.columns 
                   if col != 'condition_number' and not col.endswith('_normalized')]
    
    for col in plan_columns:
        enriched_data[col] = enriched_data['condition_number'].apply(
            lambda cond: study_plan_dict.get(cond, {}).get(col, None) if pd.notna(cond) else None
        )
    
    print(f"   ✅ Added {len(plan_columns)} study plan variables")
    
    # Reorder columns: put condition_number and study plan variables near the front
    cols = list(enriched_data.columns)
    condition_cols = ['condition_number', 'data_type'] + plan_columns
    other_cols = [c for c in cols if c not in condition_cols]
    enriched_data = enriched_data[condition_cols + other_cols]
    
    return enriched_data, human_data_count


def generate_summary_report(enriched_data: pd.DataFrame, baseline_count: int = 0) -> str:
    """
    Generate a summary report of the matching results.
    Excludes baseline/non-experimental rows from unmatched count.
    """
    report = []
    report.append("\n" + "="*80)
    report.append("CONDITION MATCHING SUMMARY REPORT")
    report.append("="*80)
    
    total_rows = len(enriched_data)
    matched_rows = enriched_data['condition_number'].notna().sum()
    unmatched_rows = total_rows - matched_rows - baseline_count
    
    report.append(f"\nTotal data rows: {total_rows}")
    report.append(f"Matched to conditions: {matched_rows} ({matched_rows/total_rows*100:.1f}%)")
    report.append(f"Baseline/non-experimental: {baseline_count} ({baseline_count/total_rows*100:.1f}%)")
    report.append(f"Failed to match: {unmatched_rows} ({unmatched_rows/total_rows*100:.1f}%)")
    
    # Calculate matching rate for matchable rows only
    matchable_rows = total_rows - baseline_count
    if matchable_rows > 0:
        report.append(f"\n{'Matching Success Rate:':-^80}")
        report.append(f"Matchable experimental rows: {matchable_rows}")
        report.append(f"Successfully matched: {matched_rows} ({matched_rows/matchable_rows*100:.1f}%)")
        report.append(f"Failed to match: {unmatched_rows} ({unmatched_rows/matchable_rows*100:.1f}%)")
    
    if matched_rows > 0:
        report.append(f"\n{'Condition Distribution:':-^80}")
        condition_counts = enriched_data['condition_number'].value_counts().sort_index()
        report.append(f"\n{'Condition':<12} {'Count':<10} {'Percentage'}")
        report.append("-" * 40)
        for cond, count in condition_counts.items():
            if pd.notna(cond):
                pct = count / matched_rows * 100
                report.append(f"{int(cond):<12} {count:<10} {pct:>6.1f}%")
    
    report.append("\n" + "="*80)
    
    return "\n".join(report)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_study_plan = os.path.join(script_dir, 'resources', 'study_plan_conditions.csv')

    parser = argparse.ArgumentParser(
        description='Match experimental conditions from study plan to actual data'
    )
    parser.add_argument(
        '--study-plan',
        type=str,
        default=default_study_plan,
        help='Path to the study plan CSV file'
    )
    parser.add_argument(
        '--data',
        type=str,
        required=True,
        help='Path to the rated final-idea CSV file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='processed/final_idea_with_conditions_matched.csv',
        help='Path for the output enriched CSV file'
    )
    parser.add_argument(
        '--report',
        type=str,
        default='processed/condition_matching_report.txt',
        help='Path for the summary report file'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("CONDITION MATCHING SCRIPT")
    print("="*80)
    
    def resolve_path(path):
        return path if os.path.isabs(path) else os.path.abspath(path)

    study_plan_path = resolve_path(args.study_plan)
    data_path = resolve_path(args.data)
    output_path = resolve_path(args.output)
    report_path = resolve_path(args.report)
    
    # Load files
    study_plan = load_study_plan(study_plan_path)
    data = load_data(data_path)
    
    # Match conditions
    enriched_data, baseline_count = add_condition_columns(data, study_plan)
    
    # Generate summary report
    report = generate_summary_report(enriched_data, baseline_count)
    print(report)
    
    # Save outputs
    print(f"\n💾 Saving enriched data to: {output_path}")
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    enriched_data.to_csv(output_path, index=False)
    print(f"   ✅ Saved {len(enriched_data)} rows")
    
    print(f"\n💾 Saving summary report to: {report_path}")
    report_dir = os.path.dirname(report_path)
    if report_dir:
        os.makedirs(report_dir, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"   ✅ Report saved")
    
    print("\n" + "="*80)
    print("✅ MATCHING COMPLETE!")
    print("="*80)
    print(f"\nOutput files:")
    print(f"  📊 Data: {output_path}")
    print(f"  📄 Report: {report_path}")
    print("\nYou can now use the enriched dataset for regression analysis!")
    

if __name__ == '__main__':
    main()
