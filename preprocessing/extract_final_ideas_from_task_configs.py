#!/usr/bin/env python3
# extract_final_ideas_from_task_configs.py - Extract final ideas only from files covered by task configurations
import os
import re
import glob
import pandas as pd
import argparse
import json
from typing import Dict, List, Tuple, Any, Optional

def load_task_configs(config_file: str) -> List[Dict[str, Any]]:
    """Load task configurations from JSON file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            configs = json.load(f)
        print(f"✅ Loaded {len(configs)} task configurations from {config_file}")
        return configs
    except FileNotFoundError:
        print(f"❌ File not found: {config_file}")
        return []
    except Exception as e:
        print(f"❌ Error loading configurations: {e}")
        return []

def sanitize_model_name(model_name):
    """
    Sanitize model name for filename (matches conversation.py logic).
    """
    MODEL_SHORT_NAMES = {
        "gemini-2.0-flash-thinking-exp": "gemini2-flash",
        'gemini-2.5-pro-preview-05-06': "gemini2.5-pro",
        "deepseek-ai/DeepSeek-R1": "deepseek-R1",
        "o1-mini": "o1-mini",
        "o3-mini": "o3-mini",
        'o4-mini': 'o4-mini',
    }

    if isinstance(model_name, list):
        # Handle mixed models
        sanitized_parts = []
        for m in model_name:
            short_name = MODEL_SHORT_NAMES.get(m, m)
            # Basic sanitization for each part
            invalid_chars = r'<>:"/\|?*'
            for char in invalid_chars:
                short_name = short_name.replace(char, "-")
            short_name = short_name.replace("/", "-")
            sanitized_parts.append(short_name)
        model_part = "_".join(sanitized_parts)
    else:
        # Handle single model name
        model_part = MODEL_SHORT_NAMES.get(model_name, model_name)
        # Sanitize the single model name
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            model_part = model_part.replace(char, "-")
        model_part = model_part.replace("/", "-")

    # Final cleanup
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        model_part = model_part.replace(char, "-")

    return model_part

def predict_output_filename(config: Dict[str, Any]) -> Tuple[str, str]:
    """
    Predict what the output filename would be for a given configuration.
    Returns (output_dir, base_filename) tuple.
    """
    # Extract configuration parameters with defaults
    model_name = config.get("model", "unknown_model")
    temperature = config.get("temperature", 1)
    llm_count = config.get("llm_count", "unknown_count")
    persona_type = config.get("persona_type", "unknown_persona")
    phases = config.get("phases", "unknown_phases")
    generation_method = config.get("generation_method", "unknown_gen")
    discussion_method = config.get("discussion_method", "unknown_disc")
    replacement_pool_size = config.get("replacement_pool_size", "unknown_pool")
    discussion_order_method = config.get("discussion_order_method", "unknown_order")
    max_responses = config.get("max_responses", "unknown_max_responses")
    min_responses = config.get("min_responses", None)
    question_id = config.get("question_id", "unknown_question")

    # Sanitize model name
    try:
        model_part = sanitize_model_name(model_name)
    except Exception as e:
        print(f"Warning: sanitize_model_name failed for '{model_name}': {e}")
        model_part = "error_model"

    # Prepare filename components consistently
    temp_str = str(temperature)
    count_str = str(llm_count)
    persona_str = str(persona_type)
    phases_str = str(phases)
    order_str = str(discussion_order_method)
    max_responses_str = str(max_responses)
    min_responses_str = str(min_responses)

    # Handle phase-dependent parts
    if phases == 'direct_discussion':
        gen_method_str = "Direct"
        disc_method_str = str(discussion_method)
        pool_str = f"pool_{replacement_pool_size}"
    elif phases == 'three_stage':
        gen_method_str = str(generation_method)
        disc_method_str = str(discussion_method)
        pool_str = f"pool_{replacement_pool_size}"
    else:
        gen_method_str = str(generation_method)
        disc_method_str = str(discussion_method)
        pool_str = f"pool_{replacement_pool_size}" if replacement_pool_size != "unknown_pool" else "NA"

    # Construct the base filename from components
    filename_parts = [
        model_part,
        temp_str,
        count_str,
        persona_str,
        phases_str,
        gen_method_str,
        disc_method_str,
        order_str,
        pool_str,
        max_responses_str,
        min_responses_str
    ]

    # Join parts and clean up
    base_filename = "_".join(filter(None, filename_parts)) + ".txt"
    base_filename = base_filename.replace("__", "_")

    return question_id, base_filename

def get_files_for_config(results_directory: str, config: Dict[str, Any]) -> List[str]:
    """
    Get list of existing files for a given configuration (including versioned files).
    Limited to exactly 5 files per configuration to avoid processing extras.
    """
    question_id, base_filename = predict_output_filename(config)
    output_dir = os.path.join(results_directory, question_id)
    
    if not os.path.exists(output_dir):
        return []

    # Look for base file and versioned files
    base_path = os.path.join(output_dir, base_filename)
    base_name_no_ext = os.path.splitext(base_filename)[0]
    
    existing_files = []
    
    # Check for base file
    if os.path.exists(base_path):
        existing_files.append(base_path)
    
    # Check for versioned files (_v1.txt, _v2.txt, etc.)
    version = 1
    while len(existing_files) < 5:  # Limit to 5 files max
        versioned_filename = f"{base_name_no_ext}_v{version}.txt"
        versioned_path = os.path.join(output_dir, versioned_filename)
        if os.path.exists(versioned_path):
            existing_files.append(versioned_path)
            version += 1
        else:
            break
    
    # Return only the first 5 files to ensure consistency
    return existing_files[:5]

def parse_config_from_content(content: str) -> Dict[str, Any]:
    """Extract task configuration from file content."""
    config = {}
    
    # Extract configuration section
    config_match = re.search(r'=== Task Configuration ===\s*\{(.*?)\}', content, re.DOTALL)
    if config_match:
        try:
            config_str = "{" + config_match.group(1) + "}"
            config = json.loads(config_str)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse configuration JSON")
    
    return config

def parse_token_usage(content: str) -> Dict[str, Any]:
    """Extract token usage information from file content."""
    token_data = {}
    
    # Extract overall token usage
    overall_match = re.search(r'Overall:\s*Total Prompt Tokens Used: (\d+)\s*Total Completion Tokens Used: (\d+)\s*Total Reasoning Tokens Used: (\d+)\s*Grand Total Tokens Used: (\d+)', content)
    if overall_match:
        token_data.update({
            'total_prompt_tokens': int(overall_match.group(1)),
            'total_completion_tokens': int(overall_match.group(2)),
            'total_reasoning_tokens': int(overall_match.group(3)),
            'grand_total_tokens': int(overall_match.group(4))
        })
    
    # Extract phase-wise token usage
    phases = ['Idea_generation', 'Selection', 'Discussion', 'Single_llm', 'Other']
    for phase in phases:
        phase_pattern = rf'{phase} Phase:\s*Prompt Tokens Used: (\d+)\s*Completion Tokens Used: (\d+)\s*Reasoning Tokens Used: (\d+)\s*Total Tokens Used: (\d+)'
        phase_match = re.search(phase_pattern, content)
        if phase_match:
            token_data.update({
                f'{phase.lower()}_prompt_tokens': int(phase_match.group(1)),
                f'{phase.lower()}_completion_tokens': int(phase_match.group(2)),
                f'{phase.lower()}_reasoning_tokens': int(phase_match.group(3)),
                f'{phase.lower()}_total_tokens': int(phase_match.group(4))
            })
    
    # Extract total rounds
    rounds_match = re.search(r'=== Total Rounds Executed: (\d+) ===', content)
    if rounds_match:
        token_data['total_rounds'] = int(rounds_match.group(1))
    
    return token_data

def extract_total_rounds(content: str) -> Optional[int]:
    """Extract the actual total rounds from discussion content."""
    
    # First try the explicit total rounds statement
    rounds_match = re.search(r'=== Total Rounds Executed: (\d+) ===', content)
    if rounds_match:
        explicit_rounds = int(rounds_match.group(1))
        return explicit_rounds
    
    # If not found, try to count from the Idea Evolution History section
    evolution_section = re.search(r'=== Idea Evolution History ===\s*(.*?)(?:=== Chat History ===|\Z)', content, re.DOTALL)
    if evolution_section:
        evolution_content = evolution_section.group(1)
        # Look for "-- Round X --" patterns in the evolution history
        round_matches = re.findall(r'-- Round (\d+) --', evolution_content)
        if round_matches:
            try:
                max_round = max([int(r) for r in round_matches])
                return max_round
            except ValueError:
                pass
    
    # If still not found, try to count from discussion prompts mentioning "You are on round X"
    discussion_round_matches = re.findall(r'You are on round (\d+)\.', content)
    if discussion_round_matches:
        try:
            max_round = max([int(r) for r in discussion_round_matches])
            return max_round
        except ValueError:
            pass
    
    return None

def extract_question_id_and_run_num(file_path: str) -> Tuple[Optional[str], int]:
    """Extract question_ID from directory structure and run_num from filename."""
    
    # Get the directory name (question_ID)
    dir_name = os.path.basename(os.path.dirname(file_path))
    question_id = dir_name if dir_name and dir_name != '.' else None
    
    # Extract run number from filename
    filename = os.path.basename(file_path)
    
    # Look for version pattern like "_v1.txt", "_v2.txt", etc.
    version_match = re.search(r'_v(\d+)\.txt$', filename)
    if version_match:
        # If version found, run_num = version_num + 1 (since v1 means second run)
        run_num = int(version_match.group(1)) + 1
    else:
        # If no version, this is the first run
        run_num = 1
    
    return question_id, run_num

def clean_idea_text(text: str) -> str:
    """Clean up idea text by removing common prefixes and formatting artifacts."""
    if not text:
        return text
    
    cleaned_text = text.strip()
    
    # Remove dashed lines (common formatting artifact)
    cleaned_text = re.sub(r'^-{50,}$', '', cleaned_text, flags=re.MULTILINE)
    
    # Remove "Response:" headers
    cleaned_text = re.sub(r'^Response:\s*', '', cleaned_text, flags=re.MULTILINE)
    
    # Remove "Final idea (Round X):" pattern
    cleaned_text = re.sub(r'^Final idea \(Round \d+\):\s*', '', cleaned_text, flags=re.IGNORECASE)
    
    # Remove "Replaced: True/False. Final idea for (Round X):" pattern (for iterative condition)
    cleaned_text = re.sub(r'^Replaced:\s*(True|False)\.\s*Final idea for \(Round \d+\):\s*', '', cleaned_text, flags=re.IGNORECASE)
    
    # IMPROVED: Extract content after "Replace:" or "Modify:" if it exists anywhere in the text
    # This handles cases where there's explanatory text before "Replace:" or "Modify:"
    
    # First try **Replace:**
    replace_match = re.search(r'.*?\*\*Replace:\*\*\s*(.*)', cleaned_text, re.DOTALL | re.IGNORECASE)
    if replace_match:
        cleaned_text = replace_match.group(1).strip()
    else:
        # Try **Modify:**
        modify_match = re.search(r'.*?\*\*Modify:\*\*\s*(.*)', cleaned_text, re.DOTALL | re.IGNORECASE)
        if modify_match:
            cleaned_text = modify_match.group(1).strip()
        else:
            # Try without markdown formatting for Replace:
            replace_match = re.search(r'.*?Replace:\s*(.*)', cleaned_text, re.DOTALL | re.IGNORECASE)
            if replace_match:
                cleaned_text = replace_match.group(1).strip()
            else:
                # Try without markdown formatting for Modify:
                modify_match = re.search(r'.*?Modify:\s*(.*)', cleaned_text, re.DOTALL | re.IGNORECASE)
                if modify_match:
                    cleaned_text = modify_match.group(1).strip()
    
    # Remove action labels like "Replace:", "Modify:", etc. at the beginning (for cases not caught above)
    cleaned_text = re.sub(r'^(Replace|Modify|Agree):\s*', '', cleaned_text, flags=re.IGNORECASE)
    
    # Remove "After careful review, I propose a Replace action:" type text
    cleaned_text = re.sub(r'^After careful review,.*?(Replace|Modify):\s*', '', cleaned_text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove "Modify: " with quoted title pattern (e.g., Modify: "Title" -> Title)
    cleaned_text = re.sub(r'^Modify:\s*["\']([^"\']+)["\']', r'\1', cleaned_text, flags=re.IGNORECASE)
    
    # Remove everything after "Reason:" (including the reason section)
    cleaned_text = re.split(r'\*\*Reason:\*\*|\bReason:\s*', cleaned_text, flags=re.IGNORECASE)[0]
    
    # Remove everything after "**Reason" (alternative formatting)
    cleaned_text = re.split(r'\*\*Reason\b', cleaned_text, flags=re.IGNORECASE)[0]
    
    # Remove word count notes
    cleaned_text = re.sub(r'\*\(Word count.*?\)\*', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\(Word count.*?\)', '', cleaned_text, flags=re.IGNORECASE)
    
    # Remove novelty/usefulness/alignment analysis sections
    cleaned_text = re.split(r'\*\*Novelty:\*\*|\*\*Usefulness:\*\*|\*\*Alignment:\*\*', cleaned_text, flags=re.IGNORECASE)[0]
    
    # Remove markdown-style bold formatting from the main idea title
    cleaned_text = re.sub(r'^\*\*(.*?)\*\*\s*', r'\1 ', cleaned_text)
    
    # Clean up extra whitespace and empty lines
    cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)  # Remove empty lines
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize whitespace
    cleaned_text = cleaned_text.strip()
    
    # Final pass: Remove any remaining "Replace:" and "Modify:" patterns at the beginning (after all other cleaning)
    cleaned_text = re.sub(r'^Replace:\s*', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'^\*\*\s*Replace:\s*', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'^Replace\s*:\s*', '', cleaned_text, flags=re.IGNORECASE)  # Handle space before colon
    
    # Remove any remaining "Modify:" patterns
    cleaned_text = re.sub(r'^Modify:\s*', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'^\*\*\s*Modify:\s*', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'^Modify\s*:\s*', '', cleaned_text, flags=re.IGNORECASE)  # Handle space before colon
    
    # IMPROVED: Remove trailing asterisks, dashes, and other formatting artifacts
    # Remove trailing asterisks (**, ***, etc.)
    cleaned_text = re.sub(r'\*+\s*$', '', cleaned_text)
    # Remove trailing dashes (-, --, etc.)
    cleaned_text = re.sub(r'-+\s*$', '', cleaned_text)
    # Remove trailing underscores
    cleaned_text = re.sub(r'_+\s*$', '', cleaned_text)
    # Remove trailing equal signs
    cleaned_text = re.sub(r'=+\s*$', '', cleaned_text)
    # Remove trailing periods followed by spaces
    cleaned_text = re.sub(r'\.\s*$', '.', cleaned_text)
    
    # Final cleanup
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

def map_to_study1_columns(config: Dict[str, Any]) -> Dict[str, Any]:
    """Map configuration to study1_15062025.csv column format."""
    
    # Extract values from config
    llm_count = config.get('llm_count', 1)
    persona_type = config.get('persona_type', 'none')
    phases = config.get('phases', 'three_stage')
    discussion_method = config.get('discussion_method', 'none')
    discussion_order_method = config.get('discussion_order_method', 'fixed')
    replacement_pool_size = config.get('replacement_pool_size', 0)
    max_responses = config.get('max_responses', 60)
    min_responses = config.get('min_responses')
    
    # Map persona_type
    persona_mapping = {
        'none': 'no',
        'same': 'same', 
        'different': 'different'
    }
    persona = persona_mapping.get(persona_type, 'no')
    
    # Map idea generation method
    if phases == 'three_stage':
        if config.get('generation_method') == 'dependent':
            idea_generation = 'interactive'
        else:
            idea_generation = 'nominal'
    elif llm_count == 1:
        idea_generation = 'one idea'
    else:
        idea_generation = ''
    
    # Map discussion method
    discussion_mapping = {
        'none': '',
        'all_at_once': 'instructed',
        'iterative_refinement': 'iterative',
        'creative': '',  # creative goes in additional_idea_generation
        'open': 'open'
    }
    discussion = discussion_mapping.get(discussion_method, '')
    
    # Map replacement pool
    if replacement_pool_size == 0:
        replacement_pool = 'no'
    elif replacement_pool_size == 5:
        replacement_pool = 'top5'
    else:
        replacement_pool = str(replacement_pool_size)
    
    # Map additional idea generation
    additional_idea_generation = ''
    if discussion_method == 'creative':
        additional_idea_generation = 'creative'
    
    # Map conversation length
    conversation_length = str(max_responses)
    if min_responses is not None:
        conversation_length = f"{max_responses} (minimum {min_responses})"
    
    # Map discussion order
    order_mapping = {
        'fixed': 'fix',
        'random': 'random',
        'hand_raising': 'raise'
    }
    discussion_order = order_mapping.get(discussion_order_method, 'fix')
    
    return {
        'number_of_agents': llm_count,
        'persona': persona,
        'idea_generation': idea_generation,
        'discussion': discussion,
        'replacement_pool': replacement_pool,
        'additional_idea_generation': additional_idea_generation,
        'conversation_length': conversation_length,
        'discussion_order': discussion_order
    }

def generate_condition_code(config: Dict[str, Any]) -> str:
    """Generate a compact condition code that captures the experimental setup."""
    # Extract key parameters
    llm_count = config.get('llm_count', 1)
    persona_type = config.get('persona_type', 'none')
    phases = config.get('phases', 'three_stage')
    discussion_method = config.get('discussion_method', 'none')
    discussion_order_method = config.get('discussion_order_method', 'fixed')
    replacement_pool_size = config.get('replacement_pool_size', 0)
    max_responses = config.get('max_responses', 60)
    min_responses = config.get('min_responses')
    
    # Create compact codes for each component
    persona_code = {'none': 'N', 'same': 'S', 'different': 'D'}.get(persona_type, 'N')
    
    phases_code = {
        'three_stage': '3S',
        'direct_discussion': 'DD',
        'single_llm': '1L'
    }.get(phases, '3S')
    
    discussion_code = {
        'none': 'N',
        'all_at_once': 'AO',
        'iterative_refinement': 'IR',
        'creative': 'CR',
        'open': 'OP'
    }.get(discussion_method, 'N')
    
    order_code = {
        'fixed': 'F',
        'random': 'R',
        'hand_raising': 'H'
    }.get(discussion_order_method, 'F')
    
    # Build condition code
    # Format: [agents][persona][phases][discussion][order][pool][responses]
    condition_parts = [
        f"{llm_count}A",  # e.g., "3A" for 3 agents
        persona_code,     # e.g., "D" for different personas
        phases_code,      # e.g., "3S" for three_stage
        discussion_code,  # e.g., "AO" for all_at_once
        order_code,       # e.g., "F" for fixed
        f"P{replacement_pool_size}",  # e.g., "P0" for pool size 0
        f"R{max_responses}"  # e.g., "R60" for 60 max responses
    ]
    
    # Add min_responses if specified
    if min_responses is not None:
        condition_parts.append(f"M{min_responses}")
    
    condition_code = "_".join(condition_parts)
    
    return condition_code

def extract_final_idea(content: str, file_id: str, config: Dict) -> Optional[Dict]:
    """Extract only the final idea from the very end of the log file."""
    
    # Get the last 10000 characters to focus on the end of the file
    content_tail = content[-40000:] if len(content) > 40000 else content
    
    discussion_method = config.get('discussion_method', '')
    
    if discussion_method == 'none':
        # For 'none' discussion method, extract the highest rated idea from the ranking
        ranking_pattern = r'Ranked Ideas:\s*Rank 1: (.*?) \(Avg Score: ([\d.]+)\)'
        ranking_match = re.search(ranking_pattern, content, re.DOTALL)
        
        if ranking_match:
            final_idea = ranking_match.group(1).strip()
            final_idea = clean_idea_text(final_idea)  # Clean the text
            
            return {
                'file': file_id,
                'final_idea': final_idea,
                'final_idea_length': len(final_idea),
                'source': 'ranking'
            }
    
    elif discussion_method == 'all_at_once':
        # For 'all_at_once', check if final response is "Agree"
        # Find the last "Response:" section in the file
        response_pattern = r'Response:\s*(.*?)(?:\*{100,}|\Z)'
        responses = re.findall(response_pattern, content_tail, re.DOTALL)
        
        if responses:
            final_response = responses[-1].strip()
            
            # Special handling for hand-raising mode
            discussion_order_method = config.get('discussion_order_method', '')
            if (discussion_order_method == 'hand_raising' and 
                "Final idea selection from discussion process" in final_response):
                
                # If we have at least 2 responses, look at the previous one
                if len(responses) >= 2:
                    previous_response = responses[-2].strip()
                    
                    # Apply the same logic recursively to the previous response
                    if previous_response.startswith("Agree:") or "No changes needed" in previous_response:
                        # Look for "Current Ideas Under Discussion:" section (try multiple patterns)
                        current_ideas_patterns = [
                            r'\*\*Current Ideas Under Discussion:\*\*\s*\d+\.\s*(.*?)(?=\n\n|\*{100,}|-{50,}|\Z)',
                            r'Current Ideas Under Discussion:\s*\d+\.\s*(.*?)(?=\n\n|\*{100,}|-{50,}|\Z)',
                            r'Current Ideas:\s*\d+\.\s*(.*?)(?=\n\n|\*{100,}|-{50,}|\Z)'
                        ]
                        
                        final_idea = None
                        for pattern in current_ideas_patterns:
                            matches = re.findall(pattern, content_tail, re.DOTALL)
                            if matches:
                                final_idea = matches[-1].strip()
                                break
                        
                        if final_idea:
                            final_idea = clean_idea_text(final_idea)  # Clean the text
                            
                            return {
                                'file': file_id,
                                'final_idea': final_idea,
                                'final_idea_length': len(final_idea),
                                'source': 'current_idea_under_discussion_hand_raising_all_at_once'
                            }
                    else:
                        # If previous response is not "Agree", use it as the final idea
                        final_idea = clean_idea_text(previous_response)  # Clean the text
                        return {
                            'file': file_id,
                            'final_idea': final_idea,
                            'final_idea_length': len(final_idea),
                            'source': 'previous_response_hand_raising_all_at_once'
                        }
            
            # If final response is "Agree: No changes needed." or similar, extract current idea under discussion
            elif final_response.startswith("Agree:") or "No changes needed" in final_response:
                # Look for "Current Ideas Under Discussion:" section (try multiple patterns)
                current_ideas_patterns = [
                    r'\*\*Current Ideas Under Discussion:\*\*\s*\d+\.\s*(.*?)(?=\n\n|\*{100,}|-{50,}|\Z)',
                    r'Current Ideas Under Discussion:\s*\d+\.\s*(.*?)(?=\n\n|\*{100,}|-{50,}|\Z)',
                    r'Current Ideas:\s*\d+\.\s*(.*?)(?=\n\n|\*{100,}|-{50,}|\Z)'
                ]
                
                final_idea = None
                for pattern in current_ideas_patterns:
                    matches = re.findall(pattern, content_tail, re.DOTALL)
                    if matches:
                        final_idea = matches[-1].strip()
                        break
                
                if final_idea:
                    final_idea = clean_idea_text(final_idea)  # Clean the text
                    
                    return {
                        'file': file_id,
                        'final_idea': final_idea,
                        'final_idea_length': len(final_idea),
                        'source': 'current_idea_under_discussion'
                    }
            else:
                # If not "Agree", use the final response as the idea
                final_idea = clean_idea_text(final_response)  # Clean the text
                return {
                    'file': file_id,
                    'final_idea': final_idea,
                    'final_idea_length': len(final_idea),
                    'source': 'final_response'
                }
    
    elif discussion_method == 'open':
        # For 'open' discussion method, find the very last "Response:" and take everything after it
        # Work backwards from the end of the file
        last_response_pos = content.rfind('Response:')
        if last_response_pos != -1:
            # Get everything after "Response:"
            after_response = content[last_response_pos + len('Response:'):].strip()
            
            # Remove asterisks at the end if present
            final_idea = re.sub(r'\*{50,}.*$', '', after_response, flags=re.DOTALL).strip()
            final_idea = clean_idea_text(final_idea)
            
            return {
                'file': file_id,
                'final_idea': final_idea,
                'final_idea_length': len(final_idea),
                'source': 'final_response_open'
            }
    
    # For other discussion methods or fallback cases
    # Find the last "Response:" section in the file (focus on the tail)
    response_pattern = r'Response:\s*(.*?)(?:\*{100,}|\Z)'
    responses = re.findall(response_pattern, content_tail, re.DOTALL)
    
    if not responses:
        return None
    
    # Get the last response
    final_response = responses[-1].strip()
    
    if not final_response:
        return None
    
    # Special handling for hand-raising mode
    discussion_order_method = config.get('discussion_order_method', '')
    if (discussion_order_method == 'hand_raising' and 
        "Final idea selection from discussion process" in final_response):
        
        # If we have at least 2 responses, look at the previous one
        if len(responses) >= 2:
            previous_response = responses[-2].strip()
            
            # Apply the same logic recursively to the previous response
            if previous_response.startswith("Agree:") or "No changes needed" in previous_response:
                # Look for "Current Ideas Under Discussion:" section (try multiple patterns)
                current_ideas_patterns = [
                    r'\*\*Current Ideas Under Discussion:\*\*\s*\d+\.\s*(.*?)(?=\n\n|\*{100,}|-{50,}|\Z)',
                    r'Current Ideas Under Discussion:\s*\d+\.\s*(.*?)(?=\n\n|\*{100,}|-{50,}|\Z)',
                    r'Current Ideas:\s*\d+\.\s*(.*?)(?=\n\n|\*{100,}|-{50,}|\Z)'
                ]
                
                final_idea = None
                for pattern in current_ideas_patterns:
                    matches = re.findall(pattern, content_tail, re.DOTALL)
                    if matches:
                        final_idea = matches[-1].strip()
                        break
                
                if final_idea:
                    final_idea = clean_idea_text(final_idea)  # Clean the text
                    
                    return {
                        'file': file_id,
                        'final_idea': final_idea,
                        'final_idea_length': len(final_idea),
                        'source': 'current_idea_under_discussion_hand_raising'
                    }
            else:
                # If previous response is not "Agree", use it as the final idea
                final_idea = clean_idea_text(previous_response)  # Clean the text
                return {
                    'file': file_id,
                    'final_idea': final_idea,
                    'final_idea_length': len(final_idea),
                    'source': 'previous_response_hand_raising'
                }
    
    # Clean the final response text
    final_response = clean_idea_text(final_response)
    
    # Try to extract agent information from the section before the final response
    # Look for the agent pattern right before the final response (in the tail)
    final_agent_pattern = r'Agent\s+(\d+)\((.*?),\s*(.*?),\s*Idea Index:\s*(.*?),\s*Round:\s*(.*?)\)\s*-+\s*Prompt:.*?Response:\s*' + re.escape(final_response[:100])
    agent_match = re.search(final_agent_pattern, content_tail, re.DOTALL)
    
    agent_info = {}
    if agent_match:
        agent_info = {
            'agent_num': agent_match.group(1).strip(),
            'model': agent_match.group(2).strip(),
            'phase': agent_match.group(3).strip(),
            'idea_index': agent_match.group(4).strip() if agent_match.group(4).strip() != 'N/A' else None,
            'round': agent_match.group(5).strip() if agent_match.group(5).strip() != 'N/A' else None
        }
    
    return {
        'file': file_id,
        'final_idea': final_response,
        'final_idea_length': len(final_response),
        'source': 'final_response',
        **agent_info
    }

def extract_comprehensive_data(file_path: str) -> Dict[str, Any]:
    """Extract comprehensive data from a single file, focusing on final idea only."""
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    file_id = os.path.basename(file_path).replace('.txt', '')
    
    # Get file size in bytes
    file_size_bytes = os.path.getsize(file_path)
    
    # Parse configuration
    config = parse_config_from_content(content)
    
    # Parse token usage
    token_data = parse_token_usage(content)
    
    # Extract actual total rounds
    actual_total_rounds = extract_total_rounds(content)
    if actual_total_rounds is not None:
        token_data['total_rounds'] = actual_total_rounds
    
    # Extract question_ID and run_num from file path
    question_id_from_path, run_num = extract_question_id_and_run_num(file_path)
    
    # Use question_ID from config if available, otherwise from path
    question_id = config.get('question_id') or question_id_from_path
    
    # Generate condition code
    condition_code = generate_condition_code(config)
    
    # Map to study1 columns
    study1_mapping = map_to_study1_columns(config)
    
    # Extract only the final idea
    final_idea_data = extract_final_idea(content, file_id, config)
    
    return {
        'file_id': file_id,
        'file_path': file_path,
        'file_size_bytes': file_size_bytes,
        'question_id': question_id,
        'run_num': run_num,
        'condition_code': condition_code,
        'study1_mapping': study1_mapping,
        'config': config,
        'token_data': token_data,
        'final_idea_data': final_idea_data
    }

def create_final_ideas_dataframe(all_data: List[Dict]) -> pd.DataFrame:
    """Create a dataframe with final ideas and configuration information."""
    rows = []
    
    for idx, data in enumerate(all_data):
        file_id = data['file_id']
        config = data['config']
        token_data = data['token_data']
        final_idea_data = data['final_idea_data']
        question_id = data['question_id']
        run_num = data['run_num']
        condition_code = data['condition_code']
        study1_mapping = data['study1_mapping']
        file_size_bytes = data['file_size_bytes']
        
        # Create base row with config and token data
        row = {
            'ID': idx + 1,  # Unique ID starting from 1
            'file_id': file_id,
            'file_size_bytes': file_size_bytes,  # Added file size column
            'question_ID': question_id,  # Added question_ID column
            'run_num': run_num,          # Added run_num column
            'condition_code': condition_code,  # Added condition_code column
            
            # Study1 columns (matching study1_15062025.csv format)
            'number_of_agents': study1_mapping['number_of_agents'],
            'persona': study1_mapping['persona'],
            'idea_generation': study1_mapping['idea_generation'],
            'discussion': study1_mapping['discussion'],
            'replacement_pool': study1_mapping['replacement_pool'],
            'additional_idea_generation': study1_mapping['additional_idea_generation'],
            'conversation_length': study1_mapping['conversation_length'],
            'discussion_order': study1_mapping['discussion_order'],
            # Configuration fields
            'task_type': config.get('task_type'),
            'phases': config.get('phases'),
            'generation_method': config.get('generation_method'),
            'selection_method': config.get('selection_method'),
            'discussion_method': config.get('discussion_method'),
            'discussion_order_method': config.get('discussion_order_method'),
            'persona_type': config.get('persona_type'),
            'llm_count': config.get('llm_count'),
            'models': ', '.join(config.get('model', [])) if isinstance(config.get('model'), list) else config.get('model'),
            'temperature': config.get('temperature'),
            'replacement_pool_size': config.get('replacement_pool_size'),
            'role_assignment': '|'.join(config.get('role_assignment_in_user_prompt', [])) if config.get('role_assignment_in_user_prompt') else None,
            'max_responses': config.get('max_responses'),
            'min_responses': config.get('min_responses'),
            'reasoning_efforts': '|'.join([str(x) if x is not None else 'None' for x in config.get('reasoning_efforts', [])]) if config.get('reasoning_efforts') else None,
            'question_id': config.get('question_id'),  # Keep original for backward compatibility
            
            # Token usage fields
            'total_prompt_tokens': token_data.get('total_prompt_tokens'),
            'total_completion_tokens': token_data.get('total_completion_tokens'),
            'total_reasoning_tokens': token_data.get('total_reasoning_tokens'),
            'grand_total_tokens': token_data.get('grand_total_tokens'),
            'total_rounds': token_data.get('total_rounds'),
            
            # Phase-wise token usage
            'idea_generation_prompt_tokens': token_data.get('idea_generation_prompt_tokens'),
            'idea_generation_completion_tokens': token_data.get('idea_generation_completion_tokens'),
            'idea_generation_reasoning_tokens': token_data.get('idea_generation_reasoning_tokens'),
            'idea_generation_total_tokens': token_data.get('idea_generation_total_tokens'),
            
            'selection_prompt_tokens': token_data.get('selection_prompt_tokens'),
            'selection_completion_tokens': token_data.get('selection_completion_tokens'),
            'selection_reasoning_tokens': token_data.get('selection_reasoning_tokens'),
            'selection_total_tokens': token_data.get('selection_total_tokens'),
            
            'discussion_prompt_tokens': token_data.get('discussion_prompt_tokens'),
            'discussion_completion_tokens': token_data.get('discussion_completion_tokens'),
            'discussion_reasoning_tokens': token_data.get('discussion_reasoning_tokens'),
            'discussion_total_tokens': token_data.get('discussion_total_tokens'),
            
            'single_llm_prompt_tokens': token_data.get('single_llm_prompt_tokens'),
            'single_llm_completion_tokens': token_data.get('single_llm_completion_tokens'),
            'single_llm_reasoning_tokens': token_data.get('single_llm_reasoning_tokens'),
            'single_llm_total_tokens': token_data.get('single_llm_total_tokens'),
            
            'other_prompt_tokens': token_data.get('other_prompt_tokens'),
            'other_completion_tokens': token_data.get('other_completion_tokens'),
            'other_reasoning_tokens': token_data.get('other_reasoning_tokens'),
            'other_total_tokens': token_data.get('other_total_tokens'),
        }
        
        # Add final idea information
        if final_idea_data:
            row.update({
                'final_idea': final_idea_data['final_idea'],
                'final_idea_length': final_idea_data['final_idea_length'],
                'final_agent_num': final_idea_data.get('agent_num'),
                'final_agent_model': final_idea_data.get('model'),
                'final_agent_phase': final_idea_data.get('phase'),
                'final_idea_index': final_idea_data.get('idea_index'),
                'final_round': final_idea_data.get('round'),
                'source': final_idea_data['source'],
            })
        else:
            row.update({
                'final_idea': None,
                'final_idea_length': 0,
                'final_agent_num': None,
                'final_agent_model': None,
                'final_agent_phase': None,
                'final_idea_index': None,
                'final_round': None,
                'source': None,
            })
        
        rows.append(row)
    
    return pd.DataFrame(rows)

def process_files_from_task_configs(results_directory: str, task_configs: List[Dict[str, Any]]) -> pd.DataFrame:
    """Process files based on task configurations and return final ideas dataframe."""
    all_data = []
    processed_files = set()  # Track processed files to avoid duplicates
    
    print(f"Processing files from {len(task_configs)} task configurations...")
    
    for i, config in enumerate(task_configs):
        try:
            # Get files for this configuration
            files_for_config = get_files_for_config(results_directory, config)
            
            for file_path in files_for_config:
                # Skip if already processed (in case multiple configs map to same file)
                if file_path in processed_files:
                    continue
                
                processed_files.add(file_path)
                
                print(f"Processing: {file_path}")
                data = extract_comprehensive_data(file_path)
                all_data.append(data)
                
                # Show relative path for better readability
                rel_path = os.path.relpath(file_path, results_directory)
                print(f"✓ Processed: {rel_path}")
                
        except Exception as e:
            print(f"✗ Error processing config {i}: {e}")
            continue
        
        # Progress indicator
        if (i + 1) % 50 == 0 or (i + 1) == len(task_configs):
            print(f"  Processed {i + 1}/{len(task_configs)} configurations...")
    
    print(f"\nTotal files processed: {len(all_data)}")
    
    # Create dataframe
    final_ideas_df = create_final_ideas_dataframe(all_data)
    
    return final_ideas_df

def main():
    parser = argparse.ArgumentParser(description='Extract final ideas from files covered by task configurations')
    parser.add_argument('results_directory', help='Directory containing result files')
    parser.add_argument(
        '--task-configs',
        default=os.path.join(os.path.dirname(__file__), 'resources', 'unique_task_configs.json'),
        help='JSON file containing task configurations to extract'
    )
    parser.add_argument('--output-prefix', default='final_ideas_from_configs', help='Prefix for output files')
    parser.add_argument('--format', choices=['csv', 'excel'], default='csv', help='Output format')
    
    args = parser.parse_args()
    
    print("Starting final idea extraction from task configurations...")
    print(f"Task configs file: {args.task_configs}")
    print(f"Results directory: {args.results_directory}")
    
    # Load task configurations
    task_configs = load_task_configs(args.task_configs)
    if not task_configs:
        print("❌ No task configurations loaded. Exiting.")
        return
    
    # Process files based on task configurations
    final_ideas_df = process_files_from_task_configs(args.results_directory, task_configs)
    
    # Save results
    if args.format == 'csv':
        output_file = os.path.join(args.results_directory, f"{args.output_prefix}.csv")
        final_ideas_df.to_csv(output_file, index=False)
        print(f"\n✓ Final ideas saved to: {output_file}")
        
    else:  # excel
        output_file = os.path.join(args.results_directory, f"{args.output_prefix}.xlsx")
        final_ideas_df.to_excel(output_file, index=False)
        print(f"\n✓ Final ideas saved to: {output_file}")
    
    print(f"\nSummary:")
    print(f"- Processed {len(final_ideas_df)} files from task configurations")
    print(f"- Extracted {len(final_ideas_df[final_ideas_df['final_idea'].notna()])} final ideas")
    
    # Show some statistics
    if len(final_ideas_df) > 0:
        avg_length = final_ideas_df['final_idea_length'].mean()
        print(f"- Average final idea length: {avg_length:.1f} characters")
        
        # Show distribution by question_ID
        if 'question_ID' in final_ideas_df.columns:
            question_counts = final_ideas_df['question_ID'].value_counts()
            print(f"- Distribution by question_ID:")
            for question, count in question_counts.items():
                print(f"  {question}: {count}")
        
        # Show distribution by discussion method
        if 'discussion_method' in final_ideas_df.columns:
            method_counts = final_ideas_df['discussion_method'].value_counts()
            print(f"- Distribution by discussion method:")
            for method, count in method_counts.items():
                print(f"  {method}: {count}")
        
        # Show distribution by run number
        if 'run_num' in final_ideas_df.columns:
            run_counts = final_ideas_df['run_num'].value_counts().sort_index()
            print(f"- Distribution by run number:")
            for run_num, count in run_counts.items():
                print(f"  Run {run_num}: {count}")
        
        # Show distribution by condition code (top 10)
        if 'condition_code' in final_ideas_df.columns:
            condition_counts = final_ideas_df['condition_code'].value_counts().head(10)
            print(f"- Top 10 condition codes:")
            for condition, count in condition_counts.items():
                print(f"  {condition}: {count}")

if __name__ == "__main__":
    main() 
