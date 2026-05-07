# data_strategies.py

import re
import json
import logging
from pydantic import BaseModel
from openai import OpenAI
from typing import List
from utils import calculate_tokens
from azure_model_service import AzureModelService
import sys

logging.basicConfig(
    filename='data_discussion.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)
class GenericDataStrategy:
    def __init__(self, task_config):
        self.task_config = task_config
        self.intention_scores = {}

        # For AUT/PS
        self.all_ideas = []                 # [{'idea': str, 'agent': str}, ...]
        self.idea_scores = {}               # { idea_text: [scores] }
        self.ranked_ideas = []              # sorted by average

        # Discussion-time common
        self.current_ideas = []             # For all_at_once or one_by_one
        self.replacement_ideas = []         # For rating scenario (shared), or selectionTop scenario if you prefer
        self.left = []                      # leftover pool, used if we want to keep replacements at a certain size
        self.replaced_ideas = []
        # For selectionTop:
        self.agent_selected_ideas = {}      # {agent_name: [ idx1, idx2 ... ] or direct text}

        # agent_replacement_ideas: optional per-agent. We can do a dict if we want each agent own picks
        self.agent_replacement_ideas = {}   # {agent_name: [ "idea text", ... ] }

        # Agreement sets
        self.agreed_agents = set()          # For all_at_once (AUT)
        self.agreed_agents_per_idea = {}    # For one_by_one (AUT)
        self.agreed_agents_ps = set()       # For PS

        self.current_idea_index = 0
        self.first_agent_name = None

        self.model_service = AzureModelService()


    # ------------------ Idea Generation ------------------
    def collect_ideas(self, agent_name, agent_response):
        lines = self._extract_lines(agent_response)
        # This part remains the same
        for l in lines:
            self.all_ideas.append({'idea': l, 'agent': agent_name})

    def _extract_lines(self, text):
        """
        Extracts each non-empty line from the text as a separate item.
        """
        results = []
        # Split the text into lines
        for line in text.strip().split('\n'):
            # Remove leading/trailing whitespace
            stripped_line = line.strip()
            # If the line has content after stripping, add it to results
            if stripped_line:
                results.append(stripped_line)
        return results



    # ------------------ Selection Phase ------------------
    def collect_scores(self, agent_name, agent_response):
        scores_map= self._parse_rating_scores(agent_response)
        ttype= self.task_config.get("task_type","AUT")

        for idx, sc in scores_map.items():
            if 0<=idx<len(self.all_ideas):
                txt= self.all_ideas[idx]['idea']
                if txt not in self.idea_scores:
                    self.idea_scores[txt] = []
                self.idea_scores[txt].append(sc)

    def _parse_rating_scores(self, text):
        """
        parse 'Idea X: Y' or 'Solution X: Y' => { (X-1): Y }
        """
        pattern = r'(?:Idea\s*)?(\d+)[\s:\-]+(\d+)'
        out={}
        for line in text.split('\n'):
            line=line.strip()
            match= re.search(pattern, line, re.IGNORECASE)
            if match:
                idx= int(match.group(1))-1
                sc= int(match.group(2))
                out[idx]= sc
        return out

    def calculate_rankings_by_average(self,conversation):
        """
        Calculate average scores for each idea, rank them in descending order, 
        and add the process to the chat history.
        """
        try:
            items = []
            for txt, sc_list in self.idea_scores.items():
                avg = sum(sc_list) / len(sc_list)
                items.append((txt, avg))
            
            # Sort items by average score in descending order
            items.sort(key=lambda x: x[1], reverse=True)
            self.ranked_ideas = [x[0] for x in items]

            # Log and record the process
            rank_summary = "\n".join(
                [f"Rank {i+1}: {idea} (Avg Score: {avg:.2f})" for i, (idea, avg) in enumerate(items)]
            )
            conversation.add_chat_entry(
                model_name="System",
                agent_name='System',
                prompt="Ranking ideas based on average scores.",
                response=f"Ranked Ideas:\n{rank_summary}",
                phase="other",
            )
            print(f"Ranked Ideas:\n{rank_summary}")
        except Exception as e:
            logging.error("Error calculating rankings by average: %s", e)
            raise

    def collect_selections(self, agent_name, agent_response):
        lines= agent_response.strip().split('\n')
        idxs=[]
        for line in lines:
            line=line.strip()
            match= re.match(r'^\s*(?:\d+\.)?\s*(?:Idea)?\s*(\d+)[\s:.-]*', line, re.IGNORECASE)
            if match:
                i= int(match.group(1))-1
                idxs.append(i)
        ttype= self.task_config.get("task_type","AUT")
        if ttype=="AUT":
            idxs= idxs[:5]
        else:
            idxs= idxs[:3]
        self.agent_selected_ideas[agent_name]= idxs
        print(agent_name, self.agent_selected_ideas)
        print("")

    # ------------------ Discussion / Agreement ------------------
    def reset_agreements(self):
        ttype= self.task_config.get("task_type","AUT")
        dmethod= self.task_config.get("discussion_method","all_at_once")
        if ttype=="AUT":
            if dmethod=="all_at_once":
                self.agreed_agents= set()
            else:
                idx= self.current_idea_index
                self.agreed_agents_per_idea[idx]= set()
        else:
            self.agreed_agents_ps= set()

    def agent_has_agreed(self, agent_name):
        ttype= self.task_config.get("task_type","AUT")
        dmethod= self.task_config.get("discussion_method","all_at_once")
        if ttype=="AUT":
            if dmethod=="all_at_once":
                return agent_name in self.agreed_agents
            else:
                idx= self.current_idea_index
                return agent_name in self.agreed_agents_per_idea.get(idx, set())
        else:
            return agent_name in self.agreed_agents_ps
    
    def _set_agent_agreed(self, agent_name):
        ttype= self.task_config.get("task_type","AUT")
        dmethod= self.task_config.get("discussion_method","all_at_once")
        if ttype=="AUT":
            if dmethod=="all_at_once":
                self.agreed_agents.add(agent_name)
            else:
                idx= self.current_idea_index
                if idx not in self.agreed_agents_per_idea:
                    self.agreed_agents_per_idea[idx] = set()
                self.agreed_agents_per_idea[idx].add(agent_name)
        else:
            self.agreed_agents_ps.add(agent_name)

    def all_agents_agreed(self, agents):
        ttype= self.task_config.get("task_type","AUT")
        dmethod= self.task_config.get("discussion_method","all_at_once")
        if ttype=="AUT":
            if dmethod=="all_at_once":
                return len(self.agreed_agents)== len(agents)
            else:
                idx= self.current_idea_index
                return len(self.agreed_agents_per_idea.get(idx, set()))== len(agents)
        else:
            return len(self.agreed_agents_ps)== len(agents)

    def update_shared_data(self, conversation, agent_response):

        agent_name= conversation.current_agent.name

        # 1) use GPT to interprete agent_response =>  "If_agree", "current_ideas", "replacement_ideas"
        # Call the parsing function
        parse_result, prompt_tokens, completion_tokens,reasoning_tokens = self._parse_agent_response_with_gpt(agent_response, agent_name)
        print("parse_result", parse_result)
        # Update token usage in the conversation
        conversation.update_phase_token_usage("other",prompt_tokens, completion_tokens,reasoning_tokens)

        # 2) if parse_result["If_agree"] == True => self._set_agent_agreed
        action_type = parse_result.action_type
        self.current_ideas = parse_result.current_ideas
        replaced_ideas = parse_result.replaced_ideas

        # Append replaced idea if applicable
        if action_type == "replace" and replaced_ideas:
            self.replaced_ideas.append(replaced_ideas)
            print(self.replaced_ideas)

        # Phases-specific logic
        phases = self.task_config.get("phases", "three_stage")
        if phases == "direct_discussion":
            # For direct_discussion, only update current_ideas; replacement_ideas are not relevant
            if action_type == "agree":
                self._set_agent_agreed(agent_name)
            elif action_type in {"modify", "replace", "adjust"}:
                print(f"Agent {agent_name} chose to {action_type} ideas.")
                self.reset_agreements()

        else:
            if action_type == "agree":
                self._set_agent_agreed(agent_name)
            elif action_type in {"modify", "replace","adjust"}:

                print(f"Agent {agent_name} chose to {action_type} ideas.")
                self.reset_agreements()
                sel_method = self.task_config.get("selection_method", "rating")
                if sel_method == "selectionTop":
                    self.agent_replacement_ideas[agent_name] = parse_result.replacement_ideas
                
                else:
                    self.replacement_ideas = parse_result.replacement_ideas
                    ttype = self.task_config.get("task_type", "AUT")
                    if ttype == "AUT":
                        desired_size = 5
                    else:
                        # PS branch: use config option (default: 3)
                        desired_size = self.task_config.get("replacement_pool_size", 3)
                    if len(self.replacement_ideas) < desired_size and self.left:
                        gap = desired_size - len(self.replacement_ideas)
                        for _ in range(gap):
                            if self.left:
                                self.replacement_ideas.append(self.left[0])
                                self.left.pop(0)


    
    def _parse_agent_response_with_gpt(self, agent_response, agent_name):
        """
        Parses the agent's response, adapting to the discussion method.
        """
        ttype= self.task_config.get("task_type","AUT")
        phases = self.task_config.get("phases", "three_stage")

        if phases == 'three_stage':
            if ttype=="AUT":
                discussion_method = self.task_config.get("discussion_method", "one_by_one")
        
                if discussion_method == "one_by_one":
                    return self._parse_one_by_one_response(agent_response, agent_name)
                elif discussion_method == "all_at_once":
                    return self._parse_all_at_once_response(agent_response, agent_name)
                else:
                    raise ValueError(f"Unsupported discussion method: {discussion_method}")
            else:
                return self._parse_one_by_one_response(agent_response, agent_name)
        
        elif phases == "direct_discussion":
            discussion_method = self.task_config.get("discussion_method", "all_at_once")
            if ttype == 'AUT':
                if discussion_method == "all_at_once":
                    return self._parse_direct_all_at_once_response(agent_response, agent_name)
                elif discussion_method == "one_by_one":
                    return self._parse_direct_one_by_one_response(agent_response, agent_name)
            elif ttype == 'PS':
                return self._parse_one_by_one_response(agent_response, agent_name)
            else:
                raise ValueError(f"Unsupported discussion method for direct_discussion: {discussion_method}")

    def _parse_one_by_one_response(self, agent_response, agent_name):
        """
        Manual parsing approach that doesn't depend on LLM.
        Preserves the same interface and output format as the original function.
        """
        # 1) Figure out which replacement pool to display (same as original)
        sel_method = self.task_config.get("selection_method", "rating")
        if sel_method == "rating":
            rep_list = self.replacement_ideas
        else:
            rep_list = self.agent_replacement_ideas.get(agent_name, [])

        # Default response structure (for "agree" case or fallback)
        result = {
            "action_type": "agree",
            "current_ideas": self.current_ideas.copy(),
            "replacement_ideas": rep_list.copy(),
            "replaced_ideas": None
        }

        # Parse the agent's response to determine action_type
        response_lines = agent_response.strip().split('\n')
        first_line = response_lines[0].strip() if response_lines else ""

        # Helper function to extract the idea, trimming off "- Reason:" and everything after it
        def extract_idea(text):
            if "- Reason:" in text:
                return text.split("- Reason:")[0].strip()
            elif " - Reason:" in text:
                return text.split(" - Reason:")[0].strip()
            # Also handle **Reason:** format (for DeepSeek compatibility)
            elif "**Reason:**" in text:
                return text.split("**Reason:**")[0].strip()
            return text.strip()

        # Find action keywords anywhere in the response (not just first line)
        # This handles cases where DeepSeek adds introductory text before the action
        action_line = None
        action_type_found = None
        
        for line in response_lines:
            line_stripped = line.strip()
            if line_stripped.startswith("Agree:") or line_stripped.startswith("**Agree:**"):
                action_line = line_stripped
                action_type_found = "agree"
                break
            elif line_stripped.startswith("Modify:") or line_stripped.startswith("**Modify:**"):
                action_line = line_stripped
                action_type_found = "modify"
                break
            elif line_stripped.startswith("Replace:") or line_stripped.startswith("**Replace:**"):
                action_line = line_stripped
                action_type_found = "replace"
                break

        # Check for explicit prefixes in the first line (handle both regular and **bold** formats)
        if action_type_found == "agree":
            # Do nothing for "agree" as default values are already set
            pass

        elif action_type_found == "modify":
            # Extract the modified idea (everything after "Modify:" or "**Modify:**" but before "- Reason:")
            if action_line.startswith("**Modify:**"):
                modified_idea = extract_idea(action_line[len("**Modify:**"):].strip())
            else:
                modified_idea = extract_idea(action_line[len("Modify:"):].strip())

            # If there's no content after "Modify:", try to extract from subsequent lines
            if not modified_idea and len(response_lines) > 1:
                for line in response_lines[1:]:
                    if line.strip() and not line.startswith("Reason:") and not line.startswith("**Reason:**"):
                        modified_idea = extract_idea(line.strip())
                        break

            if modified_idea:
                result["action_type"] = "modify"
                result["current_ideas"] = [modified_idea]

        elif action_type_found == "replace":
            # Extract the replacement idea (everything after "Replace:" or "**Replace:**" but before "- Reason:")
            if action_line.startswith("**Replace:**"):
                replacement_idea = extract_idea(action_line[len("**Replace:**"):].strip())
            else:
                replacement_idea = extract_idea(action_line[len("Replace:"):].strip())

            # If there's no content after "Replace:", try to extract from subsequent lines
            if not replacement_idea and len(response_lines) > 1:
                for line in response_lines[1:]:
                    if line.strip() and not line.startswith("Reason:") and not line.startswith("**Reason:**"):
                        replacement_idea = extract_idea(line.strip())
                        break

            if replacement_idea:
                # Check if the replacement idea matches any in rep_list
                match_found = False
                for idx, idea in enumerate(rep_list):
                    if replacement_idea.strip() == idea.strip():
                        match_found = True

                        # Set action_type to replace
                        result["action_type"] = "replace"

                        # Update current_ideas with the replacement
                        result["current_ideas"] = [idea]

                        # Store the replaced idea
                        replaced_idea = self.current_ideas[0] if self.current_ideas else None
                        result["replaced_ideas"] = replaced_idea

                        # Update replacement_ideas by removing the used idea
                        updated_rep_list = rep_list.copy()
                        updated_rep_list.pop(idx)
                        result["replacement_ideas"] = updated_rep_list
                        break

                # If no match found in replacement pool, use as-is
                if not match_found:
                    result["action_type"] = "replace"
                    result["current_ideas"] = [replacement_idea]
                    result["replaced_ideas"] = self.current_ideas[0] if self.current_ideas else None

        # Create a mock response object with the same structure as the original function
        class MockAgentResponse:
            def __init__(self, data):
                self.action_type = data["action_type"]
                self.current_ideas = data["current_ideas"]
                self.replacement_ideas = data["replacement_ideas"]
                self.replaced_ideas = data["replaced_ideas"]

        mock_response = MockAgentResponse(result)

        # Return the structure expected by the calling function
        return mock_response, 0, 0, 0  # Object, prompt_tokens, completion_tokens, reasoning_tokens    # def _parse_one_by_one_response(self, agent_response, agent_name):


    def _parse_one_by_one_response_validate(self, agent_response, agent_name):
        """
        Manual parsing approach that doesn't depend on LLM.
        Preserves the same interface and output format as the original function.
        """
        # 1) Figure out which replacement pool to display (same as original)
        sel_method = self.task_config.get("selection_method", "rating")
        if sel_method == "rating":
            rep_list = self.replacement_ideas
        else:
            rep_list = self.agent_replacement_ideas.get(agent_name, [])

        # Default response structure (for "agree" case or fallback)
        result = {
            "action_type": "agree",
            "current_ideas": self.current_ideas.copy(),
            "replacement_ideas": rep_list.copy(),
            "replaced_ideas": None
        }

        # Parse the agent's response to determine action_type
        response_lines = agent_response.strip().split('\n')
        first_line = response_lines[0].strip() if response_lines else ""

        # Helper function to extract the idea, trimming off "- Reason:" and everything after it
        def extract_idea(text):
            if "- Reason:" in text:
                return text.split("- Reason:")[0].strip()
            elif " - Reason:" in text:
                return text.split(" - Reason:")[0].strip()
            # Also handle **Reason:** format (for DeepSeek compatibility)
            elif "**Reason:**" in text:
                return text.split("**Reason:**")[0].strip()
            return text.strip()

        # Find action keywords anywhere in the response (not just first line)
        # This handles cases where DeepSeek adds introductory text before the action
        action_line = None
        action_type_found = None
        
        for line in response_lines:
            line_stripped = line.strip()
            if line_stripped.startswith("Agree:") or line_stripped.startswith("**Agree:**"):
                action_line = line_stripped
                action_type_found = "agree"
                break
            elif line_stripped.startswith("Modify:") or line_stripped.startswith("**Modify:**"):
                action_line = line_stripped
                action_type_found = "modify"
                break
            elif line_stripped.startswith("Replace:") or line_stripped.startswith("**Replace:**"):
                action_line = line_stripped
                action_type_found = "replace"
                break

        # Check for explicit prefixes in the first line (handle both regular and **bold** formats)
        if action_type_found == "agree":
            # Do nothing for "agree" as default values are already set
            pass

        elif action_type_found == "modify":
            # Extract the modified idea (everything after "Modify:" or "**Modify:**" but before "- Reason:")
            if action_line.startswith("**Modify:**"):
                modified_idea = extract_idea(action_line[len("**Modify:**"):].strip())
            else:
                modified_idea = extract_idea(action_line[len("Modify:"):].strip())

            # If there's no content after "Modify:", try to extract from subsequent lines
            if not modified_idea and len(response_lines) > 1:
                for line in response_lines[1:]:
                    if line.strip() and not line.startswith("Reason:") and not line.startswith("**Reason:**"):
                        modified_idea = extract_idea(line.strip())
                        break

            if modified_idea:
                result["action_type"] = "modify"
                result["current_ideas"] = [modified_idea]

        elif action_type_found == "replace":
            # Extract the replacement idea (everything after "Replace:" or "**Replace:**" but before "- Reason:")
            if action_line.startswith("**Replace:**"):
                replacement_idea = extract_idea(action_line[len("**Replace:**"):].strip())
            else:
                replacement_idea = extract_idea(action_line[len("Replace:"):].strip())

            # If there's no content after "Replace:", try to extract from subsequent lines
            if not replacement_idea and len(response_lines) > 1:
                for line in response_lines[1:]:
                    if line.strip() and not line.startswith("Reason:") and not line.startswith("**Reason:**"):
                        replacement_idea = extract_idea(line.strip())
                        break

            if replacement_idea:
                # Only allow replacement if the idea is in the pool and pool is not empty
                logging.info(f"PRE-CHECK: Agent {agent_name} replacement idea: {replacement_idea}")
                logging.info(f"PRE-CHECK: Updated replacement idea pool: {rep_list}")
                condition_met = rep_list and replacement_idea.strip() in [idea.strip() for idea in rep_list]
                logging.info(f"DEBUG: Condition evaluated to: {condition_met}")

                if not rep_list or replacement_idea.strip() in [idea.strip() for idea in rep_list]:
                    logging.info(
                        f"CONDITION MET: Agent {agent_name} replacement idea valid (empty pool or found in pool).")
                    logging.info(f"CONDITION MET: replacement_idea was: {replacement_idea}")

                    result["action_type"] = "replace"
                    result["current_ideas"] = [replacement_idea]
                    replaced_idea = self.current_ideas[0] if self.current_ideas else None
                    result["replaced_ideas"] = replaced_idea

                    if rep_list:
                        try:
                            idx = [idea.strip() for idea in rep_list].index(replacement_idea.strip())
                            logging.info(f"CONDITION MET: Found at index {idx} with value: {rep_list[idx]}")
                            updated_rep_list = rep_list.copy()
                            updated_rep_list.pop(idx)
                            result["replacement_ideas"] = updated_rep_list
                        except ValueError:
                            logging.info(f"CONDITION MET: Idea not in list, but empty pool allowed.")
                            result["replacement_ideas"] = rep_list.copy()
                    else:
                        logging.info(f"CONDITION MET: Empty replacement pool, any replacement allowed.")
                        result["replacement_ideas"] = []
                else:
                    logging.info(f"CONDITION NOT MET: Agent {agent_name} replacement idea NOT found in pool.")
                    logging.info(f"CONDITION NOT MET: replacement_idea was: {replacement_idea}")

                    # If not in pool, treat as invalid: return None to signal regeneration
                    return None, 0, 0, 0
        else:
            return None, 0, 0, 0
        # Create a mock response object with the same structure as the original function
        class MockAgentResponse:
            def __init__(self, data):
                self.action_type = data["action_type"]
                self.current_ideas = data["current_ideas"]
                self.replacement_ideas = data["replacement_ideas"]
                self.replaced_ideas = data["replaced_ideas"]

        mock_response = MockAgentResponse(result)

        # Return the structure expected by the calling function
        return mock_response, 0, 0, 0  # Object, prompt_tokens, completion_tokens, reasoning_tokens    # def _parse_one_by_one_response(self, agent_response, agent_name):


    #     """
    #     GPT + pydantic parse approach => we must provide current_ideas, replacement_ideas, agent_name in the prompt.
    #     """
    #     class AgentResponse(BaseModel):
    #         action_type: str  # "agree", "modify", or "replace"
    #         current_ideas: List[str]
    #         replacement_ideas: List[str]
    #         replaced_ideas: str = None
    #
    #     # 1) figure out which replacement pool to display:
    #     sel_method = self.task_config.get("selection_method", "rating")
    #     if sel_method == "rating":
    #         # Shared
    #         rep_list = self.replacement_ideas
    #     else:
    #         # selectionTop => each agent has their own replacement pool
    #         # if not exist => fallback empty
    #         rep_list = self.agent_replacement_ideas.get(agent_name, [])
    #
    #     # 2) build the strings
    #     current_str = "\n".join(f"- {idea}" for idea in self.current_ideas)
    #     replacement_str = "\n".join(f"- {idea}" for idea in rep_list)
    #
    #     system_msg_one_by_one = f"""Here is the current list of ideas:
    #     {current_str if current_str else "(none)"}
    #
    #     Here is the replacement ideas list:
    #     {replacement_str if replacement_str else "(none)"}
    #
    #     Based on the agent's response, judge whether the agent:
    #     - **Agrees** with the current ideas without suggesting any changes. The agent explicitly says "Agree:..."
    #     - **Modifies** any of the current ideas. The agent explicitly says "Modify:..."
    #     - **Replaces** any of the current ideas with one from the replacement pool. The agent explicitly says "Replace:..."
    #
    #     For each action, the agent must ensure that the lists reflect the following updates:
    #
    #     1. **Agree**:
    #         - If the agent agrees, the `current_ideas` remain unchanged.
    #         - The `replacement_ideas` list also remains unchanged.
    #
    #     2. **Modify**:
    #         - If the agent modifies an idea, update the `current_ideas` list with the modified version of the idea.
    #         - The `replacement_ideas` list remains unchanged.
    #
    #     3. **Replace**:
    #         - If the agent replaces an idea:
    #             - Update the `current_ideas` list by the agent's newly proposed idea, VERBATIM.
    #             - Remove the selected replacement idea from the `replacement_ideas` list. Skip if there is no replacement idea.
    #             - Move the replaced idea to the `replaced_ideas` list by appending this list.
    #
    #     **Important**:
    #         - The `current_ideas` list must only include **one idea**. If the agent modifies or replaces an idea, ensure that the `current_ideas` list reflects this change.
    #         - The `replacement_ideas` list must reflect the updated pool after any replacements.
    #         - The `replaced_ideas` list must include the replaced idea(s) for record-keeping.
    #         - You MUST preserve the VERBATIM original text and formatting of all idea strings in the output.
    #
    #     Note that you should not include any reasoning from the raw agent response in the output.
    #     The expected output JSON structure should detail the action taken, the updated list of current ideas (only include one idea), an updated list of replacement ideas and an updated list of replaced ideas, all must in full and not shortened:
    #     {{
    #         "action_type": "agree/modify/replace",
    #         "current_ideas": [],
    #         "replacement_ideas": [],
    #         "replaced_ideas": [],
    #     }}
    #     """.strip()
    #
    #
    #
    #
    #
    #     messages = [
    #         {"role": "system", "content": system_msg_one_by_one},
    #         {"role": "user", "content": agent_response}
    #     ]
    #
    #     return self._call_gpt_and_parse(messages, AgentResponse)

#     def _parse_one_by_one_response(self, agent_response, agent_name):
#         """
#         GPT + pydantic parse approach => we must provide current_ideas,
#         replacement_ideas, existing replaced_ideas, and agent_name in the prompt.
#         """
#         class AgentResponse(BaseModel):
#             action_type: str
#             current_ideas: List[str]
#             replacement_ideas: List[str]
#             # Changed to List[str] to store cumulative replaced ideas
#             replaced_ideas: List[str]

#         # 1) Figure out which replacement pool to display:
#         sel_method = self.task_config.get("selection_method", "rating")
#         if sel_method == "rating":
#             rep_list = self.replacement_ideas
#         else:
#             rep_list = self.agent_replacement_ideas.get(agent_name, [])

#         # 2) Build the strings for context
#         current_idea_text = self.current_ideas[0] if self.current_ideas else "(No current idea provided)"
#         replacement_context_text = "\n".join(f"- {idea}" for idea in rep_list) if rep_list else "(No replacement ideas available)"
#         # Get the *current* list of already replaced ideas from the strategy state
#         existing_replaced_ideas_list = self.replaced_ideas if hasattr(self, 'replaced_ideas') else []
#         existing_replaced_context_text = "\n".join(f"- {idea}" for idea in existing_replaced_ideas_list) if existing_replaced_ideas_list else "(None yet)"

#         # Create JSON representations for use *within* the prompt's example outputs
#         replacement_json_list_str = json.dumps(rep_list)
#         existing_replaced_json_list_str = json.dumps(existing_replaced_ideas_list) # JSON list of existing replaced ideas

#         # --- System Prompt Modified for Cumulative replaced_ideas ---
#         system_msg_one_by_one = f"""You are a precise parser analyzing an agent's response to update a conversation state.

# **Context:**
# Current Idea:
# - {current_idea_text}

# Available Replacement Ideas Pool:
# {replacement_context_text}

# History of Previously Replaced Ideas:
# {existing_replaced_context_text}

# **Your Task:**
# Analyze the agent's response provided by the user. Determine the agent's action and update the state according to the following strict rules. Output *only* the final JSON object.

# **Rules & Processing Steps:**

# 1.  **Identify Action Prefix:** Check if the agent's response STARTS EXACTLY with "Agree:", "Modify:", or "Replace:".
#     *   **If no exact prefix is found:** Assume the action is "agree". Proceed to step 2.
#     *   **If a prefix is found:** Proceed to the corresponding step (2, 3, or 4).

# 2.  **Action: Agree**
#     *   Condition: Agent response starts with "Agree:" OR no valid prefix was found.
#     *   Output JSON:
#         ```json
#         {{
#             "action_type": "agree",
#             "current_ideas": ["{current_idea_text}"],
#             "replacement_ideas": {replacement_json_list_str},
#             "replaced_ideas": {existing_replaced_json_list_str}
#         }}
#         ```
#     *   Note: Use EXACT original texts. `replaced_ideas` is the *unchanged* historical list from the context.

# 3.  **Action: Modify**
#     *   Condition: Agent response starts with "Modify:".
#     *   Processing: Extract the *complete, verbatim* text of the modified idea following "Modify:". Discard reasoning.
#     *   Output JSON:
#         ```json
#         {{
#             "action_type": "modify",
#             "current_ideas": ["<EXTRACTED_MODIFIED_IDEA_TEXT_VERBATIM>"],
#             "replacement_ideas": {replacement_json_list_str},
#             "replaced_ideas": {existing_replaced_json_list_str}
#         }}
#         ```
#     *   Note: `current_ideas` contains the *full modified text*. `replacement_ideas` and `replaced_ideas` remain unchanged from the context.

# 4.  **Action: Replace**
#     *   Condition: Agent response starts with "Replace:".
#     *   Processing:
#         a.  Extract the *complete, verbatim* text of the proposed replacement idea following "Replace:". Discard reasoning. Let's call this `extracted_replacement_text`.
#         b.  **CRITICAL VALIDATION:** Check if `extracted_replacement_text` EXACTLY MATCHES any idea in the `Available Replacement Ideas Pool` listed in the Context section above.
#         c.  **If EXACT MATCH FOUND:**
#             i.  The matched idea text is `extracted_replacement_text`.
#             ii. Create the `updated_replacement_pool_list` by removing `extracted_replacement_text` from the original pool.
#             iii. Create the `updated_replaced_ideas_list` by taking the `History of Previously Replaced Ideas` list from the Context and **appending** the original `Current Idea` (`{current_idea_text}`) to it.
#             iv. Output JSON:
#                 ```json
#                 {{
#                     "action_type": "replace",
#                     "current_ideas": ["<EXTRACTED_REPLACEMENT_TEXT_VERBATIM>"],
#                     "replacement_ideas": <JSON_REPRESENTATION_OF_updated_replacement_pool_list>,
#                     "replaced_ideas": <JSON_REPRESENTATION_OF_updated_replaced_ideas_list>
#                 }}
#                 ```
#                 (Replace placeholders `<...>` with actual derived values. Ensure `replacement_ideas` and `replaced_ideas` are valid JSON lists containing the full verbatim text).
#         d.  **If NO EXACT MATCH FOUND:** The agent failed instruction. Treat as "agree". Output JSON as specified in Step 2.

# **Output Requirements:**
# - Output ONLY the JSON object. Do not include any explanatory text.
# - Ensure all idea text in the JSON is full, verbatim text. Do not shorten, summarize, or include reasoning.
# - `current_ideas` must contain exactly one string item.
# - `replacement_ideas` must be a list of strings (a valid JSON list).
# - `replaced_ideas` must be a list of strings (a valid JSON list, updated cumulatively on replace actions).
#         """.strip()
#         # --- End of Corrected System Prompt ---

#         messages = [
#             {"role": "system", "content": system_msg_one_by_one},
#             {"role": "user", "content": agent_response}
#         ]

#         return self._call_gpt_and_parse(messages, AgentResponse)

    def _parse_all_at_once_response(self, agent_response, agent_name):
        """
        Parses the agent's response for all ideas in all_at_once discussion mode with a simplified action_type.
        """
        class AgentResponse(BaseModel):
            action_type: str  # "agree" or "adjust"
            current_ideas: List[str]  # Updated list of current ideas (always 5 items)
            replacement_ideas: List[str]  # Updated replacement pool after adjustments
            replaced_ideas: str = None

        # 1) figure out which replacement pool to display:
        sel_method = self.task_config.get("selection_method", "rating")
        if sel_method == "rating":
            # Shared
            rep_list = self.replacement_ideas
        else:
            # selectionTop => each agent has their own replacement pool
            # if not exist => fallback empty
            rep_list = self.agent_replacement_ideas.get(agent_name, [])

        # Build strings for current ideas and replacement pool
        current_str = "\n".join(f"{i + 1}. {idea}" for i, idea in enumerate(self.current_ideas))
        replacement_str = "\n".join(f"{i + 1}. {idea}" for i, idea in enumerate(rep_list))

        system_msg_all_at_once = f"""
        Here is the current list of ideas being reviewed:
        {current_str if current_str else "(none)"}

        Here is the replacement ideas list:
        {replacement_str if replacement_str else "(none)"}

        Based on the agent's response, evaluate the entire list:
        - **Agree**: Reply "Agree: The list meets all objectives." if the list requires no changes.
        - **Adjust**: Reply "Adjust: Updates applied to the list as per individual idea evaluations." if any modifications or replacements are needed.

        For each idea:
        - **Agree**: Reply "Agree: No changes needed."
        - **Modify**: Reply "Modify: [updated idea] - Reason: [specific reason]."
        - **Replace**: Reply "Replace: [full replacement idea] - Reason: [why this is better and what the original idea lacks]."

        Updates to apply:
        - **Agree**: No changes to the `current_ideas` or `replacement_ideas`.
        - **Modify**: Update the `current_ideas` list with the modified idea; do not modify or shorten the `replacement_ideas`.
        - **Replace**: 
            1. Replace the idea in `current_ideas` with the selected replacement idea.
            2. Remove the used replacement idea from the replacement_ideas pool to ensure it's no longer available for further use.
            3. Discard the replaced idea and move it to the `replaced_ideas` list for record-keeping.

        Ensure the `current_ideas` list always contains exactly 5 ideas after adjustments.
        **IMPORTANT: When constructing the `current_ideas` and `replacement_ideas` lists in the JSON output, you MUST use the exact, full, original text of each idea as presented in the input context above. Do NOT shorten or summarize the ideas unless an idea was specifically modified (in which case, use the full modified text). Preserve formatting like newlines within the idea text if possible.**
        Expected output JSON:
        {{
            "action_type": "agree" or "adjust",
            "current_ideas": ["idea1", "idea2", "idea3", "idea4", "idea5"],
            "replacement_ideas": ["idea6", "idea7", ...],
            "replaced_ideas": ["idea1", "idea2",...]
        }}
        """.strip()

        messages = [
            {"role": "system", "content": system_msg_all_at_once},
            {"role": "user", "content": agent_response}
        ]

        return self._call_gpt_and_parse(messages, AgentResponse)


    def _call_gpt_and_parse(self, messages, response_model):
        """
        Sends messages to GPT and parses the response using the given response model.
        """
        model = "gpt-4o"
        phases = self.task_config.get("phases", "three_stage")

        try:
            response = self.model_service.parse_response(messages, model=model, response_model=response_model)
            data = response.choices[0].message.parsed
            print(data)
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            reasoning_tokens = 0
            
            if phases == "direct_discussion":
                if hasattr(data, 'action_type') and hasattr(data, 'current_ideas'):
                    return data, prompt_tokens, completion_tokens,reasoning_tokens
                else:
                    raise ValueError("Incomplete data in parsed response for direct_discussion.")
            else:
                if hasattr(data, 'action_type') and hasattr(data, 'current_ideas') and hasattr(data, 'replacement_ideas') and hasattr(data, 'replaced_ideas'):
                    return data, prompt_tokens, completion_tokens,reasoning_tokens
                else:
                    raise ValueError("Incomplete data in parsed response for three_stage.")
        except Exception as e:
            print(f"Error in parsing agent response: {e}")
            fallback_data = {
                "action_type": "agree",
                "current_ideas": self.current_ideas,
            }
            if phases != "direct_discussion":
                fallback_data["replacement_ideas"] = self.replacement_ideas
            return fallback_data, prompt_tokens, 0, 0

    def _parse_direct_all_at_once_response(self, agent_response, agent_name):
        """
        Parses the agent's response for all ideas in all_at_once discussion mode under direct_discussion.
        """
        class AgentResponse(BaseModel):
            action_type: str  # "agree" or "adjust"
            current_ideas: List[str]  # Updated list of current ideas (always 5 items)

        # Build strings for current ideas
        current_str = "\n".join(f"{i + 1}. {idea}" for i, idea in enumerate(self.current_ideas))

        # Update the system message to reflect direct_discussion requirements
        system_msg_all_at_once = f"""
        You are reviewing the current list of ideas in the context of a direct discussion session:
        {current_str if current_str else "(none)"}

        Actions you can take for the list:
        - **Agree**: Reply "Agree: The list meets all objectives." if no changes are needed.
        - **Adjust**: Reply "Adjust: Updates applied to the list as per individual evaluations." if any modifications or replacements are required.

        For each idea:
        - **Agree**: Reply "Agree: No changes needed."
        - **Modify**: Reply "Modify: [updated idea] - Reason: [specific reason]."
        - **Replace**: Propose a **new idea** to replace the current idea. Use this format:
            "Replace: [new idea] - Reason: [why this is better aligned with the task objectives and what the current idea lacks]."

        Updates to apply:
        - **Agree**: Keep the `current_ideas` list unchanged.
        - **Modify**: Update the `current_ideas` list with the modified idea. 
        - **Replace**: Replace the idea in `current_ideas` with the proposed new idea. Ensure that the updated `current_ideas` list always contains exactly 5 ideas.

        Expected output JSON:
        {{
            "action_type": "agree" or "adjust",
            "current_ideas": ["idea1", "idea2", "idea3", "idea4", "idea5"]
        }}
        """.strip()

        messages = [
            {"role": "system", "content": system_msg_all_at_once},
            {"role": "user", "content": agent_response}
        ]

        return self._call_gpt_and_parse(messages, AgentResponse)

    def _parse_direct_one_by_one_response(self, agent_response, agent_name):
        """
        GPT + pydantic parse approach => we must provide current_ideas, replacement_ideas, agent_name in the prompt.
        """
        class AgentResponse(BaseModel):
            action_type: str  # "agree", "modify", or "replace"
            current_ideas: List[str]
            replaced_ideas: str = None  


        current_str = "\n".join(f"- {idea}" for idea in self.current_ideas)

        system_msg_one_by_one = f"""Here is the current idea:
        {current_str if current_str else "(none)"}

        Based on the agent's response, judge whether the agent:
        - **Agrees**  Reply "Agree: No changes needed."
        - **Modifies** Reply "Modify: [updated idea] - Reason: [specific reason]."
        - **Replaces** Propose a **new idea** to replace the current idea. "Replace: [new idea] - Reason: [specific reason]"

        Updates to apply:
        1. **Agree**: Keep the `current_ideas` unchanged.
        2. **Modify**: Revise the `current_ideas` by incorporating the proposed modifications, ensuring the updated version accurately reflects the changes. Please make sure to include only the idea, not the reasoning, in your response. 
        3. **Replace**: Replace the idea in `current_ideas` with the proposed new idea. Ensure the updated `current_ideas` list contains exactly one idea. Discard the replaced idea and move it to the `replaced_ideas` list for record-keeping. Please make sure to include only the idea, not the reasoning, in your response.

        Expected output JSON:
        {{
            "action_type": "agree/modify/replace",
            "current_ideas": ["idea1"]
            "replaced_ideas": ["idea1", "idea2",...]
        }}
        """.strip()

        messages = [
            {"role": "system", "content": system_msg_one_by_one},
            {"role": "user", "content": agent_response}
        ]

        return self._call_gpt_and_parse(messages, AgentResponse)
    
    def collect_intention_score(self, agent_name, response):
        """
        Collects the intention score directly from the agent's response.
        Expects the response format to include 'Score:X', where X is a number between 1-7.
        """
        import re

        # Use regex to extract the score from the response
        match = re.search(r'Score:\s*([1-7])', response)
        if match:
            score = int(match.group(1))  # Extract the numeric part
            self.intention_scores[agent_name] = score
            print(f"Collected intention score {score} from {agent_name}.")
        else:
            print(f"Invalid intention score format from {agent_name}: {response}")
            self.intention_scores[agent_name] = None  # Handle invalid responses gracefully


    def get_highest_intention_agent(self, candidates):
        """
        Returns the agent with the highest intention score among the candidates.
        """
        sorted_scores = sorted(
            [(self.intention_scores.get(agent.name, 0), agent) for agent in candidates],
            key=lambda x: (-x[0], x[1].name)  # Sort by score descending, then by name
        )
        return sorted_scores[0][1] if sorted_scores else None
