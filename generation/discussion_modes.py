# discussion_modes.py

import random
import logging
from prompts import TASK_REQUIREMENTS, PS_QUESTIONS, PS_OVERALL
import json
import re
from collections import defaultdict
import textwrap
import os

class GenericDiscussionMode:
    def __init__(self, conversation, task_config, message_strategy):
        self.conversation = conversation
        self.task_config = task_config
        self.message_strategy = message_strategy
        self.data_strategy = conversation.data_strategy
        self.max_responses = task_config.get("max_responses")
        logging.info("Discussion mode initialized with task configuration: %s", self.task_config)

    def run(self, skip_to_discussion=False):
        phases= self.task_config.get("phases","three_stage")
        discussion_method = self.task_config.get("discussion_method", "all_at_once")
        question_id = self.task_config.get("question_id", "global_warming")  # Get question ID from config

        # Set the appropriate question in prompts
        global PS_OVERALL
        if question_id in PS_QUESTIONS:
            PS_OVERALL = PS_QUESTIONS[question_id]
            # Also update the TASK_REQUIREMENTS dictionary
            TASK_REQUIREMENTS['PS_Overall'] = PS_OVERALL
            TASK_REQUIREMENTS['PS_Overall_Single'] = PS_OVERALL
        else:
            print(f"Warning: Question ID '{question_id}' not found. Using default question.")

        # Create output directory for this question
        output_dir = f"results/{question_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Update conversation's output directory
        self.conversation.output_dir = output_dir

        single_llm_mode = len(self.conversation.agents) == 1
        if single_llm_mode:
            self.run_single_llm_mode()
        elif discussion_method == "none":
            if not skip_to_discussion:
                self.run_generation()
                self.run_selection()
            print("Discussion phase skipped (discussion_method=none)")

        elif phases == "direct_discussion":
            # Handle direct discussion phase with different discussion methods
            if discussion_method == "open":
                self.run_open_discussion()
            elif discussion_method == "all_at_once":
                self.run_direct_discussion()
            elif discussion_method == "iterative_refinement":
                self.run_direct_iterative_refinement()
            elif discussion_method == "one_by_one":
                self.run_direct_discussion()
            else:
                print(f"Warning: Unsupported discussion_method '{discussion_method}' for direct_discussion phase")
        elif phases == "three_stage":
            if not skip_to_discussion:
                phases = self.task_config.get("phases", "three_stage")   
                self.run_generation()
                self.run_selection()
            else:
                # Example preloaded ideas and rankings
                # initialize all the ideas
                # self.data_strategy.all_ideas = [
                #     {"idea": "Create a portable clothesline for camping by suspending rope between trees.", "agent": "CFO"},
                #     {"idea": "Fashion a quick improvised belt for holding up trousers in an emergency.", "agent": "CFO"},
                #     {"idea": "Use rope as a makeshift hammock for relaxation in a pinch.", "agent": "CFO"},
                #     {"idea": "Construct a DIY jump rope for a fun workout alternative.", "agent": "CFO"},
                #     {"idea": "Generate a unique wall decoration by weaving colorful rope into shapes.", "agent": "CFO"},
                #     {"idea": "DIY vertical garden trellis for trailing plants indoors or outdoors.", "agent": "CTO"},
                #     {"idea": "Emergency leash for pets in unexpected situations.", "agent": "CTO"},
                #     {"idea": "Portable clothesline for drying clothes on camping trips.", "agent": "CTO"},
                #     {"idea": "Backpack hydration system to secure water bottles for hiking.", "agent": "CTO"},
                #     {"idea": "Art installation tool for creating 3D sculptures in galleries.", "agent": "CTO"},
                #     {"idea": "Emergency fishing line for catching small fish in survival situations.", "agent": "CEO"},
                #     {"idea": "Makeshift belt for securing loose clothing or gear.", "agent": "CEO"},
                #     {"idea": "Temporary dog leash in a pinch for pet safety.", "agent": "CEO"},
                #     {"idea": "Decorative wall art by weaving colorful rope patterns.", "agent": "CEO"},
                #     {"idea": "Garden trellis support for climbing plants and vegetables.", "agent": "CEO"}
                # ]

                # self.data_strategy.agent_selected_ideas = {
                #     "CEO": [0, 10, 2, 5, 3],
                #     "CTO": [1, 2, 5, 10, 9],
                #     "CFO": [0, 1, 6, 10, 5]
                # }

                self.data_strategy.ranked_ideas = [
                    "Implement a 'Wellness Swap' program where employees can exchange skills or activities (like yoga sessions, cooking classes, etc.) to foster community, promote mental health, and encourage holistic wellbeing.",
                    "Create a 'Nature Day,' allowing employees to work remotely from a nature location, encouraging outdoor time, reducing stress, and enhancing creativity.",
                    "Introduce a digital 'Wellbeing Buddy' app that pairs employees with a peer for regular check-ins, support, and friendly challenges, fostering connection and accountability in maintaining wellbeing.",
                    "Implement a 'Wellness Buddy' program, pairing employees for regular check-ins and support through fitness activities, mental health discussions, and shared wellness challenges.",
                    "Create a virtual 'Personal Growth Fund' allowing employees to access a budget for activities like courses, therapy, or wellness retreats focused on their wellbeing.",
                    "Launch a 'Mood Docket' app where employees anonymously share daily sentiments, fostering open dialogue and building a collective understanding of workplace wellbeing needs.",
                    "Implement a 'Wellbeing Exchange' platform where employees can trade unused wellness days for points redeemable for mental health services or fitness classes.",
                    "Create a virtual reality relaxation room where employees can escape to calming environments and participate in guided meditation sessions during breaks.",
                    "Introduce 'Wellness Ambassadors,' trained employees who promote healthy habits, support peers, and organize regular activities focusing on physical and mental health.",
                    "Develop a 'Wellbeing Mentor' initiative where experienced staff members guide others in maintaining mental and physical health routines.",
                    "Organize a quarterly 'Wellness Day' where the company hosts events like mindfulness workshops, fitness challenges, or healthy cooking classes.",
                    "Create a 'Mindfulness Library' of curated resources, including books, podcasts, and videos, for employees to access on demand.",
                    "Launch a 'Wellbeing Dashboard' that provides employees with personalized recommendations for improving their physical and mental health based on self-reported data.",
                    "Host an annual 'Health Fair' offering free health screenings, wellness seminars, and opportunities to explore mental and physical health resources.",
                    "Develop an 'Active Breaks' program encouraging employees to participate in brief, guided physical activities during work hours to reduce stress and boost energy levels."
                ]

                print("Predefined ranked ideas loaded.")
            
            if discussion_method == "open":
                self.run_open_discussion()
            elif discussion_method == "creative":  # New branch
                self.run_creative_generation()
            elif discussion_method == "iterative_refinement":
                self.run_iterative_refinement()
            elif discussion_method in ["all_at_once", "one_by_one"]:
                self.run_discussion()
        else:
            print(f"Warning: Unsupported phases '{phases}'")
        
        print("\n=== Final Token Usage Summary ===")
        print(self.conversation.get_token_summary())


    def run_open_discussion(self):
        print("Starting open discussion phase.")
        total_resp = 0
        while total_resp < self.max_responses:
            agent = self._select_next_agent(self.conversation.agents)
            self.conversation.current_agent = agent
            msgs = self.message_strategy.construct_messages(agent, "open_discussion", self.conversation, current_round=total_resp+1, max_rounds=self.max_responses)
            resp, prompt_tokens, completion_tokens, reasoning_tokens = agent.generate_response(msgs)
            # Updated: pass current_ideas and round_number for proper idea evolution logging.
            self.conversation.update_phase_token_usage("discussion", prompt_tokens, completion_tokens, reasoning_tokens)
            #self.data_strategy.update_shared_data(self.conversation, resp)
            self.conversation.add_chat_entry(agent.model_name, agent.name, "\n".join(m["content"] for m in msgs), resp, "open_discussion", current_ideas = self.data_strategy.current_ideas, round_number=total_resp+1)

            print(f"[open_discussion] {agent.name} => {resp}")
            total_resp += 1
        print("Open discussion phase ended.")
    
            # Select the last agent who spoke to summarize
        summarizing_agent = self.conversation.current_agent
        
        task_type = self.task_config.get("task_type", "AUT")
        task_context = TASK_REQUIREMENTS['AUT_Mode1_Overall'] if task_type == "AUT" else TASK_REQUIREMENTS['PS_Overall']

        model = summarizing_agent.model_name
        role = "user" if model in self.task_config.get("role_assignment_in_user_prompt", [None]) else "system"

        summary_msgs =[]
        summary_msgs.append({"role": role, "content": f"# **Role**\n{agent.system_message}"})

        if self.task_config.get("task_type","AUT")=="AUT":
            summary_msgs.append({"role":role,"content": f"\n# **Task Requirement**\n{TASK_REQUIREMENTS['AUT_Mode1_Overall'].strip()}"})
        else:
            summary_msgs.append({"role":role,"content": f"\n# **Task Requirement**\n{TASK_REQUIREMENTS['PS_Overall'].strip()}"})
        # Create a summary request message
        summary_msgs.append(
            {
                "role": "user",
                "content": "Your goal now is to summarize and synthesize the entire discussion "
                        "into a single, compelling, and well-defined final idea. Present this as a unified concept, "
                        "as if you are proposing the final idea in response to the task.\n"
                        "Start your response *exactly* with 'FINAL IDEA:'.\n"
                        "The idea should be approximately 80-100 words."
            })
        history = self.conversation.get_previous_responses(current_phase="open_discussion",history_depth=-1)

        history_text = "\n".join(history) if history else "(Start of the open discussion phase)"

        num_responses = self.task_config.get("llm_count", "3") # Get the number of responses from the task config
        history_section = (
            f"\n# **Discussion History (in chronological order)**\n" # <-- Changed here
            f"{history_text}\n"
            # Separator moved here, before the optional warning/final prompt
            "---\n"
        )

        summary_msgs.append({
            "role": 'user',
            "content": history_section
        })

        # Generate the summary
        print("Generating summary...")
        final_idea, pt, ct, rt = summarizing_agent.generate_response(summary_msgs)
        

        # Update token usage
        self.conversation.update_phase_token_usage("discussion", pt, ct, rt)
        
        # Extract the final idea (remove the prefix if present)
        if "FINAL IDEA:" in final_idea:
            final_idea = final_idea.split("FINAL IDEA:")[1].strip()
        
        # Update the data strategy with the final idea
        self.data_strategy.current_ideas = [final_idea]
                # Log the summary
        self.conversation.add_chat_entry(
            summarizing_agent.model_name,
            summarizing_agent.name,
            "\n".join(m["content"] for m in summary_msgs),
            final_idea,
            "open_discussion",
            current_ideas=[final_idea],
            round_number=total_resp+1
        )
        
        print(f"[open_discussion_summary] {summarizing_agent.name} => {final_idea}")
        print("Open discussion phase ended with final idea extraction.")
    def run_iterative_refinement(self):
            # Initialize tracking variables
        print("Starting iterative refinement discussion phase.")


        total_resp = 0
        max_rounds = self.max_responses  # Use the same max as other discussion methods
        if not hasattr(self.data_strategy, 'past_current_ideas'):
                self.data_strategy.past_current_ideas = [] # Or deque(maxlen=self.max_past_ideas)
        if not hasattr(self.data_strategy, 'all_generated_ideas'):
                self.data_strategy.all_generated_ideas = self.data_strategy.ranked_ideas[:] # Start with current
        if not self.data_strategy.current_ideas:
                self.data_strategy.current_ideas= [self.data_strategy.ranked_ideas[0]]

        consecutive_same_counter = 0
        last_best_idea = None
        convergence_threshold = self.task_config.get("llm_count", 3)  # or your config key

        # Continue for multiple rounds
        while total_resp < max_rounds:
            # Track token usage for this phase
            total_prompt_tokens = 0
            total_completion_tokens = 0
            total_reasoning_tokens = 0
            


            # Capture the current ideas for reference
            original_ideas = self.data_strategy.current_ideas.copy()
            
            # Select agent
            agent = self._select_next_agent(self.conversation.agents)
            self.conversation.current_agent = agent
            
            # Generate new idea using the message strategy
            msgs = self.message_strategy.construct_messages(agent, "iterative_refinement", self.conversation)        
            response, prompt_tokens, completion_tokens, reasoning_tokens = agent.generate_response(msgs)

            # Parse the JSON response to extract the idea
            new_idea = response
            print(f"Extracted idea: {new_idea}")
            # You can also store the reasoning if needed
            self.data_strategy.all_generated_ideas.append(new_idea)
            # Update token usage and conversation log
            self.conversation.add_chat_entry(
                agent.model_name, 
                agent.name, 
                "\n".join(m["content"] for m in msgs), 
                response,
                "discussion",
                round_number=total_resp+1
            )
            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens
            total_reasoning_tokens += reasoning_tokens
            
            print(f"[iterative_refinement] {agent.name} generated new idea: {new_idea}")
            
            # Now rank the ideas (new idea + current ideas)
            ranking_msgs = []
            # Use agent.model_name to set the role properly.
            model = agent.model_name
            role = "user" if model in self.task_config.get("role_assignment_in_user_prompt", [None]) else "system"
            
            # Get task type and add system prompt
            task_type = self.task_config.get("task_type", "AUT")
            if task_type == "PS":
                system_prompt = TASK_REQUIREMENTS['PS_Overall']
            elif task_type == "AUT":
                system_prompt = TASK_REQUIREMENTS['AUT_Overall']
            
            # Build ranking prompt (unchanged)
            ideas_to_rank = [new_idea] + self.data_strategy.current_ideas + self.data_strategy.past_current_ideas
            # Randomize order using list operations instead of string operations
            ideas_to_rank = list(set(ideas_to_rank))  # Remove duplicates (order doesn't matter)

            shuffled_ideas = ideas_to_rank[:]  # Create a copy of the list
            random.shuffle(shuffled_ideas)  # Shuffle the copy
            # Create text with randomized order
            ideas_text = "\n".join([f"Idea {i+1}: {idea}" for i, idea in enumerate(shuffled_ideas)])


            role = "user" if model in self.task_config.get("role_assignment_in_user_prompt", [None]) else "system"

            ranking_msgs =[]
            ranking_msgs.append({"role": role, "content": f"# **Role**\n{agent.system_message}"})

            if self.task_config.get("task_type","AUT")=="AUT":
                ranking_msgs.append({"role":role,"content": f"\n# **Task Requirement**\n{TASK_REQUIREMENTS['AUT_Mode1_Overall'].strip()}"})
            else:
                ranking_msgs.append({"role":role,"content": f"\n# **Task Requirement**\n{TASK_REQUIREMENTS['PS_Overall'].strip()}"})

            ranking_prompt = ("We define creativity as a combination of novelty (how original or unexpected the idea is in this context) and usefulness (its potential practical value or impact in addressing the goal). "
            "Please output the BEST idea based on creativity.\n"
            "Ideas to rank:\n"
            f"{ideas_text}\n"
            "Provide only the best idea, verbatim. Do not include any explanations or use markdown formatting. Do not include numbering.")




            ranking_prompt = textwrap.dedent(ranking_prompt).strip()

            ranking_msgs.extend([
                {"role": 'user', "content": ranking_prompt}
            ])
            best_idea, r_prompt_tokens, r_completion_tokens, r_reasoning_tokens = agent.generate_response(ranking_msgs)

            best_idea = re.sub(r'^Idea\s*\d+:\s*', '', best_idea)

            # Update token usage
            total_prompt_tokens += r_prompt_tokens
            total_completion_tokens += r_completion_tokens  
            total_reasoning_tokens += r_reasoning_tokens
            
            self.data_strategy.past_current_ideas.append(self.data_strategy.current_ideas[0])
            self.data_strategy.current_ideas = [best_idea]

            # Determine if the new idea is best and should replace current idea
            if best_idea == new_idea or new_idea in best_idea:
                print(f"[iterative_refinement] New idea ranked highest and replaced current idea.")
                replacement_made = True
            else:
                
                print(f"[iterative_refinement] Current idea ranked higher. No replacement made.")
                replacement_made = False
            # Add ranking to conversation log
            self.conversation.add_chat_entry(
                agent.model_name,
                agent.name,
                "\n".join(m["content"] for m in ranking_msgs),
                best_idea,
                "discussion",
                round_number=total_resp+1
            )
            
            past_current_idea_limit = self.task_config.get("llm_count", 3) + 1  # Default to 10 if not set
            if len(self.data_strategy.past_current_ideas) >  past_current_idea_limit:
                self.data_strategy.past_current_ideas= self.data_strategy.past_current_ideas[-past_current_idea_limit:]
            # After ranking and evaluating:

            # ... inside the while loop, after best_idea is determined:
            if best_idea == last_best_idea:
                consecutive_same_counter += 1
            else:
                consecutive_same_counter = 1
                last_best_idea = best_idea

            if consecutive_same_counter >= convergence_threshold:
                print(
                    f"[iterative_refinement] Same idea chosen for {convergence_threshold} consecutive rounds. Early stopping.")
                self.conversation.add_chat_entry(
                    agent.model_name,
                    agent.name,
                    "",
                    f"Final idea (Round {total_resp + 1}): {self.data_strategy.current_ideas[0]}",
                    "discussion",
                    current_ideas=self.data_strategy.current_ideas,
                    round_number=total_resp + 1
                )
                break
            # Log the final chosen idea
            self.conversation.add_chat_entry(
                agent.model_name,
                agent.name,
                "",
                f"Replaced: {replacement_made}. Final idea for (Round {total_resp+1}): {self.data_strategy.current_ideas[0]}",
                "discussion",
                current_ideas = self.data_strategy.current_ideas,
                round_number=total_resp+1
            )
            
            # Update total token usage for the phase
            self.conversation.update_phase_token_usage(
                "discussion", 
                total_prompt_tokens, 
                total_completion_tokens,
                total_reasoning_tokens
            )
            print("Starting iterative refinement discussion phase.")
            total_resp += 1
        print("Iterative refinement phase completed.")
        print(f"Original idea: {original_ideas[0] if original_ideas else '(none)'}")
        print(f"Final idea: {self.data_strategy.current_ideas[0]}")
        return

    def run_direct_iterative_refinement(self):
        # Initialize tracking variables
        print("Starting iterative refinement discussion phase - without intitial idea generation.")
        self.data_strategy.current_ideas = []  # Clear current ideas initially.
        total_resp = 0
        max_rounds = self.max_responses  # Use the same max as other discussion methods
        if not hasattr(self.data_strategy, 'past_current_ideas'):
            self.data_strategy.past_current_ideas = []  # Or deque(maxlen=self.max_past_ideas)
        if not hasattr(self.data_strategy, 'all_generated_ideas'):
            self.data_strategy.all_generated_ideas = []  # Start with current
        if not self.data_strategy.current_ideas:
            self.data_strategy.current_ideas = []

        consecutive_same_counter = 0
        last_best_idea = None
        convergence_threshold = self.task_config.get("llm_count", 3)  # or your config key

        # Continue for multiple rounds

        while total_resp < max_rounds:

            # Track token usage for this phase
            total_prompt_tokens = 0
            total_completion_tokens = 0
            total_reasoning_tokens = 0

            # Capture the current ideas for reference

            # Select agent
            agent = self._select_next_agent(self.conversation.agents)
            self.conversation.current_agent = agent

            # Generate new idea using the message strategy
            msgs = self.message_strategy.construct_messages(agent, "iterative_refinement", self.conversation)
            print("prompt here", msgs)
            response, prompt_tokens, completion_tokens, reasoning_tokens = agent.generate_response(msgs)
            print("response", response)
            print("total_resp", total_resp)
            if total_resp == 0:
                print("here")
                self.data_strategy.current_ideas = [response]
                self.data_strategy.all_generated_ideas.append(response)
                self.conversation.add_chat_entry(agent.model_name, agent.name, "\n".join(m["content"] for m in msgs), response, "direct_discussion",current_ideas=self.data_strategy.current_ideas,round_number=total_resp+1)
                original_ideas = self.data_strategy.current_ideas.copy()
                total_resp +=1
                print("parsed this properly")
                continue
            # Parse the JSON response to extract the idea
            new_idea = response
            print(f"Extracted idea: {new_idea}")
            # You can also store the reasoning if needed
            self.data_strategy.all_generated_ideas.append(new_idea)
            # Update token usage and conversation log
            self.conversation.add_chat_entry(
                agent.model_name,
                agent.name,
                "\n".join(m["content"] for m in msgs),
                response,
                "discussion",
                round_number=total_resp + 1
            )
            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens
            total_reasoning_tokens += reasoning_tokens

            print(f"[iterative_refinement] {agent.name} generated new idea: {new_idea}")

            # Now rank the ideas (new idea + current ideas)
            ranking_msgs = []
            # Use agent.model_name to set the role properly.
            model = agent.model_name
            role = "user" if model in self.task_config.get("role_assignment_in_user_prompt", [None]) else "system"

            # Get task type and add system prompt
            task_type = self.task_config.get("task_type", "AUT")
            if task_type == "PS":
                system_prompt = TASK_REQUIREMENTS['PS_Overall']
            elif task_type == "AUT":
                system_prompt = TASK_REQUIREMENTS['AUT_Overall']

            # Build ranking prompt (unchanged)
            ideas_to_rank = [new_idea] + self.data_strategy.current_ideas + self.data_strategy.past_current_ideas
            # Randomize order using list operations instead of string operations
            ideas_to_rank = list(set(ideas_to_rank))  # Remove duplicates (order doesn't matter)

            shuffled_ideas = ideas_to_rank[:]  # Create a copy of the list
            random.shuffle(shuffled_ideas)  # Shuffle the copy
            # Create text with randomized order
            ideas_text = "\n".join([f"Idea {i + 1}: {idea}" for i, idea in enumerate(shuffled_ideas)])

            role = "user" if model in self.task_config.get("role_assignment_in_user_prompt", [None]) else "system"

            ranking_msgs = []
            ranking_msgs.append({"role": role, "content": f"# **Role**\n{agent.system_message}"})

            if self.task_config.get("task_type", "AUT") == "AUT":
                ranking_msgs.append({"role": role,
                                     "content": f"\n# **Task Requirement**\n{TASK_REQUIREMENTS['AUT_Mode1_Overall'].strip()}"})
            else:
                ranking_msgs.append(
                    {"role": role, "content": f"\n# **Task Requirement**\n{TASK_REQUIREMENTS['PS_Overall'].strip()}"})

            ranking_prompt = (
                "We define creativity as a combination of novelty (how original or unexpected the idea is in this context) and usefulness (its potential practical value or impact in addressing the goal). "
                "Please output the BEST idea based on creativity.\n"
                "Ideas to rank:\n"
                f"{ideas_text}\n"
                "Provide only the best idea, verbatim. Do not include any explanations or use markdown formatting. Do not include numbering.")

            ranking_prompt = textwrap.dedent(ranking_prompt).strip()

            ranking_msgs.extend([
                {"role": 'user', "content": ranking_prompt}
            ])
            best_idea, r_prompt_tokens, r_completion_tokens, r_reasoning_tokens = agent.generate_response(ranking_msgs)

            best_idea = re.sub(r'^Idea\s*\d+:\s*', '', best_idea)

            # Update token usage
            total_prompt_tokens += r_prompt_tokens
            total_completion_tokens += r_completion_tokens
            total_reasoning_tokens += r_reasoning_tokens

            self.data_strategy.past_current_ideas.append(self.data_strategy.current_ideas[0])
            self.data_strategy.current_ideas = [best_idea]

            # Determine if the new idea is best and should replace current idea
            if best_idea == new_idea or new_idea in best_idea:
                print(f"[iterative_refinement] New idea ranked highest and replaced current idea.")
                replacement_made = True
            else:

                print(f"[iterative_refinement] Current idea ranked higher. No replacement made.")
                replacement_made = False
            # Add ranking to conversation log
            self.conversation.add_chat_entry(
                agent.model_name,
                agent.name,
                "\n".join(m["content"] for m in ranking_msgs),
                best_idea,
                "discussion",
                round_number=total_resp + 1
            )

            past_current_idea_limit = self.task_config.get("llm_count", 3) + 1  # Default to 10 if not set
            if len(self.data_strategy.past_current_ideas) >  past_current_idea_limit:
                self.data_strategy.past_current_ideas= self.data_strategy.past_current_ideas[-past_current_idea_limit:]

            # ... inside the while loop, after best_idea is determined:
            if best_idea == last_best_idea:
                consecutive_same_counter += 1
            else:
                consecutive_same_counter = 1
                last_best_idea = best_idea

            if consecutive_same_counter >= convergence_threshold:
                print(
                    f"[iterative_refinement] Same idea chosen for {convergence_threshold} consecutive rounds. Early stopping.")
                self.conversation.add_chat_entry(
                    agent.model_name,
                    agent.name,
                    "",
                    f"Final idea (Round {total_resp + 1}): {self.data_strategy.current_ideas[0]}",
                    "discussion",
                    current_ideas=self.data_strategy.current_ideas,
                    round_number=total_resp + 1
                )
                break
            # Log the final chosen idea
            self.conversation.add_chat_entry(
                agent.model_name,
                agent.name,
                "",
                f"Replaced: {replacement_made}. Final idea for (Round {total_resp + 1}): {self.data_strategy.current_ideas[0]}",
                "discussion",
                current_ideas=self.data_strategy.current_ideas,
                round_number=total_resp + 1
            )

            # Update total token usage for the phase
            self.conversation.update_phase_token_usage(
                "discussion",
                total_prompt_tokens,
                total_completion_tokens,
                total_reasoning_tokens
            )
            print("Starting iterative refinement discussion phase.")
            total_resp += 1
        print("Iterative refinement phase completed.")
        print(f"Original idea: {original_ideas[0] if original_ideas else '(none)'}")
        print(f"Final idea: {self.data_strategy.current_ideas[0]}")
        return

    def run_creative_generation(self):
        print("Starting creative generation phase.")
        # Step 1: Creative idea generation (expect 9 new ideas)
        original_top_ideas = self.data_strategy.ranked_ideas[:5].copy()  # or just list slicing        
        novel_ideas = []
        for agent in self.conversation.agents:
            self.conversation.current_agent = agent
            msgs = self.message_strategy.construct_messages(agent, "creative_generation", self.conversation)
            resp, pt, ct, rt = agent.generate_response(msgs)
            
            # Parse the response to extract 5 ideas
            ideas = [idea.strip() for idea in resp.split('\n') if idea.strip()]

            pattern = r"^\d+\.\s+"

            # 3. Use re.sub() in a list comprehension to remove the pattern
            ideas = [re.sub(pattern, "", idea) for idea in ideas]


            novel_ideas.extend([(idea, agent.name) for idea in ideas[:5]])
            
            # use ranked idea as current idea store
            self.data_strategy.ranked_ideas.extend(ideas[:5])
            self.conversation.add_chat_entry(
                agent.model_name,
                agent.name,
                "\n".join(m["content"] for m in msgs),
                resp,
                "creative_generation",
                current_ideas = ideas,

            )
            self.conversation.update_phase_token_usage("discussion", pt, ct, rt)
            print(f"Agent {agent.name} generated {len(ideas[:5])} novel ideas")


        # Step 2: Collect creative ideas as the new pool
        self.data_strategy.all_ideas=([{"idea": idea, "agent": agent} for idea,agent in novel_ideas])
        # For creative phase, we expect a full rating on these ideas.
        # Reusing selection: here force selection method "rating" and use all creative ideas as ranked pool.
        self.data_strategy.idea_scores = {}  # reset scores
        self.run_selection_novelty()
        # Step 3: Select top creative idea from ranked_ideas (first one)

        self.data_strategy.current_ideas = self.data_strategy.ranked_ideas[:5]  # Get the top 5 ideas for reference
        print(f"Top 5 creative ideas: {self.data_strategy.current_ideas}")

        for agent in self.conversation.agents:
            # each agent improve all 5 in a round

            self.conversation.current_agent = agent
            msgs = self.message_strategy.construct_messages(agent, 'practical_discussion', self.conversation)
            resp, pt, ct, rt = agent.generate_response(msgs)
            ideas = [idea.strip() for idea in resp.split('\n') if idea.strip()]
            self.data_strategy.current_ideas = ideas
            self.conversation.add_chat_entry(
            agent.model_name,
            agent.name,
            "\n".join(m["content"] for m in msgs),
            resp,
            "practical_discussion",
            current_ideas = ideas
            )


        # Step (e): Final ranking combining top novel and initial ideas
        combined_ideas = original_top_ideas + self.data_strategy.current_ideas
        random.shuffle(combined_ideas)  # Randomize order
        self.data_strategy.all_ideas = [{"idea": idea, "agent": "system"} for idea in combined_ideas]

        self.data_strategy.idea_scores = {}  # reset scores
        self.run_selection()
        # now choose the best one
        self.data_strategy.current_ideas = [self.data_strategy.ranked_ideas[0]]
        print(f"Final selected idea: {self.data_strategy.current_ideas[0]}")
        # log it
        # Log the final outcome
        self.conversation.add_chat_entry(
            "system",
            "system",
            "Final idea selection from creative generation process",
            self.data_strategy.current_ideas[0],
            "creative_generation",
            current_ideas=[self.data_strategy.current_ideas[0]],
        )






    def run_practical_discussion(self):
        print("Starting practical discussion phase.")
        self.data_strategy.first_agent_name = None  # optional clear
        disc_method = self.task_config.get("discussion_method", "all_at_once")
            # Reuse the same all_at_once loop, but messages use phase 'practical_discussion'
        self.data_strategy.reset_agreements()
        total_resp = 0
        while total_resp < self.max_responses:
            remain = [ag for ag in self.conversation.agents if not self.data_strategy.agent_has_agreed(ag.name)]
            if not remain:
                print("All agents agreed (practical discussion).")
                self._print_final()
                return
            agent = self._select_next_agent(remain)
            self.conversation.current_agent = agent
            msgs = self.message_strategy.construct_messages(agent, 'practical_discussion', self.conversation)
            resp, pt, ct, rt = agent.generate_response(msgs)
            self.conversation.add_chat_entry(agent.model_name, agent.name, "\n".join(m["content"] for m in msgs), resp, 'discussion', current_ideas=self.data_strategy.current_ideas, round_number=total_resp+1)
            self.conversation.update_phase_token_usage("discussion", pt, ct, rt)
            print(f"[practical_discussion] {agent.name} => {resp}")
            self.data_strategy.update_shared_data(self.conversation, resp)
            total_resp += 1
        print("Practical discussion phase ended.")
        print("\n=== Final Token Usage Summary ===")
        print(self.conversation.get_token_summary())


    # ---------------- Single Agent ----------------
    def run_single_llm_mode(self):
        print("Starting single LLM mode.")
        agent = self.conversation.agents[0]  
        messages = self.message_strategy.construct_messages(agent, "single_task", self.conversation)

        # generate response
        response, prompt_tokens, completion_tokens, reasoning_tokens = agent.generate_response(messages)
        self.conversation.add_chat_entry(agent.model_name, agent.name, "\n".join(m['content'] for m in messages), response, 'single_llm')

        # update token usage
        self.conversation.update_phase_token_usage("single_llm", prompt_tokens, completion_tokens,reasoning_tokens)

        # print
        print(f"Response from {agent.name}: {response}")

    # ---------------- Generation ----------------
    def run_generation(self):
        print("Starting idea generation phase.")
        agents= self.conversation.agents[:]
        if self.task_config.get("discussion_order_method")=="random":
            random.shuffle(agents)
        
        if not self.data_strategy.first_agent_name and agents:
            self.data_strategy.first_agent_name = agents[0].name

        for ag in agents:
            self.conversation.current_agent= ag
            msgs= self.message_strategy.construct_messages(ag, 'idea_generation', self.conversation)

            # Generate response and get token usage
            resp, prompt_tokens, completion_tokens, reasoning_tokens = ag.generate_response(msgs)
            self.conversation.add_chat_entry(ag.model_name, ag.name, "\n".join(m['content'] for m in msgs), resp, 'idea_generation')

            # Update token usage
            self.conversation.update_phase_token_usage("idea_generation", prompt_tokens, completion_tokens,reasoning_tokens)

            self.data_strategy.collect_ideas(ag.name, resp)
            
            logging.debug("Agent %s generated ideas: %s", ag.name, resp)

        # Print token usage summary for the generation phase
        print("\n=== Token Usage Summary (Generation Phase) ===")
        print(self.conversation.get_token_summary())

    # ---------------- Selection ----------------
    def run_selection(self):
        print("Starting selection phase.")
        agents= self.conversation.agents[:]
        sel_method= self.task_config.get("selection_method","rating")
        if self.task_config.get("discussion_order_method")=="random":
            random.shuffle(agents)

        random.shuffle(self.data_strategy.all_ideas) # Make a copy

        for ag in agents:
            self.conversation.current_agent= ag
            msgs= self.message_strategy.construct_messages(ag, 'selection', self.conversation)

            lines=[f"Idea {i+1}: {x['idea']}" for i,x in enumerate(self.data_strategy.all_ideas)]
            msgs.append({"role":"assistant","content":"\n".join(lines)})

            # Generate response and get token usage
            resp, prompt_tokens, completion_tokens, reasoning_tokens = ag.generate_response(msgs)
            self.conversation.add_chat_entry(ag.model_name, ag.name, "\n".join(m['content'] for m in msgs), resp, 'selection')

            # Update token usage
            self.conversation.update_phase_token_usage("selection",prompt_tokens, completion_tokens,reasoning_tokens)

            if sel_method=="rating":
                self.data_strategy.collect_scores(ag.name, resp)
            else:
                self.data_strategy.collect_selections(ag.name, resp)

        if sel_method=="rating":
            self.data_strategy.calculate_rankings_by_average(self.conversation)
        
        # Print token usage summary for the generation phase
        print("\n=== Token Usage Summary (Selection Phase) ===")
        print(self.conversation.get_token_summary())

    def run_selection_novelty(self):
        """Special version of run_selection that uses novelty-focused prompts"""
        print("Starting creative selection phase.")
        agents = self.conversation.agents[:]
        if self.task_config.get("discussion_order_method") == "random":
            random.shuffle(agents)
        random.shuffle(self.data_strategy.all_ideas) # Make a copy

        for ag in agents:
            self.conversation.current_agent = ag
            # Use selection_novelty instead of regular selection prompt
            msgs = self.message_strategy.construct_messages(ag, 'selection_novelty', self.conversation)
            
            lines = [f"Idea {i+1}: {x['idea']}" for i,x in enumerate(self.data_strategy.all_ideas)]
            msgs.append({"role": "assistant", "content": "\n".join(lines)})

            resp, prompt_tokens, completion_tokens, reasoning_tokens = ag.generate_response(msgs)
            self.conversation.add_chat_entry(
                ag.model_name, 
                ag.name, 
                "\n".join(m["content"] for m in msgs), 
                resp, 
                'selection_novelty'
            )
            self.conversation.update_phase_token_usage(
                "selection",
                prompt_tokens, 
                completion_tokens,
                reasoning_tokens
            )
            
            self.data_strategy.collect_scores(ag.name, resp)

        self.data_strategy.calculate_rankings_by_average(self.conversation)
        print("\n=== Token Usage Summary (Creative Selection Phase) ===")
        print(self.conversation.get_token_summary())

    # ---------------- Discussion ----------------
    def run_discussion(self):
        print("Starting discussion phase.")
        self.data_strategy.first_agent_name= None  # optional clear
        disc_method= self.task_config.get("discussion_method","all_at_once")
        if disc_method=="all_at_once":
            self.discussion_all_at_once()
        else:
            self.discussion_one_by_one()
        
        # Print token usage summary for the discussion phase
        print("\n=== Token Usage Summary (Discussion Phase) ===")
        print(self.conversation.get_token_summary())

    def generate_with_retries(self, agent, msgs, max_retries=50):
        """
        Call agent.generate_response, parse with parse_fn, retry on parse failure.
        parse_fn should return a truthy value on success, or None on failure.
        """
        for attempt in range(1, max_retries + 1):
            resp, pt, ct, rt = agent.generate_response(msgs)
            agent_name = self.conversation.current_agent.name
            logging.info("Agent response: %s", resp)
            result = self.data_strategy._parse_one_by_one_response_validate(resp, agent_name)
            if result[0] is not None:
                return resp, pt, ct, rt
            logging.warning("Attempt %d/%d: invalid parse, retrying…", attempt, max_retries)

        raise RuntimeError(f"Failed to get valid response after {max_retries} attempts")
    def discussion_all_at_once(self):
        """
        Handles 'all_at_once' discussion.
        Branches behavior based on 'discussion_order_method':
        - 'hand_raising': New two-pass mechanism (generate all -> score all -> select highest).
        - 'fixed'/'random': Original mechanism (select speaker -> generate -> commit).
        Supports (rating) or (selectionTop), for AUT or PS.
        """
        disc_order = self.task_config.get("discussion_order_method", "fixed")
        print(f"Starting discussion phase (all_at_once, order: {disc_order}).")

        self.data_strategy.reset_agreements()
        sel_method = self.task_config.get("selection_method", "rating")
        ttype = self.task_config.get("task_type", "AUT")
        initial_setup_done = False


        self.conversation.add_chat_entry(
                    'initial idea',
                    'initial idea',
                    '',
                    '',
                    'discussion',
                    current_ideas=self.data_strategy.ranked_ideas[:1], # Log current state
                    round_number=0
                )

        total_resp = 0
        while total_resp < self.max_responses:
            remain = [ag for ag in self.conversation.agents if not self.data_strategy.agent_has_agreed(ag.name)]
            if not remain:
                print(f"All agents agreed (all_at_once, order: {disc_order}).")
                self._print_final()
                return

            # --- Initial Idea Setup (Run once, before agent selection/generation) ---
            # This needs to happen regardless of order method, but only once.
            if not initial_setup_done:
                # Use the first available agent for setup reference if needed (esp. for selectionTop)
                if not remain: # Should not happen if loop condition is met, but safety check
                    print("Error: No remaining agents for initial setup. Breaking.")
                    break
                agent_for_setup_ref = remain[0]

                if sel_method == "rating":
                    if ttype == "AUT":
                        self.data_strategy.current_ideas = self.data_strategy.ranked_ideas[:5]
                        self.data_strategy.replacement_ideas = self.data_strategy.ranked_ideas[5:10]
                        self.data_strategy.left = self.data_strategy.ranked_ideas[10:]
                    else: # PS
                        pool_size = self.task_config.get("replacement_pool_size", 3)
                        self.data_strategy.current_ideas = self.data_strategy.ranked_ideas[:1]
                        if pool_size > 0:
                            self.data_strategy.replacement_ideas = self.data_strategy.ranked_ideas[1:1 + pool_size]
                            self.data_strategy.left = self.data_strategy.ranked_ideas[1 + pool_size:]
                        else:
                            self.data_strategy.replacement_ideas = []
                            self.data_strategy.left = self.data_strategy.ranked_ideas[1:]
                    initial_setup_done = True

                elif sel_method == "selectionTop":
                    # Use the reference agent to establish the initial state for the round
                    if not self.data_strategy.first_agent_name:
                        # Set the anchor agent name based on the first agent in 'remain' this round
                        self.data_strategy.first_agent_name = agent_for_setup_ref.name

                    # Perform setup using the established first_agent_name's preferences
                    # Ensure all_ideas is populated (might happen if skipping phases)
                    if not hasattr(self.data_strategy, 'all_ideas') or not self.data_strategy.all_ideas:
                         print("Warning: selectionTop requires self.data_strategy.all_ideas, which is empty. Cannot initialize ideas.")
                         # Handle this error state - maybe break or use a default?
                         # For now, we'll let it potentially fail below if agent_selected_ideas access empty all_ideas
                         all_idea_texts = []
                    else:
                        all_idea_texts = [idea['idea'] for idea in self.data_strategy.all_ideas]

                    # Ensure agent_selected_ideas is populated
                    if not hasattr(self.data_strategy, 'agent_selected_ideas'):
                         self.data_strategy.agent_selected_ideas = {} # Initialize if missing

                    first_agent_picks = self.data_strategy.agent_selected_ideas.get(self.data_strategy.first_agent_name, [])


                    if ttype == "AUT":
                        current_ideas = [all_idea_texts[i] for i in first_agent_picks if 0 <= i < len(all_idea_texts)][:5]
                        self.data_strategy.current_ideas = current_ideas
                        # Ensure replacement ideas are populated for all agents if needed later
                        if not hasattr(self.data_strategy, 'agent_replacement_ideas'):
                            self.data_strategy.agent_replacement_ideas = {}
                        for ag in self.conversation.agents:
                           if ag.name not in self.data_strategy.agent_replacement_ideas:
                               idxs = self.data_strategy.agent_selected_ideas.get(ag.name, [])
                               self.data_strategy.agent_replacement_ideas[ag.name] = [
                                   all_idea_texts[i] for i in idxs if 0 <= i < len(all_idea_texts)
                               ][:5] # AUT uses top 5 as potential replacements
                    else: # PS
                        current_ideas = []
                        pool_size = self.task_config.get("replacement_pool_size", 3)
                        if first_agent_picks:
                           if 0 <= first_agent_picks[0] < len(all_idea_texts):
                               current_ideas.append(all_idea_texts[first_agent_picks[0]])

                        self.data_strategy.current_ideas = current_ideas[:1] # Ensure only one current idea for PS
                        # Ensure replacement ideas are populated for all agents
                        if not hasattr(self.data_strategy, 'agent_replacement_ideas'):
                            self.data_strategy.agent_replacement_ideas = {}
                        for ag in self.conversation.agents:
                            if ag.name not in self.data_strategy.agent_replacement_ideas:
                                idxs = self.data_strategy.agent_selected_ideas.get(ag.name, [])
                                agent_replacements = [all_idea_texts[i] for i in idxs[1:] if 0 <= i < len(all_idea_texts)][:pool_size]
                                self.data_strategy.agent_replacement_ideas[ag.name] = agent_replacements

                    initial_setup_done = True # Mark setup as done for this discussion

            # --- Branch based on Discussion Order Method ---
            selected_agent = None
            selected_response = None
            selected_messages = None
            generation_pt, generation_ct, generation_rt = 0, 0, 0 # Tokens for the *chosen* speaker's generation

            if disc_order == "hand_raising":
                self.data_strategy.reset_agreements()

                # --- New Hand-Raising Logic ---
                print(f"\n--- Round {total_resp + 1}: Hand-Raising Protocol ---")
                # Step 1: Generate Potential Responses
                potential_responses = {}
                print("  Generating Potential Responses...")
                for agent in remain:
                    self.conversation.current_agent = agent # Context for message generation
                    msgs = self.message_strategy.construct_messages(
                        agent, 'discussion', self.conversation,
                        total_resp=total_resp, max_rounds=self.max_responses
                    )
                    #resp, pt, ct, rt = agent.generate_response(msgs)

                    resp, pt, ct, rt = self.generate_with_retries(
                        agent,
                        msgs
                    )


                    potential_responses[agent.name] = {
                        "response": resp, "prompt_tokens": pt, "completion_tokens": ct,
                        "reasoning_tokens": rt, "messages": msgs
                    }



                    # print(f"    {agent.name} potential: {resp[:80]}...") # Optional: Log snippet
                # Step 2: Generate Intention Scores
                intention_scores = {}
                total_intention_pt, total_intention_ct, total_intention_rt = 0, 0, 0

                for agent in remain:
                    self.conversation.current_agent = agent # Context for message generation
                    agent_potential_response = potential_responses[agent.name]["response"]
                    #history = self.conversation.get_previous_responses(current_phase="discussion", history_depth=-1) # Adjust depth as needed
                    #history_text = "\n".join(history) if history else "(Start of Discussion)"
                    # Define the intention prompt (consider moving to prompts.py)
                    # Define the intention prompt (Focused on CREATIVITY)

                    intention_prompt = TASK_REQUIREMENTS["Intention_Scoring"]
                    #intention_prompt = intention_prompt.replace("{history_text}", history_text)
                    intention_prompt = intention_prompt.replace("{current_idea}", "\n".join(self.data_strategy.current_ideas))
                    intention_prompt = intention_prompt.replace("{agent_potential_response}", agent_potential_response)
                    model = agent.model_name
                    role = (
                        # "developer" if model in ['o3-mini','o1'] else
                        "user" if model in self.task_config.get("role_assignment_in_user_prompt", [None]) else
                        "system"
                    )
                    intention_msgs =[]
                    intention_msgs.append({"role": role, "content": f"# **Role**\n{agent.system_message}"})
                    if self.task_config.get("task_type","AUT")=="AUT":
                        intention_msgs.append({"role":role,"content": f"\n# **Task Requirement**\n{TASK_REQUIREMENTS['AUT_Mode1_Overall'].strip()}"})
                    else:
                        intention_msgs.append({"role":role,"content": f"\n# **Task Requirement**\n{TASK_REQUIREMENTS['PS_Overall'].strip()}"})


                    intention_msgs.append({"role": 'user', "content": intention_prompt})

                    score_resp, ipt, ict, irt = agent.generate_response(intention_msgs)

                    # Parse the score
                    # Parse the score (supports decimals)
                    score = 0.0  # Default score as float
                    try:
                        match = re.search(r'\d+(\.\d+)?', score_resp)
                        if match:
                            score = float(match.group(0))
                            score = max(1.0, min(10.0, score))  # Clamp score to range 1-10
                        else:
                            print(
                                f"    Warning: Could not parse score from '{score_resp}' for {agent.name}. Defaulting to 0.")
                    except Exception as e:
                        print(
                            f"    Warning: Error parsing score for {agent.name} ('{score_resp}'): {e}. Defaulting to 0.")
                    intention_scores[agent.name] = {
                        "score": score,
                        "raw_response": score_resp,
                        "prompt_tokens": ipt,
                        "completion_tokens": ict,
                        "reasoning_tokens": irt,
                        "messages": intention_msgs # For logging
                    }
                    # Accumulate intention token usage immediately
                    total_intention_pt += ipt
                    total_intention_ct += ict
                    total_intention_rt += irt
                    # print(f"    {agent.name} intention score: {score} (Raw: '{score_resp}')") # Optional: Log score

                # Update total phase token usage for *all* intention calls this round
                self.conversation.update_phase_token_usage("discussion", total_intention_pt, total_intention_ct, total_intention_rt)

                # (Optional but recommended) Log the intention scoring results for transparency
                for name, data in intention_scores.items():
                     # Find the agent object to get model name
                     agent_obj = next((ag for ag in remain if ag.name == name), None)
                     if agent_obj:
                         self.conversation.add_chat_entry(
                             agent_obj.model_name, name,
                             "\n".join(m['content'] for m in data["messages"]),
                             data["raw_response"] + f" (Parsed: {data['score']})",
                             'intention_scoring', # Use a distinct phase name for logging
                             round_number=total_resp + 1
                         )

                # Step 3: Select the Speaker
                if not intention_scores:
                    print("  Warning: No intention scores generated. Picking random agent.")
                    if not remain: # Safety check
                        print("Error: No remaining agents to pick from. Breaking.")
                        break
                    selected_agent = random.choice(remain)
                    selected_agent_name = selected_agent.name
                    max_score = "N/A"
                else:
                    max_score = max(data["score"] for data in intention_scores.values()) if intention_scores else 0
                    top_agents_names = [name for name, data in intention_scores.items() if data["score"] == max_score]
                    if not top_agents_names: # Handle case where all scores were 0 or parsing failed for all
                        print("  Warning: No agents with positive scores found. Picking randomly from remaining.")
                        if not remain: break # Break if no agents left
                        selected_agent = random.choice(remain)
                        selected_agent_name = selected_agent.name
                    else:
                        selected_agent_name = random.choice(top_agents_names)
                        selected_agent = next(agent for agent in remain if agent.name == selected_agent_name)

                print(f"  Selected Speaker: {selected_agent_name} (Score: {max_score})")

                # Step 4: Prepare selected agent's data for commit
                # Ensure the selected agent actually generated a potential response
                if selected_agent_name not in potential_responses:
                    print(f"Error: Selected agent {selected_agent_name} did not have a potential response recorded. Skipping turn.")
                    # Decide how to handle: continue to next iteration, break, etc.
                    total_resp += 1 # Avoid potential infinite loop
                    continue # Skip the commit stage for this round

                selected_data = potential_responses[selected_agent_name]
                selected_response = selected_data["response"]
                selected_messages = selected_data["messages"]
                generation_pt = selected_data["prompt_tokens"]
                generation_ct = selected_data["completion_tokens"]
                generation_rt = selected_data["reasoning_tokens"]

            else:
                # --- Original Logic (Fixed or Random) ---
                print(f"\n--- Round {total_resp + 1}: Selecting Speaker via '{disc_order}' ---")
                # Step 1: Select the Speaker using the appropriate method
                selected_agent = self._select_next_agent(remain) # Handles fixed/random based on config
                if not selected_agent: # Should not happen if remain is not empty
                     print("Error: _select_next_agent returned None. Breaking.")
                     break
                print(f"  Selected Speaker: {selected_agent.name}")
                self.conversation.current_agent = selected_agent

                # Step 2: Generate Response for the selected agent
                selected_messages = self.message_strategy.construct_messages(
                    selected_agent, 'discussion', self.conversation,
                    total_resp=total_resp, max_rounds=self.max_responses
                )

                selected_response, generation_pt, generation_ct, generation_rt = self.generate_with_retries(
                    selected_agent,
                    selected_messages
                )

                # selected_response, generation_pt, generation_ct, generation_rt = selected_agent.generate_response(selected_messages)


            # --- Commit Stage (Common for both branches) ---
            if selected_agent and selected_response is not None:
                # Add the *selected* agent's generation response to history
                # Update token usage for the *selected* agent's *generation* call
                self.conversation.update_phase_token_usage("discussion", generation_pt, generation_ct, generation_rt)

                print(f"[{disc_order}] {selected_agent.name} => {selected_response}")
                ideas_at_start_of_turn = list(self.data_strategy.current_ideas)

                # Update shared data using the *selected* response
                self.data_strategy.update_shared_data(self.conversation, selected_response)

                self.conversation.add_chat_entry(
                    selected_agent.model_name,
                    selected_agent.name,
                    "\n".join(m['content'] for m in selected_messages),
                    selected_response,
                    'discussion',
                    current_ideas=ideas_at_start_of_turn, # Log state BEFORE update
                    round_number=total_resp + 1
                )

                total_resp += 1
                if disc_order == "hand_raising":
                    if "agree: no changes needed" in selected_response.lower():
                        print(f"All agents agreed (all_at_once, order: {disc_order}).")
                        self._print_final()
                                            # Log this agreement round before exiting
                        self.conversation.add_chat_entry(
                            'system',  # Keyword doesn't match 'model_name'
                            "system",
                            'N/A (Early agreement detected in potential responses)',
                            "Final idea selection from discussion process",
                            'discussion',  # Keyword matches 'phase'
                            current_ideas=[self.data_strategy.current_ideas[0]],
                            round_number=total_resp + 1
                        )
                        return
                # Check agreement *after* the selected agent has spoken and state updated
                if self.data_strategy.all_agents_agreed(self.conversation.agents):
                    print(f"All agents agreed (all_at_once, order: {disc_order}).")
                    self._print_final()
                    return
            else:
                 # This case might happen if generation failed or selection failed unexpectedly
                 print(f"Warning: No valid response generated or agent selected in round {total_resp + 1}. Skipping round.")
                 # Increment to prevent potential infinite loop if issue persists
                 total_resp += 1

        # Loop finished (max responses reached)
        print(f"Max responses ({self.max_responses}) reached (all_at_once, order: {disc_order}) => no full agreement or discussion limit hit.")
        self._print_final()


    def discussion_one_by_one(self):
        """
        4 scenarios:
          - rating => keep leftover => next idea from leftover[0]
          - selectionTop => each round pick new first_agent => ...
        Only AUT (PS is skipped).
        """
        if self.task_config.get("task_type","AUT")!="AUT":
            print("PS + one_by_one not supported.")
            return

        sel_method= self.task_config.get("selection_method","rating")

        if sel_method=="rating":
            # Suppose we have 15 ideas in ranked_ideas.
            # We'll do 5 rounds => each round:
            # Round1 => current_ideas= [ranked_ideas[0]], replacement_ideas= [1..5], left= [6..]
            # After round, if no new replacement usage or partial usage => next round
            # set current_ideas= [ replacement_ideas[0] ] or leftover[0], depends on your logic
            # Here we do a demonstration
            self.discussion_one_by_one_rating_mode()
        else:
            self.discussion_one_by_one_selectionTop_mode()

    def discussion_one_by_one_rating_mode(self):
        """
        Example logic: 
        Round1 => current_ideas= [ranked_ideas[0]], replacement= [1..5], left= [6..]
        Round2 => new idea from leftover or from replacement leftover
        ...
        """
        ideas_list= self.data_strategy.ranked_ideas
        total_ideas= len(ideas_list)
        if total_ideas<1:
            print("No ideas for one_by_one rating.")
            return

        # Start with first idea
        # e.g. Round1
        current_idx=0
        self.data_strategy.current_idea_index= 0

        # init
        self.data_strategy.current_ideas= [ideas_list[0]]
        self.data_strategy.replacement_ideas= ideas_list[1:6]
        self.data_strategy.left= ideas_list[6:]

        round_count= 5  # we want 5 ideas total
        final_ideas = []  # track used

        for round_i in range(round_count):
            self.data_strategy.reset_agreements()
            if round_i==0:
                # use the already init
                pass
            else:
                # new round => current idea from leftover approach:
                # Step 1: Use the first idea from replacement_ideas as the current idea
                if self.data_strategy.replacement_ideas:
                    new_idea = self.data_strategy.replacement_ideas.pop(0)
                    self.data_strategy.current_ideas = [new_idea]

                # Step 2: Refill replacement_ideas from left to maintain the desired size
                desired_size = 5  # Adjust based on task requirements
                while len(self.data_strategy.replacement_ideas) < desired_size:
                    if self.data_strategy.left:
                        self.data_strategy.replacement_ideas.append(self.data_strategy.left.pop(0))
                    else:
                        print("No more leftover ideas!")
                        break

            local_res=0

            while local_res<10:
                remain= [ag for ag in self.conversation.agents if not self.data_strategy.agent_has_agreed(ag.name)]
                if not remain:
                    print(f"Round {round_i+1} => all agreed.")
                    break

                agent = self._select_next_agent(remain)

                self.conversation.current_agent= agent
                msgs= self.message_strategy.construct_messages(agent,'discussion', self.conversation, idea_index=round_i,current_round=local_res + 1, max_rounds=10)
                resp, prompt_tokens, completion_tokens, reasoning_tokens = agent.generate_response(msgs)
                self.conversation.add_chat_entry(agent.model_name, agent.name, "\n".join(m['content'] for m in msgs), resp, 'discussion', round_i,current_ideas=self.data_strategy.current_ideas)

                # Update token usage
                self.conversation.update_phase_token_usage("discussion",prompt_tokens, completion_tokens,reasoning_tokens)

                print(f"[one_by_one+rating Round {round_i+1}] {agent.name} => {resp}")
                self.data_strategy.update_shared_data(self.conversation, resp)
                local_res+=1

            print(f"End Round {round_i+1} => final idea: {self.data_strategy.current_ideas[0]}")
            final_ideas.append(self.data_strategy.current_ideas[0])

        print("One_by_one + rating done.")
        print("\n=== Final AUT ideas ===")
        for i, idea in enumerate(final_ideas, 1):
            print(f"{i}. {idea}")


    def discussion_one_by_one_selectionTop_mode(self):
        """
        Each round => we handle 1 idea from an agent's top picks.
        A. first round => no first_agent => the first who speaks becomes first_agent => use agent's picks => set current_ideas= [picks[0]]? 
        B. other agents => they have their own picks in agent_replacement_ideas => can do replace. 
        C. end of round => clear first_agent => next round => new first_agent or the same.
        """

        round_count= 5  # want 5 final ideas
        ttype= self.task_config.get("task_type","AUT")

        # Step 1: Initialize replacement_ideas for all agents
        all_txt = [x['idea'] for x in self.data_strategy.all_ideas]
        for ag in self.conversation.agents:
            if ag.name not in self.data_strategy.agent_replacement_ideas:
                idxs = self.data_strategy.agent_selected_ideas.get(ag.name, [])
                rep_list = [all_txt[i] for i in idxs if 0 <= i < len(all_txt)]
                self.data_strategy.agent_replacement_ideas[ag.name] = rep_list

        # List to store the final ideas for each round
        final_ideas = []

        for r in range(round_count):
            self.data_strategy.reset_agreements()
            self.data_strategy.current_idea_index= r
            self.data_strategy.current_ideas= []
            # For clarity, we do not unify leftover logic here. We rely on each agent's picks. 

            local_res=0
            while local_res<10:
                remain= [ag for ag in self.conversation.agents if not self.data_strategy.agent_has_agreed(ag.name)]
                if not remain:
                    print(f"[one_by_one+selectionTop] Round {r+1} => all agreed.")
                    break

                chosen = self._select_next_agent(remain)

                # if there's no first_agent => set chosen as first_agent => init current_ideas from chosen picks (the r'th pick).
                if not self.data_strategy.first_agent_name:
                    self.data_strategy.first_agent_name = chosen.name
                    first_agent_repl = self.data_strategy.agent_replacement_ideas.get(chosen.name, [])
                    if first_agent_repl:
                        current_idea = first_agent_repl.pop(0)  # Take the first idea
                        self.data_strategy.current_ideas = [current_idea]
                        self.data_strategy.agent_replacement_ideas[chosen.name] = first_agent_repl
                    else:
                        self.data_strategy.current_ideas = ["(no valid ideas)"]
                        print(f"{chosen.name} has no replacement ideas remaining.")

                # Let chosen agent speak
                self.conversation.current_agent= chosen
                msgs= self.message_strategy.construct_messages(chosen,'discussion', self.conversation, r,current_round=local_res + 1, max_rounds=self.max_responses)
                resp, prompt_tokens, completion_tokens, reasoning_tokens= chosen.generate_response(msgs)
                self.conversation.add_chat_entry(chosen.model_name, chosen.name, "\n".join(m['content'] for m in msgs), resp, 'discussion', r,current_ideas=self.data_strategy.current_ideas)

                # Update token usage
                self.conversation.update_phase_token_usage("discussion",prompt_tokens, completion_tokens,reasoning_tokens)
                print(f"[one_by_one+selectionTop Round {r+1}] {chosen.name} => {resp}")
                self.data_strategy.update_shared_data(self.conversation, resp)
                local_res+=1
            
            # Store the final idea for this round
            final_ideas.append(self.data_strategy.current_ideas[0])
            print(f"[one_by_one+selectionTop] Round {r+1} ended => final idea: {self.data_strategy.current_ideas[0]}")
            self.data_strategy.first_agent_name= None  # so next round can pick new first_agent if needed

        print("one_by_one + selectionTop completed.")
        # Print and store the final list of 5 ideas
        self.data_strategy.current_ideas = final_ideas

        print("\n=== Final AUT ideas ===")
        for i, idea in enumerate(final_ideas, 1):
            print(f"{i}. {idea}")


    def run_direct_discussion(self):
        """
        Handles the direct discussion phase.
        Supports AUT and PS tasks with either "all_at_once" or "one_by_one" methods.
        """
        print("Starting direct discussion phase.")
        self.data_strategy.first_agent_name = None  # Reset first agent tracking.

        task_type = self.task_config.get("task_type", "AUT")
        discussion_method = self.task_config.get("discussion_method", "all_at_once")

        if task_type == "AUT":
            if discussion_method == "all_at_once":
                self.direct_discussion_aut_all_at_once()
            elif discussion_method == "one_by_one":
                self.direct_discussion_aut_one_by_one()
        elif task_type == "PS":
            self.direct_discussion_ps_all_at_once()

        print("\n=== Final Token Usage Summary ===")
        print(self.conversation.get_token_summary())

    def direct_discussion_aut_all_at_once(self):
        """
        Direct discussion for AUT with all_at_once.
        """
        print("[direct_discussion_aut_all_at_once] Starting...")
        self.data_strategy.current_ideas = []  # Clear current ideas initially.
        total_resp = 0

        while total_resp < self.max_responses:      
            remain = [ag for ag in self.conversation.agents if not self.data_strategy.agent_has_agreed(ag.name)]
            if not remain:
                print("All agents agreed (AUT all_at_once direct discussion).")
                break
            agent = self._select_next_agent(remain)
            self.conversation.current_agent = agent

            msgs = self.message_strategy.construct_messages(agent, 'direct_discussion', self.conversation, total_resp=total_resp,max_rounds=self.max_responses)
            resp, prompt_tokens, completion_tokens, reasoning_tokens = agent.generate_response(msgs)
            if total_resp == 0:
                self.data_strategy.current_ideas = [resp]
            self.conversation.add_chat_entry(agent.model_name,agent.name, "\n".join(m["content"] for m in msgs), resp, "direct_discussion",current_ideas=self.data_strategy.current_ideas)

            # Update token usage
            self.conversation.update_phase_token_usage("discussion",prompt_tokens, completion_tokens,reasoning_tokens)

            print(f"[AUT all_at_once direct] {agent.name} => {resp}")

            # Update shared data
            if total_resp != 0:
                self.data_strategy.update_shared_data(self.conversation, resp)
            total_resp += 1

        print("[direct_discussion_aut_all_at_once] Completed.")

    def direct_discussion_aut_one_by_one(self):
        """
        Direct discussion for AUT with one_by_one.
        Each idea has up to 15 rounds of discussion.
        """
        print("[direct_discussion_aut_one_by_one] Starting...")
        self.data_strategy.current_ideas = []  # Clear current ideas initially.
        round_count = 5  # Number of ideas to finalize.
        max_rounds_per_idea = 15  # Maximum rounds for each idea.
        final_ideas = []  # Store finalized ideas.

        for idea_idx in range(round_count):
            self.data_strategy.reset_agreements()
            self.data_strategy.current_ideas = []  # Reset current ideas for the new idea.

            total_resp_per_idea = 0  # Reset response count for the current idea.

            while total_resp_per_idea < max_rounds_per_idea:
                remain = [
                    ag for ag in self.conversation.agents
                    if not self.data_strategy.agent_has_agreed(ag.name)
                ]
                if not remain:
                    print(f"All agents agreed for idea #{idea_idx + 1}. Moving to the next idea.")
                    break

                # Determine the next agent to respond.
                agent = self._select_next_agent(remain)
                self.conversation.current_agent = agent

                msgs = self.message_strategy.construct_messages(
                    agent, "direct_discussion", self.conversation, current_round=total_resp_per_idea + 1, idea_index = idea_idx
                )
                resp, prompt_tokens, completion_tokens, reasoning_tokens = agent.generate_response(msgs)
                if total_resp_per_idea == 0:
                    self.data_strategy.current_ideas = [resp]
                self.conversation.add_chat_entry(
                    agent.model_name, agent.name, "\n".join(m["content"] for m in msgs), resp, "direct_discussion", idea_index=idea_idx,current_ideas=self.data_strategy.current_ideas
                )

                # Update token usage.
                self.conversation.update_phase_token_usage("discussion",prompt_tokens, completion_tokens,reasoning_tokens)

                print(f"[One_by_one] Agent {agent.name} responded: {resp}")

                # Update shared data.
                if total_resp_per_idea != 0:
                    self.data_strategy.update_shared_data(self.conversation, resp)

                total_resp_per_idea += 1

            print(f"Discussion for idea #{idea_idx + 1} completed. Final idea: {self.data_strategy.current_ideas[0]}")
            final_ideas.append(self.data_strategy.current_ideas[0])

        print("\n=== Final Ideas ===")
        for i, idea in enumerate(final_ideas, 1):
            print(f"{i}. {idea}")

        print("[direct_discussion_aut_one_by_one] Completed.")


    # PS direct discussion only supports all_at_once
    def direct_discussion_ps_all_at_once(self):
        """
        Direct discussion for PS with all_at_once.
        """
        print("[direct_discussion_ps_all_at_once] Starting...")
        self.data_strategy.current_ideas = []  # Clear current ideas initially.
        total_resp = 0
        
        disc_order = self.task_config.get("discussion_order_method", "fixed")
        
        while total_resp < self.max_responses:
            # For the first round, don't check agreements - just use all agents
            if total_resp == 0:
                remain = self.conversation.agents.copy()
            else:
                remain = [ag for ag in self.conversation.agents if not self.data_strategy.agent_has_agreed(ag.name)]
                if not remain:
                    print("All agents agreed (PS all_at_once direct discussion).")
                    break
                
            # Handle different discussion order methods
            selected_agent = None
            selected_response = None
            selected_messages = None
            generation_pt, generation_ct, generation_rt = 0, 0, 0
            
            if disc_order == "hand_raising" and total_resp > 0:
                # Hand-raising logic similar to discussion_all_at_once
                # Skip hand-raising for the first round since there's no existing idea to evaluate
                print(f"\n--- Round {total_resp + 1}: Hand-Raising Protocol ---")
                
                # Step 1: Generate Potential Responses
                potential_responses = {}
                print("  Generating Potential Responses...")
                for agent in remain:
                    self.conversation.current_agent = agent
                    msgs = self.message_strategy.construct_messages(
                        agent, "direct_discussion", self.conversation, 
                        total_resp=total_resp, max_rounds=self.max_responses
                    )
                    resp, pt, ct, rt = self.generate_with_retries(agent, msgs)
                    potential_responses[agent.name] = {
                        "response": resp, "prompt_tokens": pt, "completion_tokens": ct,
                        "reasoning_tokens": rt, "messages": msgs
                    }
                
                # Step 2: Generate Intention Scores
                intention_scores = {}
                total_intention_pt, total_intention_ct, total_intention_rt = 0, 0, 0
                print("  Generating Intention Scores...")
                for agent in remain:
                    self.conversation.current_agent = agent # Context for message generation
                    agent_potential_response = potential_responses[agent.name]["response"]
                    
                    # Define the intention prompt (matching original implementation)
                    intention_prompt = TASK_REQUIREMENTS["Intention_Scoring"]
                    intention_prompt = intention_prompt.replace("{current_idea}", "\n".join(self.data_strategy.current_ideas))
                    intention_prompt = intention_prompt.replace("{agent_potential_response}", agent_potential_response)
                    
                    model = agent.model_name
                    role = (
                        "user" if model in self.task_config.get("role_assignment_in_user_prompt", [None]) else
                        "system"
                    )
                    intention_msgs = []
                    intention_msgs.append({"role": role, "content": f"# **Role**\n{agent.system_message}"})
                    if self.task_config.get("task_type","AUT")=="AUT":
                        intention_msgs.append({"role":role,"content": f"\n# **Task Requirement**\n{TASK_REQUIREMENTS['AUT_Mode1_Overall'].strip()}"})
                    else:
                        intention_msgs.append({"role":role,"content": f"\n# **Task Requirement**\n{TASK_REQUIREMENTS['PS_Overall'].strip()}"})
                    
                    intention_msgs.append({"role": 'user', "content": intention_prompt})
                    
                    score_resp, ipt, ict, irt = agent.generate_response(intention_msgs)
                    
                    # Parse the score (supports decimals, matching original)
                    score = 0.0  # Default score as float
                    try:
                        match = re.search(r'\d+(\.\d+)?', score_resp)
                        if match:
                            score = float(match.group(0))
                            score = max(1.0, min(10.0, score))  # Clamp score to range 1-10
                        else:
                            print(f"    Warning: Could not parse score from '{score_resp}' for {agent.name}. Defaulting to 0.")
                    except Exception as e:
                        print(f"    Warning: Error parsing score for {agent.name} ('{score_resp}'): {e}. Defaulting to 0.")
                    
                    intention_scores[agent.name] = {
                        "score": score, "raw_response": score_resp,
                        "messages": intention_msgs, "prompt_tokens": ipt,
                        "completion_tokens": ict, "reasoning_tokens": irt
                    }
                    # Accumulate intention token usage immediately
                    total_intention_pt += ipt
                    total_intention_ct += ict
                    total_intention_rt += irt
                
                # Update token usage for intention scoring
                self.conversation.update_phase_token_usage("discussion", total_intention_pt, total_intention_ct, total_intention_rt)
                
                # Log intention scoring results
                for name, data in intention_scores.items():
                    agent_obj = next((ag for ag in remain if ag.name == name), None)
                    if agent_obj:
                        self.conversation.add_chat_entry(
                            agent_obj.model_name, name,
                            "\n".join(m['content'] for m in data["messages"]),
                            data["raw_response"] + f" (Parsed: {data['score']})",
                            'intention_scoring',
                            round_number=total_resp + 1
                        )
                
                # Step 3: Select the Speaker
                if not intention_scores:
                    print("  Warning: No intention scores generated. Picking random agent.")
                    selected_agent = random.choice(remain) if remain else None
                    max_score = "N/A"
                else:
                    max_score = max(data["score"] for data in intention_scores.values()) if intention_scores else 0
                    top_agents_names = [name for name, data in intention_scores.items() if data["score"] == max_score]
                    if not top_agents_names:
                        print("  Warning: No agents with positive scores found. Picking randomly from remaining.")
                        selected_agent = random.choice(remain) if remain else None
                        selected_agent_name = selected_agent.name if selected_agent else None
                    else:
                        selected_agent_name = random.choice(top_agents_names)
                        selected_agent = next(agent for agent in remain if agent.name == selected_agent_name)
                
                if selected_agent:
                    print(f"  Selected Speaker: {selected_agent.name} (Score: {max_score})")
                    
                    # Step 4: Prepare selected agent's data for commit
                    if selected_agent.name in potential_responses:
                        selected_data = potential_responses[selected_agent.name]
                        selected_response = selected_data["response"]
                        selected_messages = selected_data["messages"]
                        generation_pt = selected_data["prompt_tokens"]
                        generation_ct = selected_data["completion_tokens"]
                        generation_rt = selected_data["reasoning_tokens"]
                    else:
                        print(f"Error: Selected agent {selected_agent.name} did not have a potential response recorded. Skipping turn.")
                        total_resp += 1
                        continue
                        
            else:
                # Original logic for fixed/random (or hand_raising on first round)
                if disc_order == "hand_raising" and total_resp == 0:
                    # For the first round of hand_raising, just pick a random agent
                    selected_agent = random.choice(remain) if remain else None
                    print(f"\n--- Round {total_resp + 1}: First Round (Random Selection) ---")
                    if selected_agent:
                        print(f"  Selected Speaker: {selected_agent.name} (First round - random)")
                else:
                    # Normal fixed/random selection
                    selected_agent = self._select_next_agent(remain)
                    
                if not selected_agent:
                    print("Error: _select_next_agent returned None. Breaking.")
                    break
                    
                self.conversation.current_agent = selected_agent
                selected_messages = self.message_strategy.construct_messages(
                    selected_agent, "direct_discussion", self.conversation, 
                    total_resp=total_resp, max_rounds=self.max_responses
                )
                selected_response, generation_pt, generation_ct, generation_rt = selected_agent.generate_response(selected_messages)
            
            # Commit stage (common for both branches)
            if selected_agent and selected_response is not None:
                if total_resp == 0:
                    self.data_strategy.current_ideas = [selected_response]
                    
                self.conversation.add_chat_entry(
                    selected_agent.model_name, selected_agent.name, 
                    "\n".join(m["content"] for m in selected_messages), 
                    selected_response, "direct_discussion",
                    current_ideas=self.data_strategy.current_ideas,
                    round_number=total_resp+1
                )
                
                if total_resp != 0:
                    self.data_strategy.update_shared_data(self.conversation, selected_response)
                    
                self.conversation.update_phase_token_usage("discussion", generation_pt, generation_ct, generation_rt)
                
                print(f"[PS all_at_once direct] {selected_agent.name} => {selected_response}")
                total_resp += 1
            else:
                print(f"Warning: No valid response generated or agent selected in round {total_resp + 1}. Skipping round.")
                total_resp += 1
                
        print("[direct_discussion_ps_all_at_once] Completed.")


    def _print_final(self):
        ttype= self.task_config.get("task_type","AUT")
        if ttype=="AUT":
            print("\n=== Final AUT ideas ===")
            for i, idea in enumerate(self.data_strategy.current_ideas, 1):
                print(f"{i}. {idea}")
        else:
            print("\n=== Final PS ideas ===")
            for i, sol in enumerate(self.data_strategy.current_ideas, 1):
                print(f"{i}. {sol}")

    def _select_agent_by_intention(self, candidates):
        """
        Collects intention scores from candidates and selects the agent with the highest score.
        """
        print("\n=== Select agents ===")
        for agent in candidates:
            self.conversation.current_agent = agent
            msgs = self.message_strategy.construct_messages(agent, "discussion", self.conversation, include_intention_prompt=True)
            resp, prompt_tokens, completion_tokens,reasoning_tokens = agent.generate_response(msgs)

            try:
                self.data_strategy.collect_intention_score(agent.name, resp)
                self.conversation.add_chat_entry(agent.model_name, agent.name, "\n".join(m["content"] for m in msgs), resp, "intention_score")
                self.conversation.update_phase_token_usage("discussion",prompt_tokens, completion_tokens,reasoning_tokens)
            except ValueError:
                print(f"Invalid score '{resp}' from {agent.name}. Defaulting to 0.")
                self.data_strategy.collect_intention_score(agent.name, 0)

        # Get the agent with the highest score
        selected_agent = self.data_strategy.get_highest_intention_agent(candidates)
        print(f"Selected {selected_agent.name} with the highest intention score.")
        return selected_agent

    def _select_next_agent(self, remain):
        """
        Selects the next agent based on 'fixed' or 'random' order.
        Handles the round-robin ('fixed') or random choice.
        Does NOT handle 'hand_raising'.
        """
        disc_order = self.task_config.get("discussion_order_method", "fixed")

        if not remain:
             print("Warning: _select_next_agent called with no remaining agents.")
             return None # No agent to select

        if disc_order == "random":
            # print("DEBUG: Selecting next agent randomly")
            return random.choice(remain)
        elif disc_order == "fixed":
            # print("DEBUG: Selecting next agent via fixed order")
            agents = self.conversation.agents
            current_agent = self.conversation.current_agent
            # Find start index robustly
            start_index = -1
            if current_agent:
                try:
                    start_index = agents.index(current_agent)
                except ValueError:
                    # This can happen if current_agent was from a previous phase or dynamically added/removed
                    print(f"Warning: current_agent {current_agent.name} not found in agents list for fixed order. Resetting index.")
                    start_index = -1 # Fallback to start from beginning

            # Iterate through agents in fixed order, starting after current
            for i in range(1, len(agents) + 1):
                next_index = (start_index + i) % len(agents)
                # Check if the agent at the next index is in the 'remain' list
                if agents[next_index] in remain:
                    return agents[next_index]

            # Fallback: Should only happen if 'remain' has agents not in the original 'self.conversation.agents' list,
            # or if there's a logic error.
            print(f"Warning: Fixed order selection failed to find a valid agent in 'remain'. Falling back to random choice from 'remain'.")
            return random.choice(remain)
        else:
            # If discussion_order_method is 'hand_raising' or unsupported, this function shouldn't be called
            # by discussion_all_at_once's non-hand-raising branch. Log error and default.
            print(f"Error: _select_next_agent called with unsupported order '{disc_order}'. Falling back to random choice from 'remain'.")
            return random.choice(remain)