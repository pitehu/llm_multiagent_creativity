# Preprocessing Code

This folder contains the provenance scripts used to transform raw chat logs and human/LLM idea files into the compact analysis data used by the notebooks.

The main notebooks in `../analysis/` do not require these scripts; they run from the cleaned CSV files in `../data/`. These preprocessing scripts are included so readers can inspect or rerun the upstream pipeline when the raw data archives are available.

## Expected Raw Data Layout

Unzip the relevant raw data archives at the repository root:

```bash
unzip multiagent_creativity_llm_chatlogs.zip -d .
unzip multiagent_creativity_human_chatlogs.zip -d .
unzip multiagent_creativity_embeddings.zip -d .
```

Expected paths after unzipping:

```text
data_external/
  raw_chatlogs/
    llm/results/
    human/transcription_human_data/
  embeddings/
```

## Main Scripts

- `extract_final_ideas_from_task_configs.py`: extracts final LLM ideas and token metadata from raw LLM chat logs.
- `match_conditions_to_data.py`: matches extracted LLM ideas to experimental condition metadata.
- `paraphrase_ideas_csv.py` and `azure_paraphrase_service.py`: paraphrases final ideas into a standardized style before blinded human rating.
- `preprocess_all_ideas.py`: combines rated ideas with LLM and human conversation histories and writes cleaned CSV/parquet outputs.
- `embed_all_ideas.py`: embeds ideas, turns, and idea-evolution text.

The trajectory metric CSVs can be recomputed from turn embeddings with `../scripts/compute_trajectory_metrics.py`. The older trajectory precompute scripts are omitted from this release because they duplicate the cleaner release trajectory script.

## Included Resources

- `resources/unique_task_configs.json`: task configuration grid used by `extract_final_ideas_from_task_configs.py`.
- `resources/study_plan_conditions.csv`: condition plan used by `match_conditions_to_data.py`.

The scripts default to the `data_external/` layout shown above. For nonstandard locations, set the path environment variables referenced at the top of each script, such as `RESULTS_BASE_PATH`, `HUMAN_TRANSCRIPTION_DIR`, `EMBEDDINGS_DIR`, or `BASE_PATH`.

`match_conditions_to_data.py` requires the rated final-idea CSV as an explicit `--data` argument:

```bash
python preprocessing/match_conditions_to_data.py \
  --data path/to/final_idea_with_human_ratings.csv
```

The raw generation/preprocessing code may use the historical condition label `creative`; this corresponds to `progressive` in the manuscript.
