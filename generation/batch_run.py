import time
import logging
from main import main
import concurrent.futures

# task_combinations = [
#     # Condition 0: 1 agent, no persona, one idea
#     {"llm_count": 1, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 1: 3 agents, no persona, interactive
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 2: 3 agents, same persona, interactive
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 3: 3 agents, different persona, interactive
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 4: 6 agents, no persona, interactive
#     {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 5: 6 agents, same persona, interactive
#     {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 6: 6 agents, different persona, interactive
#     {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 7: 3 agents, different persona, nominal
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "independent", "discussion_method": "none", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 8: 6 agents, different persona, nominal
#     {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "independent", "discussion_method": "none", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 9: 3 agents, no persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 10: 3 agents, same persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 11: 3 agents, different persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 12: 3 agents, different persona, open discussion, 30 responses, random order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 13: 3 agents, no persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 14: 3 agents, same persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 15: 3 agents, different persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 16: 3 agents, different persona, open discussion, 60 responses, random order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 17: 3 agents, no persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 18: 3 agents, same persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 19: 3 agents, different persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 20: 3 agents, different persona, all_at_once discussion, 30 responses, hand_raising order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 21: 3 agents, different persona, all_at_once discussion, 30 responses, random order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 22: 3 agents, no persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 23: 3 agents, same persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 24: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 25: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), hand_raising order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 26: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), random order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 27: 3 agents, no persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 28: 3 agents, same persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 29: 3 agents, different persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 30: 3 agents, different persona, iterative_refinement discussion, 30 responses, random order (DIRECT DISCUSSION)
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "direct_discussion",
#      "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 31: 3 agents, no persona, interactive + all_at_once discussion, 30 responses, fixed order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 32: 3 agents, same persona, interactive + all_at_once discussion, 30 responses, fixed order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 33: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, fixed order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 34: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, hand_raising order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 35: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, random order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 36: 3 agents, no persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 37: 3 agents, same persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 38: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 39: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), hand_raising order
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 40: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), random order
#     {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 41: 3 agents, no persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 5, "question_id": "plastic_waste"},
#
#     # Condition 42: 3 agents, same persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 5, "question_id": "plastic_waste"},
#
#     # Condition 43: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 5, "question_id": "plastic_waste"},
#
#     # Condition 44: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, hand_raising order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
#      "replacement_pool_size": 5, "question_id": "plastic_waste"},
#
#     # Condition 45: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, random order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
#      "replacement_pool_size": 5, "question_id": "plastic_waste"},
#
#     # Condition 46: 6 agents, no persona, interactive + all_at_once discussion, 30 responses, fixed order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 47: 6 agents, same persona, interactive + all_at_once discussion, 30 responses, fixed order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 48: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, fixed order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 49: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, hand_raising order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 50: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, random order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 51: 6 agents, no persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
#     {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 52: 6 agents, same persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
#     {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 53: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
#     {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 54: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), hand_raising order
#     {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 55: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), random order
#     {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "min_responses": 30, "question_id": "plastic_waste"},
#
#     # Condition 56: 3 agents, no persona, interactive + iterative_refinement discussion, 30 responses, fixed order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 57: 3 agents, same persona, interactive + iterative_refinement discussion, 30 responses, fixed order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 58: 3 agents, different persona, interactive + iterative_refinement discussion, 30 responses, fixed order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 59: 3 agents, different persona, interactive + iterative_refinement discussion, 30 responses, random order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 60: 6 agents, no persona, interactive + iterative_refinement discussion, 30 responses, fixed order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 61: 6 agents, same persona, interactive + iterative_refinement discussion, 30 responses, fixed order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 62: 6 agents, different persona, interactive + iterative_refinement discussion, 30 responses, fixed order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 63: 6 agents, different persona, interactive + iterative_refinement discussion, 30 responses, random order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 64: 3 agents, no persona, interactive + creative discussion, fixed order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 65: 3 agents, same persona, interactive + creative discussion, fixed order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 66: 3 agents, different persona, interactive + creative discussion, fixed order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 67: 3 agents, different persona, interactive + creative discussion, random order
#     {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 68: 6 agents, no persona, interactive + creative discussion, fixed order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 69: 6 agents, same persona, interactive + creative discussion, fixed order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 70: 6 agents, different persona, interactive + creative discussion, fixed order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"},
#
#     # Condition 71: 6 agents, different persona, interactive + creative discussion, random order
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"}
# ]
# task_combinations = [
#     # Condition 0: 1 agent, no persona, one idea
#     {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
#      "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
#      "replacement_pool_size": 0, "question_id": "plastic_waste"}]


task_combinations = [
    # Condition 0: 1 agent, no persona, one idea
    {"llm_count": 1, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 1: 3 agents, no persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 2: 3 agents, same persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 3: 3 agents, different persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 4: 6 agents, no persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 5: 6 agents, same persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 6: 6 agents, different persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 7: 3 agents, different persona, nominal
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "independent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 8: 6 agents, different persona, nominal
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "independent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 9: 3 agents, no persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 10: 3 agents, same persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 11: 3 agents, different persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 12: 3 agents, different persona, open discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 13: 3 agents, no persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 14: 3 agents, same persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 15: 3 agents, different persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 16: 3 agents, different persona, open discussion, 60 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 17: 3 agents, no persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 18: 3 agents, same persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 19: 3 agents, different persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 20: 3 agents, different persona, all_at_once discussion, 30 responses, hand_raising order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 21: 3 agents, different persona, all_at_once discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 22: 3 agents, no persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 23: 3 agents, same persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 24: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 25: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), hand_raising order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 26: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 27: 3 agents, no persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 28: 3 agents, same persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 29: 3 agents, different persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 30: 3 agents, different persona, iterative_refinement discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 31: 3 agents, no persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 32: 3 agents, same persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 33: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 34: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, hand_raising order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 35: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 36: 3 agents, no persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 37: 3 agents, same persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 38: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 39: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), hand_raising order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 40: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), random order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 41: 3 agents, no persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "supply_chain"},

    # Condition 42: 3 agents, same persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "supply_chain"},

    # Condition 43: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "supply_chain"},

    # Condition 44: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, hand_raising order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 5, "question_id": "supply_chain"},

    # Condition 45: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 5, "question_id": "supply_chain"},

    # Condition 46: 6 agents, no persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 47: 6 agents, same persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 48: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 49: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, hand_raising order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 50: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 51: 6 agents, no persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 52: 6 agents, same persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 53: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 54: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), hand_raising order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 55: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), random order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "supply_chain"},

    # Condition 56: 3 agents, no persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 57: 3 agents, same persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 58: 3 agents, different persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 59: 3 agents, different persona, interactive + iterative_refinement discussion, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 60: 6 agents, no persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 61: 6 agents, same persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 62: 6 agents, different persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 63: 6 agents, different persona, interactive + iterative_refinement discussion, 30 responses, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 64: 3 agents, no persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 65: 3 agents, same persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 66: 3 agents, different persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 67: 3 agents, different persona, interactive + creative discussion, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 68: 6 agents, no persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 69: 6 agents, same persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 70: 6 agents, different persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    # Condition 71: 6 agents, different persona, interactive + creative discussion, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "supply_chain"},

    {"llm_count": 1, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 1: 3 agents, no persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 2: 3 agents, same persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 3: 3 agents, different persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 4: 6 agents, no persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 5: 6 agents, same persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 6: 6 agents, different persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 7: 3 agents, different persona, nominal
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "independent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 8: 6 agents, different persona, nominal
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "independent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 9: 3 agents, no persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 10: 3 agents, same persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 11: 3 agents, different persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 12: 3 agents, different persona, open discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 13: 3 agents, no persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 14: 3 agents, same persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 15: 3 agents, different persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 16: 3 agents, different persona, open discussion, 60 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 17: 3 agents, no persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 18: 3 agents, same persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 19: 3 agents, different persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 20: 3 agents, different persona, all_at_once discussion, 30 responses, hand_raising order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 21: 3 agents, different persona, all_at_once discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 22: 3 agents, no persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 23: 3 agents, same persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 24: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 25: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), hand_raising order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 26: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 27: 3 agents, no persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 28: 3 agents, same persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 29: 3 agents, different persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 30: 3 agents, different persona, iterative_refinement discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 31: 3 agents, no persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 32: 3 agents, same persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 33: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 34: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, hand_raising order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 35: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 36: 3 agents, no persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 37: 3 agents, same persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 38: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 39: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), hand_raising order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 40: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), random order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 41: 3 agents, no persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "sorry_pandemic"},

    # Condition 42: 3 agents, same persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "sorry_pandemic"},

    # Condition 43: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "sorry_pandemic"},

    # Condition 44: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, hand_raising order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 5, "question_id": "sorry_pandemic"},

    # Condition 45: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 5, "question_id": "sorry_pandemic"},

    # Condition 46: 6 agents, no persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 47: 6 agents, same persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 48: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 49: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, hand_raising order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 50: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 51: 6 agents, no persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 52: 6 agents, same persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 53: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 54: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), hand_raising order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 55: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), random order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "sorry_pandemic"},

    # Condition 56: 3 agents, no persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 57: 3 agents, same persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 58: 3 agents, different persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 59: 3 agents, different persona, interactive + iterative_refinement discussion, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 60: 6 agents, no persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 61: 6 agents, same persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 62: 6 agents, different persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 63: 6 agents, different persona, interactive + iterative_refinement discussion, 30 responses, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 64: 3 agents, no persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 65: 3 agents, same persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 66: 3 agents, different persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 67: 3 agents, different persona, interactive + creative discussion, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 68: 6 agents, no persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 69: 6 agents, same persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 70: 6 agents, different persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    # Condition 71: 6 agents, different persona, interactive + creative discussion, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "sorry_pandemic"},

    {"llm_count": 1, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 1: 3 agents, no persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 2: 3 agents, same persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 3: 3 agents, different persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 4: 6 agents, no persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 5: 6 agents, same persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 6: 6 agents, different persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 7: 3 agents, different persona, nominal
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "independent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 8: 6 agents, different persona, nominal
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "independent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 9: 3 agents, no persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 10: 3 agents, same persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 11: 3 agents, different persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 12: 3 agents, different persona, open discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 13: 3 agents, no persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 14: 3 agents, same persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 15: 3 agents, different persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 16: 3 agents, different persona, open discussion, 60 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 17: 3 agents, no persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 18: 3 agents, same persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 19: 3 agents, different persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 20: 3 agents, different persona, all_at_once discussion, 30 responses, hand_raising order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 21: 3 agents, different persona, all_at_once discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 22: 3 agents, no persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 23: 3 agents, same persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 24: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 25: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), hand_raising order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 26: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 27: 3 agents, no persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 28: 3 agents, same persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 29: 3 agents, different persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 30: 3 agents, different persona, iterative_refinement discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 31: 3 agents, no persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 32: 3 agents, same persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 33: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 34: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, hand_raising order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 35: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 36: 3 agents, no persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 37: 3 agents, same persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 38: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 39: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), hand_raising order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 40: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), random order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 41: 3 agents, no persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "education_inequality"},

    # Condition 42: 3 agents, same persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "education_inequality"},

    # Condition 43: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "education_inequality"},

    # Condition 44: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, hand_raising order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 5, "question_id": "education_inequality"},

    # Condition 45: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 5, "question_id": "education_inequality"},

    # Condition 46: 6 agents, no persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 47: 6 agents, same persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 48: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 49: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, hand_raising order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 50: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 51: 6 agents, no persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 52: 6 agents, same persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 53: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 54: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), hand_raising order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 55: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), random order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "education_inequality"},

    # Condition 56: 3 agents, no persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 57: 3 agents, same persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 58: 3 agents, different persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 59: 3 agents, different persona, interactive + iterative_refinement discussion, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 60: 6 agents, no persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 61: 6 agents, same persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 62: 6 agents, different persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 63: 6 agents, different persona, interactive + iterative_refinement discussion, 30 responses, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 64: 3 agents, no persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 65: 3 agents, same persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 66: 3 agents, different persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 67: 3 agents, different persona, interactive + creative discussion, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 68: 6 agents, no persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 69: 6 agents, same persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 70: 6 agents, different persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 71: 6 agents, different persona, interactive + creative discussion, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "education_inequality"},

    # Condition 0: 1 agent, no persona, one idea
    {"llm_count": 1, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 1: 3 agents, no persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 2: 3 agents, same persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 3: 3 agents, different persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 4: 6 agents, no persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 5: 6 agents, same persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 6: 6 agents, different persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 7: 3 agents, different persona, nominal
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "independent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 8: 6 agents, different persona, nominal
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "independent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 9: 3 agents, no persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 10: 3 agents, same persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 11: 3 agents, different persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 12: 3 agents, different persona, open discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 13: 3 agents, no persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 14: 3 agents, same persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 15: 3 agents, different persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 16: 3 agents, different persona, open discussion, 60 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 17: 3 agents, no persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 18: 3 agents, same persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 19: 3 agents, different persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 20: 3 agents, different persona, all_at_once discussion, 30 responses, hand_raising order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 21: 3 agents, different persona, all_at_once discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 22: 3 agents, no persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 23: 3 agents, same persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 24: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 25: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), hand_raising order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 26: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 27: 3 agents, no persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 28: 3 agents, same persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 29: 3 agents, different persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 30: 3 agents, different persona, iterative_refinement discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 31: 3 agents, no persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 32: 3 agents, same persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 33: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 34: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, hand_raising order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 35: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 36: 3 agents, no persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 37: 3 agents, same persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 38: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 39: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), hand_raising order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 40: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), random order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 41: 3 agents, no persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "employee_attrition"},

    # Condition 42: 3 agents, same persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "employee_attrition"},

    # Condition 43: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "employee_attrition"},

    # Condition 44: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, hand_raising order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 5, "question_id": "employee_attrition"},

    # Condition 45: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 5, "question_id": "employee_attrition"},

    # Condition 46: 6 agents, no persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 47: 6 agents, same persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 48: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 49: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, hand_raising order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 50: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 51: 6 agents, no persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 52: 6 agents, same persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 53: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 54: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), hand_raising order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 55: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), random order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "employee_attrition"},

    # Condition 56: 3 agents, no persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 57: 3 agents, same persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 58: 3 agents, different persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 59: 3 agents, different persona, interactive + iterative_refinement discussion, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 60: 6 agents, no persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 61: 6 agents, same persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 62: 6 agents, different persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 63: 6 agents, different persona, interactive + iterative_refinement discussion, 30 responses, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 64: 3 agents, no persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 65: 3 agents, same persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 66: 3 agents, different persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 67: 3 agents, different persona, interactive + creative discussion, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 68: 6 agents, no persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 69: 6 agents, same persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 70: 6 agents, different persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 71: 6 agents, different persona, interactive + creative discussion, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "employee_attrition"},

    # Condition 0: 1 agent, no persona, one idea
    {"llm_count": 1, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 1: 3 agents, no persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 2: 3 agents, same persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 3: 3 agents, different persona, interactive
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 4: 6 agents, no persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 5: 6 agents, same persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 6: 6 agents, different persona, interactive
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 7: 3 agents, different persona, nominal
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "independent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 8: 6 agents, different persona, nominal
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "independent", "discussion_method": "none", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 9: 3 agents, no persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 10: 3 agents, same persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 11: 3 agents, different persona, open discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 12: 3 agents, different persona, open discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 13: 3 agents, no persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 14: 3 agents, same persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 15: 3 agents, different persona, open discussion, 60 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 16: 3 agents, different persona, open discussion, 60 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "open", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 17: 3 agents, no persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 18: 3 agents, same persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 19: 3 agents, different persona, all_at_once discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 20: 3 agents, different persona, all_at_once discussion, 30 responses, hand_raising order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 21: 3 agents, different persona, all_at_once discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 22: 3 agents, no persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 23: 3 agents, same persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 24: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 25: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), hand_raising order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 26: 3 agents, different persona, all_at_once discussion, 60 responses (minimum 30), random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 27: 3 agents, no persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 28: 3 agents, same persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 29: 3 agents, different persona, iterative_refinement discussion, 30 responses, fixed order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 30: 3 agents, different persona, iterative_refinement discussion, 30 responses, random order (DIRECT DISCUSSION)
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different",
     "phases": "direct_discussion",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 31: 3 agents, no persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 32: 3 agents, same persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 33: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 34: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, hand_raising order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 35: 3 agents, different persona, interactive + all_at_once discussion, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 36: 3 agents, no persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 37: 3 agents, same persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 38: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 39: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), hand_raising order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 40: 3 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), random order
    {"llm_count": 3, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 41: 3 agents, no persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "singing_shower"},

    # Condition 42: 3 agents, same persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "singing_shower"},

    # Condition 43: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 5, "question_id": "singing_shower"},

    # Condition 44: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, hand_raising order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 5, "question_id": "singing_shower"},

    # Condition 45: 3 agents, different persona, interactive + all_at_once discussion with top5, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 5, "question_id": "singing_shower"},

    # Condition 46: 6 agents, no persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 47: 6 agents, same persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 48: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 49: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, hand_raising order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 50: 6 agents, different persona, interactive + all_at_once discussion, 30 responses, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 51: 6 agents, no persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 52: 6 agents, same persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 53: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), fixed order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 54: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), hand_raising order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "hand_raising",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 55: 6 agents, different persona, interactive + all_at_once discussion, 60 responses (minimum 30), random order
    {"llm_count": 6, "max_responses": 60, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "all_at_once", "discussion_order_method": "random",
     "replacement_pool_size": 0, "min_responses": 30, "question_id": "singing_shower"},

    # Condition 56: 3 agents, no persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 57: 3 agents, same persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 58: 3 agents, different persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 59: 3 agents, different persona, interactive + iterative_refinement discussion, 30 responses, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 60: 6 agents, no persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 61: 6 agents, same persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 62: 6 agents, different persona, interactive + iterative_refinement discussion, 30 responses, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 63: 6 agents, different persona, interactive + iterative_refinement discussion, 30 responses, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "iterative_refinement", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 64: 3 agents, no persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 65: 3 agents, same persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 66: 3 agents, different persona, interactive + creative discussion, fixed order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 67: 3 agents, different persona, interactive + creative discussion, random order
    {"llm_count": 3, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 68: 6 agents, no persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "none", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 69: 6 agents, same persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "same", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 70: 6 agents, different persona, interactive + creative discussion, fixed order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "fixed",
     "replacement_pool_size": 0, "question_id": "singing_shower"},

    # Condition 71: 6 agents, different persona, interactive + creative discussion, random order
    {"llm_count": 6, "max_responses": 30, "model": "gpt-4.1", "persona_type": "different", "phases": "three_stage",
     "generation_method": "dependent", "discussion_method": "creative", "discussion_order_method": "random",
     "replacement_pool_size": 0, "question_id": "singing_shower"}
]




def run_config(config):
    try:
        logging.info(f"Running config: {config}")
        main(**config)
    except Exception as e:
        logging.error(f"Error during run: {e}")


if __name__ == "__main__":
    with concurrent.futures.ProcessPoolExecutor(max_workers=36) as executor:
        futures = [executor.submit(run_config, config) for config in task_combinations]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"Task generated an exception: {exc}")

    print("\nAll tasks completed.")

# for config in task_combinations:
#     llm_count = config["llm_count"]
#     persona_type = config["persona_type"]
#     phases = config["phases"]
#     generation_method = config["generation_method"]
#     print("running config", config)
#     print(f"\nRunning: llm_count={llm_count}, persona_type={persona_type}, phases={phases}, generation_method={generation_method}")
#     logging.info(f"Starting run with llm_count={llm_count}, persona_type={persona_type}, phases={phases}, generation_method={generation_method}")
#
#     try:
#         main(**config)  # This passes all parameters from the dictionary to the function
#     except Exception as e:
#         logging.error(f"Error during run: {e}")
#
#     time.sleep(2)

