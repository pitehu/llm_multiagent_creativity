# conversation.py
import logging
import datetime
import json
import os

class Conversation:
    def __init__(self, agents, data_strategy, task_config):
        self.agents = agents
        self.data_strategy = data_strategy
        self.task_config = task_config
        self.chat_history = []
        self.current_agent = None

        # Initialize token usage tracking
        self.token_usage = {
            "prompt_tokens_used": 0,
            "completion_tokens_used": 0,
            "reasoning_tokens_used":0,
            "total_tokens_used": 0
        }
        self.phase_token_usage = {
            "idea_generation": {"prompt_tokens_used": 0, "completion_tokens_used": 0, "reasoning_tokens_used":0, "total_tokens_used": 0},
            "selection": {"prompt_tokens_used": 0, "completion_tokens_used": 0, "reasoning_tokens_used":0, "total_tokens_used": 0},
            "discussion": {"prompt_tokens_used": 0, "completion_tokens_used": 0, "reasoning_tokens_used":0, "total_tokens_used": 0},
            "single_llm": {"prompt_tokens_used": 0, "completion_tokens_used": 0, "reasoning_tokens_used":0, "total_tokens_used": 0},
            "other": {"prompt_tokens_used": 0, "completion_tokens_used": 0, "reasoning_tokens_used":0, "total_tokens_used": 0},
        }
    
    def update_phase_token_usage(self, phase, prompt_tokens, completion_tokens,reasoning_tokens):
        """
        Update the token usage for a specific phase.
        """
        if phase not in self.phase_token_usage:
            logging.warning(f"Unknown phase: {phase}. Skipping phase token update.")
            phase = "other"  # Default to "other" phase if phase is unknown

        # Update phase-specific statistics
        self.phase_token_usage[phase]["prompt_tokens_used"] += prompt_tokens
        self.phase_token_usage[phase]["completion_tokens_used"] += completion_tokens
        self.phase_token_usage[phase]["reasoning_tokens_used"] += reasoning_tokens
        self.phase_token_usage[phase]["total_tokens_used"] += (prompt_tokens + completion_tokens + reasoning_tokens)

        # Also update overall token usage
        self.token_usage["prompt_tokens_used"] += prompt_tokens
        self.token_usage["completion_tokens_used"] += completion_tokens
        self.token_usage["reasoning_tokens_used"] += reasoning_tokens
        self.token_usage["total_tokens_used"] += (prompt_tokens + completion_tokens + reasoning_tokens)

    def get_token_summary(self):
        """
        Return a formatted summary of token usage, broken down by phases.
        """
        summary = []
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_reasoning_tokens = 0

        # Iterate over phases and calculate their contributions
        for phase, usage in self.phase_token_usage.items():
            phase_prompt = usage.get("prompt_tokens_used", 0)
            phase_reasoning = usage.get("reasoning_tokens_used", 0)
            phase_completion = usage.get("completion_tokens_used", 0)
            phase_total = phase_prompt + phase_completion + phase_reasoning
            total_prompt_tokens += phase_prompt
            total_reasoning_tokens += phase_reasoning
            total_completion_tokens += phase_completion

            summary.append(
                f"{phase.capitalize()} Phase:\n"
                f"  Prompt Tokens Used: {phase_prompt}\n"
                f"  Completion Tokens Used: {phase_completion}\n"
                f"  Reasoning Tokens Used: {phase_reasoning}\n"
                f"  Total Tokens Used: {phase_total}\n"
            )

        # Add overall total
        summary.append(
            f"Overall:\n"
            f"  Total Prompt Tokens Used: {total_prompt_tokens}\n"
            f"  Total Completion Tokens Used: {total_completion_tokens}\n"
            f"  Total Reasoning Tokens Used: {total_reasoning_tokens}\n"
            f"  Grand Total Tokens Used: {total_prompt_tokens + total_reasoning_tokens + total_completion_tokens}\n"
        )

        return "\n".join(summary)
    
    def get_phase_token_summary(self):
        """
        Return a summary of token usage for each phase.
        """
        summary = "=== Phase-wise Token Usage Summary ===\n"
        for phase, usage in self.phase_token_usage.items():
            summary += (
                f"{phase.capitalize()} Phase:\n"
                f"  Prompt Tokens Used: {usage['prompt_tokens_used']}\n"
                f"  Completion Tokens Used: {usage['completion_tokens_used']}\n"
                f"  Reasoning Tokens Used: {usage['reasoning_tokens_used']}\n"
                f"  Total Tokens Used: {usage['total_tokens_used']}\n"
            )
        return summary

    def get_previous_responses(self, idea_index=None, current_phase=None, history_depth=None):
        previous_responses = []
        n_minus_n_ideas = None

        # Include entries that match the given current_phase, including "open_discussion".
        filtered_history = [entry for entry in self.chat_history if not current_phase or entry["phase"] == current_phase]
        filtered_history = [entry for entry in filtered_history if entry["agent"] != 'initial idea']

        chat_length = len(filtered_history)
        llm_count = self.task_config.get("llm_count", "none")
        if history_depth is None:
        # Step 2 & 3: If not provided, use len(self.agent) as the default
            history_depth = len(self.agents)

        # Update condition to include open_discussion.
        if current_phase in ["discussion", "direct_discussion", "open_discussion"]:
            # Extract ideas with different conditions for discussion/direct_discussion/open_discussion
            if history_depth==-1:
                target_index = 0  # Get from the very beginning

            else: 
                # Only perform calculations if history_depth is an integer
                if not isinstance(history_depth, int) or history_depth < 0:
                     # Handle invalid integer history_depth, maybe default or raise error
                     print(f"Warning: Invalid history_depth '{history_depth}', defaulting to 0.")
                     target_index = 0 # Or consider setting to chat_length to get no initial ideas?
                elif current_phase == "direct_discussion":
                    # Use max to ensure index isn't negative
                    target_index = max(0, chat_length - history_depth) # Simpler logic
                elif current_phase in ["discussion", "open_discussion"]:
                     # Use max to ensure index isn't negative
                    target_index = max(0, chat_length - history_depth) # Simpler logic

            # Now target_index is calculated safely before this check
            if 0 <= target_index < chat_length:
                 # Check if the entry actually exists and has 'current_ideas'
                 entry_at_target = filtered_history[target_index]
                 if entry_at_target:
                     n_minus_n_ideas = entry_at_target.get("current_ideas", []) # Use .get for safety
        if current_phase == "direct_discussion":
            history_to_use = filtered_history[1:] if chat_length > 1 else []
        else:
            history_to_use = filtered_history

        for i, entry in enumerate(reversed(history_to_use)):
            phase = entry["phase"]

            # Update to include open_discussion entries.
            if phase in ["discussion", "direct_discussion", "open_discussion"]:
                if idea_index is not None:
                    if entry.get("idea_index") == idea_index:
                        previous_responses.append(f"\n{entry['agent']} said: {entry['response']}")
                else:
                    previous_responses.append(f"\n{entry['agent']} said: {entry['response']}")
            elif phase == "idea_generation":
                previous_responses.append(f"\n{entry['agent']} said: {entry['response']}")

            # Use number of agents instead of hardcoded 3
            agent_count = len(self.agents)
            if history_depth != -1:
                if len(previous_responses) == agent_count and not (current_phase == "idea_generation" and llm_count == 6):
                     break

        previous_responses = list(reversed(previous_responses))  # Reverse to maintain chronological order

        if current_phase in ["discussion", "direct_discussion"] and n_minus_n_ideas:
            current_ideas_str = "\n".join(f"{i+1}. {idea}" for i, idea in enumerate(n_minus_n_ideas))
            previous_responses.insert(0, f"The initial ideas under discussion before team feedback:\n{current_ideas_str if current_ideas_str else '(none)'}")

        return previous_responses

    def add_chat_entry(self, model_name, agent_name, prompt, response, phase, **kwargs):
        """
        Add a chat entry and update token usage.
        """
        try:
            entry = {
                'agent': agent_name,
                'agent_model':model_name,
                'prompt': prompt,
                'response': response,
                'phase': phase,
                'idea_index': kwargs.get('idea_index', "N/A"),
            }

            # Update condition to include open_discussion
            if 'current_ideas' in kwargs:
                entry['current_ideas'] = list(kwargs['current_ideas'])  # Store a copy of the current_ideas list
            
            if 'round_number' in kwargs:
                entry['round'] = kwargs['round_number']  # add round number
            
            self.chat_history.append(entry)

            # Update phase and overall token usage
            # self.update_phase_token_usage(phase, kwargs.get('prompt_tokens', 0), kwargs.get('completion_tokens', 0), kwargs.get('reasoning_tokens', 0))

            log_message = f"[{phase}] {agent_name} ({model_name}):"
            log_message += f"\nPrompt: {prompt}"
            log_message += f"\nResponse: {response}"
            logging.info(log_message)

        except Exception as e:
            logging.error("Failed to add chat entry: %s", e)
            raise

    # Define a mapping for short names

    def sanitize_model_name(self, model_name):
        """
        Convert model names into a shorter, valid filename format.
        Handles single strings or lists of strings.
        Replaces invalid filename characters and specific patterns like '/'.
        """
        MODEL_SHORT_NAMES = {
            "gemini-2.0-flash-thinking-exp": "gemini2-flash",
            'gemini-2.5-pro-preview-05-06': "gemini2.5-pro",
            "deepseek-ai/DeepSeek-R1": "deepseek-R1",
            # Add other short names as needed
            "o1-mini": "o1-mini",
            "o3-mini": "o3-mini",
            'o4-mini': 'o4-mini',
        }

        # Ensure model_name is processed correctly whether it's a string or list
        if isinstance(model_name, list):
            # Sanitize each part and get short name if available
            sanitized_parts = []
            for m in model_name:
                short_name = MODEL_SHORT_NAMES.get(m, m)
                # Basic sanitization for each part before joining
                invalid_chars = r'<>:"/\|?*'
                for char in invalid_chars:
                    short_name = short_name.replace(char, "-")
                short_name = short_name.replace("/", "-") # Ensure slashes are replaced
                sanitized_parts.append(short_name)
            model_part = "_".join(sanitized_parts)
        else:
            # Handle single string model name
            model_part = MODEL_SHORT_NAMES.get(model_name, model_name)
            # Sanitize the single model name
            invalid_chars = r'<>:"/\|?*'
            for char in invalid_chars:
                model_part = model_part.replace(char, "-")
            model_part = model_part.replace("/", "-") # Ensure slashes are replaced

        # Final check for any remaining invalid chars (redundant but safe)
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            model_part = model_part.replace(char, "-")

        # Optional: Limit length if needed
        # max_len = 50
        # model_part = model_part[:max_len]

        return model_part

    def extract_idea_evolution(self):
        """
        Extract the history of how ideas evolved throughout the discussion.
        """
        idea_history = []
        
        # Filter entries with current_ideas
        for entry in self.chat_history:
            # Skip ranking rounds based on a marker in the prompt.
            if "Idea Ranking Task" in entry.get("prompt", ""):
                continue
            if 'current_ideas' in entry and entry['current_ideas']:
                round_info = entry.get('round', 'N/A')
                agent = entry['agent']
                phase = entry['phase']
                idea_index = entry.get('idea_index', 'N/A')
                
                idea_history.append({
                    'round': round_info,
                    'agent': agent,
                    'phase': phase,
                    'idea_index': idea_index,
                    'ideas': list(entry['current_ideas']),
                    'response': entry['response']
                })
        
        return idea_history

    def save_chat_history(self, filename=None):
        """
        Save the chat history and token usage to a file.
        """
        if not filename:
            # --- 1. Get configuration values with safe defaults ---
            model_name = self.task_config.get("model", "unknown_model")
            temperature = self.task_config.get("temperature", "default_temp")
            # Ensure llm_count is fetched correctly (assuming self.agents exists)
            llm_count = len(self.agents) if hasattr(self, 'agents') else self.task_config.get("llm_count", "unknown_count")
            persona_type = self.task_config.get("persona_type", "unknown_persona")
            phases = self.task_config.get("phases", "unknown_phases")
            generation_method = self.task_config.get("generation_method", "unknown_gen")
            discussion_method = self.task_config.get("discussion_method", "unknown_disc")
            replacement_pool_size = self.task_config.get("replacement_pool_size", "unknown_pool")
            discussion_order_method = self.task_config.get("discussion_order_method", "unknown_order")

            # --- 2. Sanitize model name ---
            try:
                # Use the improved sanitize_model_name
                model_part = self.sanitize_model_name(model_name)
            except Exception as e:
                logging.error(f"sanitize_model_name failed for '{model_name}': {e}")
                model_part = "error_model" # Use a distinct name for error case

            # --- 3. Prepare filename components consistently ---
            temp_str = str(temperature)
            count_str = str(llm_count)
            persona_str = str(persona_type)
            phases_str = str(phases)
            order_str = str(discussion_order_method)
            max_responses_str = str(self.task_config.get("max_responses", "unknown_max_responses"))
            min_responses_str = str(self.task_config.get("min_responses", None))
            # Use specific values or "NA" for phase-dependent parts
            if phases == 'direct_discussion':
                gen_method_str = "Direct" # Indicates no separate generation phase
                disc_method_str = str(discussion_method)
                pool_str = f"pool_{replacement_pool_size}"
            elif phases == 'three_stage':
                gen_method_str = str(generation_method)
                disc_method_str = str(discussion_method)
                # Format pool size clearly
                pool_str = f"pool_{replacement_pool_size}"
            else:
                # Default handling for other/unknown phases
                gen_method_str = str(generation_method)
                disc_method_str = str(discussion_method)
                 # Assume pool size might be relevant or use "NA"
                pool_str = f"pool_{replacement_pool_size}" if replacement_pool_size != "unknown_pool" else "NA"


            # --- 4. Construct the base filename from components ---
            # Consistent order: model, temp, count, persona, phases, gen_method, disc_method, order, pool
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

            # Join parts with underscore and add extension
            # Filter out any potential empty strings just in case
            base_filename = "_".join(filter(None, filename_parts)) + ".txt"

            # Optional: Further sanitization like removing consecutive underscores or length limiting
            base_filename = base_filename.replace("__", "_") # Clean up potential double underscores if parts were empty/NA

            # Use output_dir if it exists, otherwise save to current directory
            if hasattr(self, 'output_dir') and self.output_dir:
                filename = os.path.join(self.output_dir, base_filename)
            else:
                filename = base_filename
                
            version = 1
            original_filename = filename
            while os.path.exists(filename):
                if hasattr(self, 'output_dir') and self.output_dir:
                    filename = os.path.join(self.output_dir, f"{os.path.splitext(base_filename)[0]}_v{version}.txt")
                else:
                    filename = f"{os.path.splitext(base_filename)[0]}_v{version}.txt"
                version += 1

        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write("=== Task Configuration ===\n")
                file.write(json.dumps(self.task_config, indent=4))
                file.write("\n\n=== Phase-wise Token Usage Summary ===\n")
                file.write(self.get_phase_token_summary())
                file.write("\n\n=== Token Usage Summary ===\n")
                file.write(self.get_token_summary())
                

                # Record the actual rounds that were run
                max_round = 0
                if self.chat_history:
                    # Extract integer round numbers, ignore others ('N/A', None, etc.)
                    int_rounds = [entry['round'] for entry in self.chat_history if isinstance(entry.get('round'), int)]
                    if int_rounds:
                        max_round = max(int_rounds)
                # Write the calculated max round number near the top
                file.write(f"\n\n=== Total Rounds Executed: {max_round} ===\n")


                # Add idea evolution history
                file.write("\n\n=== Idea Evolution History ===\n")
                idea_history = self.extract_idea_evolution()
                task_type = self.task_config.get("task_type", "AUT")
                disc_method = self.task_config.get("discussion_method", "all_at_once")

                if disc_method in ["all_at_once", "iterative_refinement"]:
                    # Group by rounds
                    rounds = {}
                    for entry in idea_history:
                        round_num = entry.get('round', 'N/A')
                        if round_num not in rounds:
                            rounds[round_num] = []
                        rounds[round_num].append(entry)
                    
                    for round_num, entries in sorted(rounds.items(), key=lambda x: (str(x[0]) if x[0] == 'N/A' else int(x[0]))):
                        file.write(f"\n-- Round {round_num} --\n")
                        for entry in entries:
                            file.write(f"Agent: {entry['agent']}\n")
                            file.write("Current Ideas:\n")
                            for i, idea in enumerate(entry['ideas'], 1):
                                file.write(f"{i}. {idea}\n")
                            file.write(f"\n")
                            file.write(f"Response: {entry['response']}\n")
                            file.write("-" * 40 + "\n")
                else:
                    # Group by idea index
                    idea_indices = {}
                    for entry in idea_history:
                        idx = entry.get('idea_index', 'N/A')
                        if idx not in idea_indices:
                            idea_indices[idx] = []
                        idea_indices[idx].append(entry)
                    
                    for idx, entries in sorted(idea_indices.items(), key=lambda x: (str(x[0]) if x[0] == 'N/A' else int(x[0]))):
                        file.write(f"\n-- Idea #{idx} --\n")
                        for entry in entries:
                            file.write(f"Agent: {entry['agent']}\n")
                            file.write("Current Idea:\n")
                            for i, idea in enumerate(entry['ideas'], 1):
                                file.write(f"{i}. {idea}\n")
                            file.write(f"Response: {entry['response']}\n")
                            file.write("-" * 40 + "\n")
                
                file.write("\n\n=== Chat History ===\n")
                for entry in self.chat_history:
                    file.write(f"{entry['agent']}({entry['agent_model']}, {entry['phase']}, Idea Index: {entry.get('idea_index', 'N/A')}, Round: {entry.get('round', 'N/A')})\n")
                    file.write("-" * 80 + "\n")
                    file.write("Prompt:\n")
                    file.write(f"{entry['prompt']}\n")
                    file.write("-" * 80 + "\n")
                    file.write("Response:\n")
                    file.write(f"{entry['response']}\n")
                    file.write("**" * 80 + "\n\n")
            logging.info("Chat history saved to %s", filename)

        except Exception as e:
            logging.error("Failed to save chat history: %s", e)

            # Use output_dir for backup filename too
            if hasattr(self, 'output_dir') and self.output_dir:
                backup_filename = os.path.join(self.output_dir, "chat_backup.txt")
            else:
                backup_filename = "chat_backup.txt"
                
            version = 1
            original_backup = backup_filename
            while os.path.exists(backup_filename):
                if hasattr(self, 'output_dir') and self.output_dir:
                    backup_filename = os.path.join(self.output_dir, f"chat_backup_v{version}.txt")
                else:
                    backup_filename = f"chat_backup_v{version}.txt"
                version += 1

            try:
                with open(backup_filename, "w", encoding="utf-8") as file:
                    file.write("=== Backup Chat History ===\n")
                    file.write(json.dumps(self.task_config, indent=4))
                    file.write("\n\n=== Chat History ===\n")

                    for entry in self.chat_history:
                        file.write(f"{entry['agent']}({entry['agent_model']}, {entry['phase']}, Idea Index: {entry.get('idea_index', 'N/A')}, Round: {entry.get('round', 'N/A')})\n")
                        file.write("-" * 80 + "\n")
                        file.write("Prompt:\n")
                        file.write(f"{entry['prompt']}\n")
                        file.write("-" * 80 + "\n")
                        file.write("Response:\n")
                        file.write(f"{entry['response']}\n")
                        file.write("**" * 80 + "\n\n")

                logging.info(f"Backup chat history saved to: {backup_filename}")

            except Exception as e:
                logging.error(f"Failed to save backup chat history: {e}")
                raise

