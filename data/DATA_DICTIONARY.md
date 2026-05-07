# Data Dictionary

This file describes `ideas_with_ratings_clean.csv`, the idea-level dataset used by the release notebooks.

## Notes

- Each row is one final idea.
- Human rows are identified by `source == "human_data"` and `data_type == "human"`.
- LLM rows have `source != "human_data"` and include generation/extraction metadata.
- `creative` is the historical code label for the manuscript condition named `progressive`.
- Rating columns use anonymized rater IDs. `N*` = novelty and `U*` = usefulness. Direct creativity rater columns are not included in the release; the primary creativity outcome is `avg_creativity_rating`.
- `avg_novelty_rating` and `avg_usefulness_rating` are min-max scaled within task before computing `avg_creativity_rating`.

## Columns

| Column | Description |
|---|---|
| `file_id` | Unique row/run identifier. For LLM rows, usually derived from the raw chatlog filename; for human rows, derived from the source session/row identifier. |
| `question_id` | Task identifier: `education_inequality`, `employee_attrition`, `plastic_waste`, `singing_shower`, `sorry_pandemic`, or `supply_chain`. |
| `row_ID` | Row index from the merged preprocessing table. |
| `run_num` | LLM replicate/run number when available. Missing for human rows. |
| `condition_code` | Compact experimental condition code used in analysis scripts. Missing for human rows. |
| `condition_number` | Numeric experimental condition identifier when available. |
| `data_type` | Broad source category: `human`, `baseline`, or `experiment`. |
| `discussion` | Unified discussion label used in analyses. Historical value `creative` corresponds to manuscript `progressive`. |
| `discussion_plan` | Human-readable discussion plan from condition matching, such as `open`, `instructed`, or `iterative`. |
| `discussion_order_plan` | Human-readable discussion order plan, such as `fix`, `random`, or `raise`. |
| `idea_generation_plan` | Human-readable generation plan, such as `interactive` or `nominal`. |
| `additional_idea_generation_plan` | Additional generation condition, used mainly for the historical `creative`/`progressive` condition. |
| `number_of_agents` | Number of human participants or LLM agents in the team. |
| `models` | Model name or model mixture for LLM rows. Missing for human rows. |
| `persona` | Persona assignment condition for LLM rows: `no`, `same`, or `different`. |
| `temperature` | LLM sampling temperature when available. |
| `task_type` | Task class. In this release, rows are coded as `PS`. |
| `replacement_pool_size` | Size of the replacement idea pool used in relevant LLM conditions. |
| `final_idea` | Final idea text submitted by the human team or extracted from the LLM chatlog. |
| `final_idea_length` | Character length of `final_idea`. |
| `paraphrased_idea` | Standardized paraphrase used for blinded rating. |
| `paraphrased_word_count` | Word count of `paraphrased_idea`. |
| `source` | Extraction/source label. `human_data` marks human rows; other values describe how the LLM final idea was extracted from chat logs. |
| `final_round` | Final LLM discussion round when extracted from the raw chatlog. |
| `total_rounds` | Total number of generated discussion rounds for LLM rows. |
| `has_conversation_data` | Whether the preprocessing pipeline linked this row to raw conversation history. |
| `conversation_turns` | Number of linked conversation turns. |
| `N2` | Novelty rating from anonymized rater 2. |
| `N4` | Novelty rating from anonymized rater 4. |
| `N5` | Novelty rating from anonymized rater 5. |
| `N7` | Novelty rating from anonymized rater 7. |
| `N9` | Novelty rating from anonymized rater 9. |
| `U2` | Usefulness rating from anonymized rater 2. |
| `U4` | Usefulness rating from anonymized rater 4. |
| `U5` | Usefulness rating from anonymized rater 5. |
| `U7` | Usefulness rating from anonymized rater 7. |
| `U9` | Usefulness rating from anonymized rater 9. |
| `avg_creativity_rating` | Final creativity score used in analyses, computed as scaled novelty times scaled usefulness. |
| `avg_novelty_rating` | Mean novelty rating, min-max scaled within `question_id`. |
| `avg_usefulness_rating` | Mean usefulness rating, min-max scaled within `question_id`. |
| `grand_total_tokens` | Total tokens recorded for the LLM chatlog, when available. |
| `total_prompt_tokens` | Prompt tokens recorded for the LLM chatlog, when available. |
| `total_completion_tokens` | Completion tokens recorded for the LLM chatlog, when available. |
| `phases` | LLM run phase design, such as `three_stage` or `direct_discussion`. |
| `generation_method` | LLM idea generation dependency design: `dependent` or `independent`. |
| `selection_method` | LLM idea selection method. In this release, LLM rows are coded as `rating`. |
| `discussion_method` | Raw LLM discussion method label, such as `none`, `open`, `all_at_once`, `iterative_refinement`, or historical `creative`. |
| `discussion_order_method` | Raw LLM discussion order label, such as `fixed`, `random`, or `hand_raising`. |
| `llm_count` | Number of LLM agents for LLM rows; equals `number_of_agents` for human rows for comparison analyses. |
| `final_agent_phase` | Phase associated with the final extracted LLM response, when available. |

## Related Files

- `comprehensive_trajectory_metrics.csv`: trajectory metrics computed from Qwen3-Embedding-0.6B turn embeddings.
- `comprehensive_trajectory_metrics_4b.csv`: same trajectory metrics computed from Qwen3-Embedding-4B turn embeddings for robustness checks.
