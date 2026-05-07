# main.py
from roles import *
from agent import Agent
from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE
from conversation import Conversation
from data_strategies import GenericDataStrategy
from message_strategies import GenericMessageStrategy
from discussion_modes import GenericDiscussionMode
import logging

def parse_model_and_effort(model_str):
    # Accepts e.g. "o3-mini-high" or just "o3-mini"
    parts = model_str.rsplit("-", 1)
    if len(parts) == 2 and parts[1] in {"low", "medium", "high"}:
        return parts[0], parts[1]
    return model_str, None

def main(llm_count=1, model = 'gpt-4o', temperature=1, persona_type=None, phases="three_stage", generation_method="dependent", 
         selection_method="rating", discussion_method="all_at_once", 
         discussion_order_method="fixed", task_type="PS", replacement_pool_size=0, 
         skip_to_discussion=False, max_responses=30, min_responses=None, question_id="plastic_waste"):
    try:
        ROLES = get_randomized_roles_with_fixed_same(llm_count)

        # Print the generated roles to see the result
        for key, role_description in ROLES.items():
            print(f"--- {key} ---")
            print(role_description)
            print("\n") 
        if persona_type == 'none':
            system_messages = [f"You are Agent {i+1}." for i in range(llm_count)]
        elif persona_type == 'same':
            system_messages = [f"You are Agent {i+1}. {ROLES['Same_Persona']}" for i in range(llm_count)]
        elif persona_type == 'different':
            personas = [f"Persona_{i+1}" for i in range(llm_count)]
            system_messages = [ROLES[persona] for persona in personas[:llm_count]]
       
        # Handle single or multiple models
        if isinstance(model, list):
            if len(model) < llm_count:
                raise ValueError("Not enough models in DEFAULT_MODEL for the number of agents.")
            agent_models = model[:llm_count]  # Assign models from the list
        else:
            agent_models = [model] * llm_count  # Use the same model for all agents

        # Create agents with assigned models and reasoning efforts
        agents = []
        reasoning_efforts = []
        for i, (system_message, model_name) in enumerate(zip(system_messages, agent_models)):
            base_model, reasoning_effort = parse_model_and_effort(model_name)
            config = {"temperature": temperature}
            if reasoning_effort:
                config["reasoning_effort"] = reasoning_effort
            agent = Agent(name=f"Agent {i+1}", system_message=system_message, model_name=base_model, config=config)
            agents.append(agent)
            reasoning_efforts.append(reasoning_effort)

        print(agents)

    #    agents = []

        # for i, system_message in enumerate(system_messages):
        #     agent = Agent(name=f"Agent_{i+1}", system_message=system_message)
        #     agents.append(agent)
        # print(agents)

        # task_config = {
        #     "task_type": "PS",               # "AUT" or "PS"
        #     "phases": phases,          # "three_stage" or "direct_discussion"
        #     "generation_method": generation_method, # "independent" or "dependent"
        #     "selection_method": "rating", # "selectionTop" or "rating"
        #     "discussion_method": "all_at_once",  # "all_at_once" or "one_by_one", "open", or "iterative_refinement", or "creative" or "none"
        #     "discussion_order_method": "fixed",  # "fixed" or "random" or "hand_raising"
        #     "persona_type":persona_type,
        #     "llm_count":llm_count,
        #     "model":DEFAULT_MODEL,
        #     "temperature":DEFAULT_TEMPERATURE,
        #     "replacement_pool_size": 0
        # }

        task_config = {
            "task_type": task_type,               # "AUT" or "PS"
            "phases": phases,          # "three_stage" or "direct_discussion"
            "generation_method": generation_method, # "independent" or "dependent"
            "selection_method": selection_method, # "selectionTop" or "rating"
            "discussion_method": discussion_method,  # "all_at_once" or "one_by_one", "open", or "iterative_refinement", or "creative"
            "discussion_order_method": discussion_order_method,  # "fixed" or "random" or "hand_raising"
            "persona_type": persona_type,
            "llm_count": llm_count,
            "model": model,
            "temperature": temperature,
            "replacement_pool_size": replacement_pool_size,
            "role_assignment_in_user_prompt": ["deepseek-ai/DeepSeek-R1"],
            "max_responses": max_responses,
            "min_responses": min_responses,  # New config option to hide agree until specified round
            "reasoning_efforts": reasoning_efforts,  # Add reasoning efforts to config
            "question_id": question_id,  # Add question_id to config
        }

        data_strategy = GenericDataStrategy(task_config=task_config)
        message_strategy = GenericMessageStrategy(task_config=task_config, data_strategy=data_strategy)
        conversation = Conversation(agents=agents, data_strategy=data_strategy, task_config=task_config)
        discussion = GenericDiscussionMode(conversation, task_config, message_strategy)

        # skip_to_discussion parameter
        discussion.run(skip_to_discussion=False)
    except Exception as e:
        logging.error("An error occurred during the discussion: %s", e)
        raise
    finally:
        # Always try to save the chat history even if there was an error
        if 'conversation' in locals():
            conversation.save_chat_history()


if __name__ == "__main__":
    # Default: False (set to True for debugging) 
    main(llm_count=3, persona_type="same", min_responses=30)  # Set hide_agree_until_round=30 for instruct mode

