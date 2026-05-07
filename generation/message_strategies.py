# message_strategies.py

import re
import logging  # <-- Added for logging
from prompts import TASK_REQUIREMENTS
from utils import calculate_tokens
import textwrap
class GenericMessageStrategy:
    def __init__(self, task_config, data_strategy):
        self.task_config = task_config
        self.data_strategy = data_strategy

    def construct_messages(self, agent, phase, conversation, idea_index=None,total_resp=None,current_round=None, max_rounds=None, include_intention_prompt=False):
        msgs=[]
        single_llm_mode = len(conversation.agents) == 1  # Check for single LLM and no persona
        persona_type =  self.task_config.get("persona_type", "none")
        model = agent.model_name  # Fetch the correct model for each agent
        role = (
            # "developer" if model in ['o3-mini','o1'] else
            "user" if model in self.task_config.get("role_assignment_in_user_prompt", [None]) else
            "system"
        )
        print("Single LLM mode??", single_llm_mode)
        # Add role description unless it's a single LLM mode
        msgs.append({"role": role, "content": f"# **Role**\n{agent.system_message}"})
        # Overall
        if self.task_config.get("task_type","AUT")=="AUT":
            msgs.append({"role":role,"content": f"\n# **Task Requirement**\n{TASK_REQUIREMENTS['AUT_Mode1_Overall'].strip()}"})
        else:
            msgs.append({"role":role,"content": f"\n# **Task Requirement**\n{TASK_REQUIREMENTS['PS_Overall'].strip()}"})

        # Adjust content based on phase and task configuration
        if single_llm_mode:
            self._add_single_llm_instructions(msgs, agent, conversation)
        elif phase=="idea_generation":
            self._add_generation_instructions(msgs, agent, conversation)
        elif phase=="selection":
            self._add_selection_instructions(msgs, agent, conversation)
        elif phase=="selection_novelty":
            self._add_selection_instructions_novelty(msgs, agent, conversation)
        elif phase=="iterative_refinement":
            self._add_iterative_refinement_instructions(msgs, agent, conversation)
        elif phase=="discussion":
            self._add_discussion_instructions(msgs, agent, conversation, idea_index,total_resp=total_resp,current_round=current_round, max_rounds=max_rounds)
            if include_intention_prompt:
                if (self.task_config.get("task_type","AUT")=="AUT" and self.task_config.get("discussion_method","all_at_once")=="one_by_one") or self.task_config.get("task_type","AUT")=="PS":
                    intention_prompt = TASK_REQUIREMENTS["Intention_Prompt_Idea"]
                else:
                    intention_prompt = TASK_REQUIREMENTS["Intention_Prompt_Ideas"]

                msgs.append({"role": "user", "content": "\n\n"+intention_prompt.strip()})
        elif phase == "direct_discussion":
            self._add_direct_discussion_instructions(msgs, agent, conversation, total_resp, current_round)
            if include_intention_prompt:
                intention_prompt = TASK_REQUIREMENTS["Intention_Prompt"]
                msgs.append({"role": "user", "content": "\n\n"+intention_prompt.strip()})
        elif phase == "open_discussion":
            self._add_open_discussion_instructions(msgs, agent, conversation, current_round, max_rounds)
        elif phase=="creative_generation":
            self._add_creative_generation_instructions(msgs, agent, conversation)
        elif phase=="practical_discussion":
            self._add_practical_discussion_instructions(msgs, agent, conversation, idea_index, total_resp=total_resp,current_round=current_round, max_rounds=max_rounds)

        return msgs
    
    def _add_single_llm_instructions(self, msgs, agent, conversation):
        """
        Add instructions specifically tailored for a single LLM scenario.
        """
        # This could be dynamic based on some specific task requirements defined elsewhere or simplified
        msgs.append({"role": "user", "content": (
            "# **Current Task**\n"
            "- Please propose one possible ideas for the problem.\n"
            "- The idea should be around 80-100 words.\n"
            "- Please return only the ideas. Do not include any explanations or use markdown formatting. Do not add numbering to the idea."
        )})

    def _add_generation_instructions(self, msgs, agent, conversation):
        """
        If generation_method=='dependent' & agent != first => show previous ideas, else just ask for new
        """
        gen_method= self.task_config.get("generation_method","independent")
        ttype= self.task_config.get("task_type","AUT")

        # check if we have first_agent
        if not self.data_strategy.first_agent_name:
            self.data_strategy.first_agent_name= agent.name
            is_first= True
        else:
            is_first= (agent.name== self.data_strategy.first_agent_name)

        if ttype=="AUT":
            if gen_method=="independent":
                msgs.append({"role":"user","content": f"# **Current Task**\n{TASK_REQUIREMENTS['AUT_Mode1_IdeaGeneration'].strip()}"})
            else:
                if is_first:
                    msgs.append({"role":"user","content": f"# **Current Task**\n{TASK_REQUIREMENTS['AUT_Mode1_IdeaGeneration'].strip()}"})
                else:
                    msgs.append({"role":"user","content": f"# **Current Task**\n{TASK_REQUIREMENTS['AUT_Mode1_IdeaGeneration_Dependent'].strip()}"})
        else:
            # PS
            if gen_method=="independent":
                msgs.append({"role":"user","content": f"# **Current Task**\n{TASK_REQUIREMENTS['PS_Generation'].strip()}"})
            else:
                if is_first:
                    msgs.append({"role":"user","content": f"# **Current Task**\n{TASK_REQUIREMENTS['PS_Generation'].strip()}"})
                else:
                    msgs.append({"role":"user","content": f"# **Current Task**\n{TASK_REQUIREMENTS['PS_Generation_Dependent'].strip()}"})
        
        if gen_method == "dependent" and not is_first:
            previous_responses = conversation.get_previous_responses(current_phase="idea_generation")
            history_str = "\n".join(previous_responses) if previous_responses else "No previous responses."
            msgs.append({"role": "user", "content": f"# **Previous ideas from other agents**\n{history_str}\n"})

    def _add_selection_instructions(self, msgs, agent, conversation):
        sel_method= self.task_config.get("selection_method","rating")
        ttype= self.task_config.get("task_type","AUT")

        if ttype=="AUT":
            if sel_method=="rating":
                msgs.append({"role":"user","content": f"\n# **Current Task**\n{TASK_REQUIREMENTS['AUT_Mode1_Selection_Rating'].strip()}"})
            else:
                msgs.append({"role":"user","content": f"\n# **Current Task**\n{TASK_REQUIREMENTS['AUT_Mode1_Selection_SelectionTop'].strip()}"})
        else:
            if sel_method=="rating":
                msgs.append({"role":"user","content": f"\n# **Current Task**\n{TASK_REQUIREMENTS['PS_Selection_Rating'].strip()}"})
            else:
                msgs.append({"role":"user","content": f"\n# **Current Task**\n{TASK_REQUIREMENTS['PS_Selection_SelectionTop'].strip()}"})


    def _add_selection_instructions_novelty(self, msgs, agent, conversation):
        sel_method= self.task_config.get("selection_method","rating")
        ttype= self.task_config.get("task_type","AUT")

        if ttype=="AUT":
            if sel_method=="rating":
                pass
            else:
                pass
        else:
            if sel_method=="rating":
                msgs.append({"role":"user","content": f"\n# **Current Task**\n{TASK_REQUIREMENTS['PS_Selection_Rating_Novelty'].strip()}"})
            else:
                pass

    def _add_discussion_instructions(self, msgs, agent, conversation, idea_index, total_resp=None, current_round=None, max_rounds=None):
        """
        Modify discussion phase instructions to integrate previous responses and to 
        structure the message flow according to specified requirements.
        """
        task_type = self.task_config.get("task_type", "AUT")
        disc_method = self.task_config.get("discussion_method", "all_at_once")
        sel_method = self.task_config.get("selection_method", "rating")
        # model = self.task_config.get("model", "gpt-4o")
        model = agent.model_name  # Fetch the correct model for each agent
        print(model)
        role = (
            # "developer" if model in ['o3-mini','o1'] else
            "user" if model in self.task_config.get("role_assignment_in_user_prompt", [None]) else
            "system"
        )

        # Fetch and format previous responses
        previous_responses = conversation.get_previous_responses(idea_index if disc_method == "one_by_one" else None,current_phase="discussion")
        history_str = "\n".join(previous_responses) if previous_responses else "No previous responses."

        # Setup the task-specific prompt
        if task_type == 'AUT':
            if disc_method == "all_at_once":
                if sel_method == "rating":
                    prompt = TASK_REQUIREMENTS["AUT_Mode1_Discussion_Rating_AllAtOnce"]
                    prompt = (
                    prompt.replace("{{total_resp}}", str(total_resp + 1))
                )
                else:
                    prompt = (TASK_REQUIREMENTS["AUT_Mode1_Discussion_SelectionTop_AllAtOnce_FirstAgent"] if agent.name == self.data_strategy.first_agent_name
                            else TASK_REQUIREMENTS["AUT_Mode1_Discussion_SelectionTop_AllAtOnce_OtherAgents"])
                    prompt = (
                    prompt.replace("{{total_resp}}", str(total_resp + 1))
                )
            else:
                prompt_key = "AUT_Mode1_Discussion_Rating_OneByOne" if sel_method == "rating" else "AUT_Mode1_Discussion_SelectionTop_OneByOne"
                prompt = TASK_REQUIREMENTS[prompt_key]
                prompt = (
                    prompt.replace("{{idea_index}}", str(idea_index + 1))
                        .replace("{{current_round}}", str(current_round or 0))
                        .replace("{{max_rounds}}", str(max_rounds or 0))
                )
        else:
            if sel_method == "rating":
                pool_size = self.task_config.get("replacement_pool_size", 3)
                if pool_size == 0:
                    prompt = TASK_REQUIREMENTS["PS_Discussion_Rating_NoPool"]
                else:
                    prompt = TASK_REQUIREMENTS["PS_Discussion_Rating"]
            else:
                prompt = TASK_REQUIREMENTS["PS_Discussion_SelectionTop"]
            # Safe replacements for template variables
            if "{{total_resp}}" in prompt:
                prompt = prompt.replace("{{total_resp}}", str((total_resp or 0) + 1))
            if "{{max_rounds}}" in prompt:
                prompt = prompt.replace("{{max_rounds}}", str(self.task_config.get("max_responses", 20)))

        # Check if we need to hide the agree option based on the configuration
        hide_agree_until_round = self.task_config.get("min_responses", None)
        print("hide_agree_until_round:", hide_agree_until_round)
        if hide_agree_until_round is not None and (total_resp + 1) < hide_agree_until_round:
            # Remove the agree option from the prompt
            prompt = prompt.replace('- **Agree:** If the idea meets the task objective and does not require changes, reply "Agree: No changes needed."', '')
            prompt = prompt.replace('- **Agree**: If the current idea meets the task objective and does not require changes, reply "Agree: No changes needed."', '')
            prompt = prompt.replace('- **Agree:** If the current idea is extremely creative and you cannot come up with a more creative idea, reply "Agree: No changes needed."', '')
            # Clean up any potential double newlines created by the removal
            prompt = prompt.replace('\n\n\n', '\n\n')

        # Display task-specific prompt first
        
        previous_responses_list = conversation.get_previous_responses(
            idea_index=(idea_index if disc_method == "one_by_one" else None),
            current_phase="discussion", # Or relevant phase like "discussion", "open_discussion"
        )

        # Construct message content
        msgs.append({"role": role, "content": f"\n# **Current Task**\n{prompt.strip()}"})

        # --- Build the Discussion History Section ---
        history_section_content = ["\n# **Discussion History**"] # Start with the header

        initial_ideas_str = None
        feedback_list = []

        if previous_responses_list:
            # Check if the first element is the "initial ideas" block added by get_previous_responses
            # This block is only added for "discussion" and "direct_discussion" phases
            if previous_responses_list[0].startswith("The initial ideas under discussion"):
                initial_ideas_str = previous_responses_list[0]
                feedback_list = previous_responses_list[1:] # The rest are feedback/responses

            # Add the initial ideas block if it exists
            if initial_ideas_str:
                history_section_content.append(f"{initial_ideas_str}") # Add newline for spacing

            # Add the specific introductory sentence and the feedback/responses *only if* there is feedback
            if feedback_list:
                # Use the exact original wording requested
                num_responses = self.task_config.get("llm_count", "3") # Get the number of responses from the task config
                intro_sentence = f"Team members' feedback on these ideas so far (last {num_responses} responses, in chronological order):"
                history_section_content.append(f"\n{intro_sentence}") # Add newline for spacing before the intro
                history_section_content.append("\n".join(feedback_list)) # Append the actual feedback items
            elif not initial_ideas_str: # No initial ideas were prepended AND no feedback responses exist
                 history_section_content.append("\nNo previous discussion contributions found for this context.")
            # else: If there were initial ideas but no feedback, we just show the initial ideas.

        else:
            # No history at all was returned by get_previous_responses
            history_section_content.append("\nNo previous discussion history available.")

        # Join the parts of the history section and add it as one message
        msgs.append({"role": "user", "content": "\n".join(history_section_content)})

        current_ideas_str = "\n".join(f"{i+1}. {txt}" for i, txt in enumerate(self.data_strategy.current_ideas))
        replacement_ideas_str = self.get_replacement_ideas_str(agent, sel_method)

        if self.data_strategy.replaced_ideas:
            replaced_ideas_str = "\n".join(f"{i+1}. {idea}" for i, idea in enumerate(self.data_strategy.replaced_ideas))
            replaced_ideas_section = f"\n**Previously Replaced Ideas:**\n{replaced_ideas_str}"
        else:
            replaced_ideas_section = ""  

        replacement_pool_size = self.task_config.get("replacement_pool_size", 0)
        # Append structured message with Markdown formatting
        if replacement_pool_size ==0:
            msgs.append({"role": "user", "content":
                "\n# **Current and Replaced Ideas**\n"
                "**Current Ideas Under Discussion:**\n"
                f"{current_ideas_str if current_ideas_str else '(None)'}\n\n"
                f"{replaced_ideas_section}"
                         })
        else:
            msgs.append({"role": "user", "content":
                "\n# **Current, Replacement, and Replaced Ideas**\n"
                "**Current Ideas Under Discussion:**\n"
                f"{current_ideas_str if current_ideas_str else '(None)'}\n\n"
                
                "**Replacement Ideas Pool:**\n"
                f"{replacement_ideas_str if replacement_ideas_str else '(None)'}\n"
                f"{replaced_ideas_section}"
            })

    

    def get_replacement_ideas_str(self, agent, sel_method):
        """
        Fetch and format replacement ideas based on the selection method.
        """
        if sel_method == "rating":
            replacement_ideas = self.data_strategy.replacement_ideas
        else:  # selectionTop
            replacement_ideas = self.data_strategy.agent_replacement_ideas.get(agent.name, [])
        return "\n".join(f"{i+1}. {idea}" for i, idea in enumerate(replacement_ideas))
    
    def _add_direct_discussion_instructions(self, msgs, agent, conversation, total_resp=None, current_round=None, idea_index=None):
        """
        Add instructions for direct discussion mode, including first and subsequent rounds.
        """
        task_type = self.task_config.get("task_type", "AUT")
        discussion_method = self.task_config.get("discussion_method", "all_at_once")
        model = agent.model_name  # Fetch the correct model for each agent
        role = (
            # "developer" if model in ['o3-mini','o1'] else
            "user" if model in self.task_config.get("role_assignment_in_user_prompt", [None]) else
            "system"
        )

        if total_resp == 0 or current_round == 1:
        # First round: Initial idea generation
            if task_type == "AUT":
                if discussion_method == "all_at_once":
                    prompt = TASK_REQUIREMENTS["AUT_Direct_First_Round_AllAtOnce"]
                else:  # one_by_one
                    prompt = TASK_REQUIREMENTS["AUT_Direct_First_Round_OneByOne"]
            else:  # PS
                prompt = TASK_REQUIREMENTS["PS_Direct_First_Round_AllAtOnce"]
        else:
            # Subsequent rounds: Modifications and agreements
            if task_type == "AUT":
                if discussion_method == "all_at_once":
                    prompt = TASK_REQUIREMENTS["AUT_Direct_Dicussion_AllAtOnce"]
                    prompt = prompt.replace("{{total_resp}}", str(total_resp + 1))
                else:  # one_by_one
                    prompt = TASK_REQUIREMENTS["AUT_Direct_Discussion_OneByOne"]
                    prompt = (
                    prompt.replace("{{current_round}}", str(current_round))
                        .replace("{{idea_index}}", str(idea_index or 0 + 1))
                        
                )
            else:  # PS
                prompt = TASK_REQUIREMENTS["PS_Discussion_Rating_NoPool"]
                prompt = prompt.replace("{{total_resp}}", str(total_resp + 1))
                prompt = prompt.replace("{{max_rounds}}", str(self.task_config.get("max_responses", 20)))

            # Check if we need to hide the agree option based on the configuration
            hide_agree_until_round = self.task_config.get("min_responses", None)
            print("hide_agree_until_round:", hide_agree_until_round)

            if hide_agree_until_round is not None and total_resp + 1 < hide_agree_until_round:
                # Remove the agree option from the prompt
                prompt = prompt.replace('- **Agree:** If the current idea is extremely creative and you cannot come up with a more creative idea, reply "Agree: No changes needed."', '')
                prompt = prompt.replace('- **Agree:** If the idea meets the task objective and does not require changes, reply "Agree: No changes needed."', '')
                prompt = prompt.replace('- **Agree**: If the current idea meets the task objective and does not require changes, reply "Agree: No changes needed."', '')
                # Clean up any potential double newlines created by the removal
                prompt = prompt.replace('\n\n\n', '\n\n')


        # Fetch previous responses
        disc_method = self.task_config.get("discussion_method", "all_at_once")
        previous_responses_list = conversation.get_previous_responses(
            idea_index=(idea_index if disc_method == "one_by_one" else None),
            current_phase="direct_discussion" # Or relevant phase like "discussion", "open_discussion"
        )

        # Construct message content
        msgs.append({"role": role, "content": f"\n# **Current Task**\n{prompt.strip()}"})

        # --- Build the Discussion History Section ---
        history_section_content = ["\n# **Discussion History**"] # Start with the header

        initial_ideas_str = None
        feedback_list = []

        if previous_responses_list:
            # Check if the first element is the "initial ideas" block added by get_previous_responses
            # This block is only added for "discussion" and "direct_discussion" phases
            if previous_responses_list[0].startswith("The initial ideas under discussion"):
                initial_ideas_str = previous_responses_list[0]
                feedback_list = previous_responses_list[1:] # The rest are feedback/responses

            # Add the initial ideas block if it exists
            if initial_ideas_str:
                history_section_content.append(f"{initial_ideas_str}") # Add newline for spacing

            # Add the specific introductory sentence and the feedback/responses *only if* there is feedback
            if feedback_list:
                # Use the exact original wording requested
                num_responses = self.task_config.get("llm_count", "3") # Get the number of responses from the task config
                intro_sentence = f"Team members' feedback on these ideas so far (last {num_responses} responses, in chronological order):"
                history_section_content.append(f"\n{intro_sentence}") # Add newline for spacing before the intro
                history_section_content.append("\n".join(feedback_list)) # Append the actual feedback items
            elif not initial_ideas_str: # No initial ideas were prepended AND no feedback responses exist
                 history_section_content.append("\nNo previous discussion contributions found for this context.")
            # else: If there were initial ideas but no feedback, we just show the initial ideas.

        else:
            # No history at all was returned by get_previous_responses
            history_section_content.append("\nNo previous discussion history available.")

        # Join the parts of the history section and add it as one message
        msgs.append({"role": "user", "content": "\n".join(history_section_content)})


        # --- Add Current Ideas Section (Conditional) ---
        # Original logic for adding current ideas remains the same
        if total_resp == 0 or (disc_method == 'one_by_one' and current_round == 1):
             pass # No current ideas to show yet in these cases
        else:
            current_ideas_str = "\n".join(f"{i + 1}. {txt}" for i, txt in enumerate(self.data_strategy.current_ideas))
            # Add extra newline before for better separation from history
            msgs.append({"role": "user", "content": f"\n**Current Ideas Under Discussion:**\n{current_ideas_str if current_ideas_str else '(none)'}"})

    #
    # def _add_open_discussion_instructions(self, msgs, agent, conversation, current_round=None, total_rounds=None):
    #     round_info = ""
    #     agreement_focus_section = ""
    #     is_final_rounds = False
    #     instruction_header = "# **Instruction: Open Discussion**\n" # Default header
    #
    #     if current_round is not None and total_rounds is not None:
    #         round_info = f"Current Round: {current_round} of {total_rounds}\n"
    #         final_round_threshold = 5 # Or 3, adjust as needed
    #
    #         if (total_rounds - current_round) < final_round_threshold:
    #             is_final_rounds = True
    #
    #         if is_final_rounds:
    #             """Remember to change this back"""
    #             instruction_header = "# **Instruction: Final Rounds - Converge Towards a Single Final Idea**\n" # More specific header
    #             # Create the dedicated agreement section
    #             agreement_focus_section = (
    #                 "---\n"
    #                 f"**Nearing the End ({total_rounds - current_round + 1} rounds remaining):**\n"
    #                 "The discussion should now strongly **focus on converging towards the single most promising and creative idea.**\n"
    #                 "Prioritize refining potential candidates to meet the task requirements.\n"
    #                 "Collaboratively polish the idea you want to propose as the final output.\n"
    #                 "Introducing entirely new directions at this stage is not allowed.\n"
    #                 "---\n"
    #             )
    #
    #     # Base instruction body - might be slightly adjusted based on context
    #     if is_final_rounds:
    #          # In final rounds, the focus isn't really "share freely" anymore
    #          base_instruction_body = (
    #             "Review the discussion history below. Use your response to help the group select and refine the best idea, keeping the final goal and criteria in mind.\n"
    #             "--- Discussion History ---\n"
    #          )
    #     else:
    #         base_instruction_body = (
    #             "In this open discussion phase, please share your thoughts freely to explore the topic.\n"
    #             "**Formatting Instruction:** Structure your response clearly.\n"
    #             "**Vary your format** – use paragraphs for detailed thoughts or arguments. Use lists *sparingly* and only when needed for clear, brief enumeration of distinct items.\n"
    #             "Build upon previous points and share your perspective.\n"
    #             "--- Discussion History ---\n"
    #          )
    #
    #     # Append history
    #     history = conversation.get_previous_responses(current_phase="open_discussion")
    #     history_text = "\n".join(history) if history else "(No previous responses.)"
    #
    #     # --- Combine Message Parts ---
    #     # Order: Header, Round Info, Agreement Focus (if applicable), Base Body Intro, History
    #     full_instruction = (
    #         instruction_header +
    #         round_info +
    #         agreement_focus_section + # Placed BEFORE the history
    #         base_instruction_body +
    #         history_text
    #     )
    #
    #     msgs.append({"role": "user", "content": full_instruction})
    #
    #     logging.info(f"Open discussion instructions added (Final Rounds: {is_final_rounds}), "
    #                  f"current_round={current_round}, total_rounds={total_rounds}")
    #
    #



    def _add_open_discussion_instructions(self, msgs, agent, conversation, current_round=None, total_rounds=None):
        """
        Adds ultra-minimalist open discussion instructions, primarily context + agent prompt,
        but includes a simple notification for the final rounds.
        Modifies msgs list in place.
        """
        final_rounds_warning = ""
        is_final_rounds = False
        final_round_threshold = 5 # Notify within the last 5 rounds
        max_rounds = self.task_config.get("max_responses")
        instruction_header = (
            f"Your team has a maximum of {max_rounds} rounds to finalize the list of ideas. You are currently on round {current_round}. "
            "In terms of formatting, you should not use lists or bullet points unless absolutely necessary.\n\n"
            )


        # --- Check for Final Rounds ---
        if current_round is not None and total_rounds is not None:
            rounds_remaining = total_rounds - current_round + 1
            # Check if within the threshold (using <= because rounds_remaining includes the current round)
            if rounds_remaining <= final_round_threshold:
                is_final_rounds = True
                # Simple, purely informational warning - no convergence instructions
                final_rounds_warning = (
                    "---\n"
                    f"**Note:** Nearing end of discussion ({rounds_remaining} round(s) remaining including this one).\n"
                    "---\n"
                )

        # --- History Section (Core Context) ---
        # Present history clearly FIRST - setting the immediate context
        history = conversation.get_previous_responses(current_phase="open_discussion")
        num_responses = self.task_config.get("llm_count", "3")  # Get the number of responses from the task config

        # Use a slightly more descriptive placeholder if empty
        history_text = "\n".join(history).strip() if history else "(Start of the open discussion phase)"
        history_section = f"# **Discussion History (last {num_responses} responses, in chronological order)**\n{history_text}\n"


        # --- Final Instruction Prompt (Minimalist) ---
        # Identify the agent and ask for their response directly
        # Using agent.role assumes it exists and is useful context, otherwise just use agent.name
        agent_identifier = f"{agent.name}" + (f" ({agent.role})" if hasattr(agent, 'role') and agent.role else "")
        final_instruction_prompt = f"\n---Now, **{agent_identifier}:** Your response?"


        # --- Assemble the Full Prompt Content ---
        # Order: History -> Optional Warning -> Final Agent Prompt
        full_instruction_content = (
            instruction_header +
            history_section +
            final_rounds_warning + # Appears only if is_final_rounds is True
            final_instruction_prompt
        )

        # Append the constructed message to the list
        msgs.append({"role": "user", "content": full_instruction_content})

        # Update logging to reflect the minimalist approach and final round status
        log_message = f"Minimalist open discussion instructions added for {agent.name}"
        if current_round is not None:
             log_message += f" (Round {current_round})"
        if is_final_rounds:
             log_message += " - Final rounds notification included."
        logging.info(log_message)

    def _add_iterative_refinement_instructions(self, msgs, agent, conversation):
        """
        Add instructions for the iterative refinement process.
        This includes current ideas, previous discussion context, and clear guidance.
        """
        # 2. Add current ideas section
        # Get the model and role
        model = agent.model_name
        role = "user" if model in self.task_config.get("role_assignment_in_user_prompt", [None]) else "system"

        # Get task type
        task_type = self.task_config.get("task_type", "AUT")
        current_round = conversation.data_strategy.current_idea_index + 1 if hasattr(conversation.data_strategy, "current_idea_index") else 1
        current_ideas = conversation.data_strategy.current_ideas
        if not current_ideas and current_round == 1:               # First round: Initial idea generation
            if task_type == "AUT":
                if discussion_method == "all_at_once":
                    prompt = TASK_REQUIREMENTS["AUT_Direct_First_Round_AllAtOnce"]
                else:  # one_by_one
                    prompt = TASK_REQUIREMENTS["AUT_Direct_First_Round_OneByOne"]
            else:  # PS
                prompt = TASK_REQUIREMENTS["PS_Direct_First_Round_AllAtOnce"]

            msgs.append({"role": role, "content": prompt})

        else:
            # Get the model and role
            model = agent.model_name
            role = "user" if model in self.task_config.get("role_assignment_in_user_prompt", [None]) else "system"

            # Get task type
            task_type = self.task_config.get("task_type", "AUT")

            # 1. Add the main instructions
            instruction = textwrap.dedent("""\
                Your goal is to generate ONE significantly more creative idea that has to be different from current ideas.
                **Important:**
                - Focus on quality over quantity - create ONE excellent idea rather than multiple ideas
                - Respond with just the idea itself - no additional text or explanations.
                """).strip() # Added dedent and strip


            msgs.append({"role": role, "content": instruction})

            """
            Remove round information in this iterative refinement mode
            """
            #current_round = conversation.data_strategy.current_idea_index + 1 if hasattr(conversation.data_strategy, "current_idea_index") else 1
            #max_rounds = self.task_config.get("max_responses", 15)  # Get the max_responses from task_config
            #round_info = f"Round: {current_round} of {max_rounds}"
            #msgs.append({"role": "user", "content": f"# **Round Information**\n{round_info}"})

            # 2. Add current ideas section
            current_ideas = conversation.data_strategy.all_generated_ideas
            if current_ideas:
                current_ideas_formatted = "\n".join([f"{i+1}. {idea}" for i, idea in enumerate(current_ideas)])
                msgs.append({"role": "user", "content": f"# **Current Idea(s)**\n{current_ideas_formatted}"})


            # 4. Final prompt for generation
            msgs.append({"role": "user", "content": "Please generate a new idea that is significantly more creative than these existing idea(s)."})
        return msgs
    def _add_creative_generation_instructions(self, msgs, agent, conversation):
        # Get any creative generation history
        # Get ranked ideas
        llm_count = self.task_config.get("llm_count", 3)
        threshold = 5 * llm_count
        ranked_ideas = self.data_strategy.ranked_ideas
        instruction_header = "# **Current Task**" # Default header


        if ranked_ideas:
            ranked_ideas_str = "\n".join(f"{i+1}. {idea}" for i, idea in enumerate(ranked_ideas))
        else:
            ranked_ideas_str = "No ranked ideas available."
        new_ideas_str = '(None)'

        
        if len(ranked_ideas) > threshold:
            new_ideas = ranked_ideas[threshold:]
            new_ideas_str = "\n".join(f"{i+1}. {idea}" for i, idea in enumerate(new_ideas))
            ranked_ideas = ranked_ideas[:threshold]  
            ranked_ideas_str = "\n".join(f"{i+1}. {idea}" for i, idea in enumerate(ranked_ideas))


        # Get the creative prompt from TASK_REQUIREMENTS
        creative_prompt = TASK_REQUIREMENTS.get("Creative_Idea_Generation", "Please propose creative ideas.").strip()
        # Combine creative prompt, history and ranked ideas
        full_prompt = (
            f"\n{instruction_header}\n"
            f"{creative_prompt}"
            f"\n\nPreviously ranked ideas by the team:\n{ranked_ideas_str}"
            f"\n\nNew ideas generated by the team:\n{new_ideas_str}"
        )
        msgs.append({"role": "user", "content": full_prompt})
    
    def _add_practical_discussion_instructions(self, msgs, agent, conversation, idea_index, total_resp=None, current_round=None, max_rounds=None):
        """
        Add discussion instructions for improvement focused on practicality.
        """
        # Here we use a new prompt (assumed to be provided in TASK_REQUIREMENTS)
        prompt = TASK_REQUIREMENTS.get("Practical_Improvement", "Please propose a practical improvement for the current idea.")
            # Replace template placeholders
        msgs.append({"role": "user", "content": f"\n# **Current Task**\n{prompt.strip()}"})
        
        # Append current ideas (if any)
        current_ideas_str = "\n".join(f"{i+1}. {txt}" for i, txt in enumerate(self.data_strategy.current_ideas))
        msgs.append({"role": "user", "content": f"\n# **Current Ideas Under Discussion:**\n{current_ideas_str if current_ideas_str else '(None)'}"})
        return

