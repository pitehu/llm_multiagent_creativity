# Multi-Agent LLM Creativity: Code and Data Release

This release contains the analysis notebooks and data needed to reproduce the quantitative figures and tables reported in the manuscript.

The main notebooks run from the compact CSV files included here. Raw LLM chat logs, raw human chat logs, and embeddings are distributed separately as raw data archives.

## Contents

```text
analysis/
  1_idea_level_analysis.ipynb
  2_trajectory_analysis.ipynb
  3_robustness_checks.ipynb
data/
  ideas_with_ratings_clean.csv
  comprehensive_trajectory_metrics.csv
  comprehensive_trajectory_metrics_4b.csv
  DATA_DICTIONARY.md
scripts/
  compute_trajectory_metrics.py
generation/
  multi-agent LLM chatlog generation code
preprocessing/
  raw-log, rating, embedding, and trajectory preprocessing scripts
requirements.txt
```

The notebooks read from `data/` and create an `outputs/` folder for generated figures and tables when run. Each notebook section is annotated with the manuscript figure or table label it produces.

The `generation/` and `preprocessing/` folders are included for provenance. They are not required to reproduce the paper figures and tables from the included compact CSV files.

## Setup

```bash
pip install -r requirements.txt
jupyter notebook
```

Open the notebooks in `analysis/` and run them in order:

1. `1_idea_level_analysis.ipynb`
2. `2_trajectory_analysis.ipynb`
3. `3_robustness_checks.ipynb`

The notebooks can also be executed non-interactively:

```bash
jupyter nbconvert --execute --to notebook --output executed_1.ipynb analysis/1_idea_level_analysis.ipynb
jupyter nbconvert --execute --to notebook --output executed_2.ipynb analysis/2_trajectory_analysis.ipynb
jupyter nbconvert --execute --to notebook --output executed_3.ipynb analysis/3_robustness_checks.ipynb
```

## Data Files

| File | Description |
|---|---|
| `ideas_with_ratings_clean.csv` | Idea-level dataset with blind creativity, novelty, and usefulness ratings plus experimental metadata. |
| `comprehensive_trajectory_metrics.csv` | Pre-computed semantic trajectory features using Qwen3-Embedding-0.6B. |
| `comprehensive_trajectory_metrics_4b.csv` | Pre-computed semantic trajectory features using Qwen3-Embedding-4B for the embedding-model robustness check. |
| `DATA_DICTIONARY.md` | Column definitions for the released idea-level CSV. |

## Notebook Coverage

### `1_idea_level_analysis.ipynb`

Reproduces idea-level comparisons between human and LLM teams, including:

- LLM vs. human creativity, novelty, and usefulness comparisons
- Novelty-usefulness trade-off figure
- Best-idea and top-percentile analyses
- Top-10 distribution and top-idea tables
- Discussion-structure effects by model type
- Discussion order, round length, generation mode, and replacement-pool tables
- Persona and team-size appendix tables
- Idea-level regression and descriptive-statistics tables

### `2_trajectory_analysis.ipynb`

Reproduces semantic trajectory analyses, including:

- Hierarchical variance decomposition
- LLM vs. human trajectory coefficient comparison
- Scaffolding-paradox figure
- Full LLM and human trajectory regression tables
- Model-specific variance decomposition
- Design-lever manipulability tables

### `3_robustness_checks.ipynb`

Reproduces robustness analyses, including:

- Embedding model robustness
- Additive vs. multiplicative creativity operationalization
- Token-count control for discussion effects

## Raw Data Archive

The notebooks above do not require the raw data archives. To inspect raw chat logs or regenerate the cleaned data and trajectory files, download the archive(s) needed for that step:

https://drive.google.com/drive/folders/1g9azpIYK7CBcvEdULXf0oAgG9JeSKAA7?usp=sharing


```text
multiagent_creativity_llm_chatlogs.zip
multiagent_creativity_human_chatlogs.zip
multiagent_creativity_embeddings.zip
```

Unzip each archive at the repository root:

```bash
unzip multiagent_creativity_llm_chatlogs.zip -d .
unzip multiagent_creativity_human_chatlogs.zip -d .
unzip multiagent_creativity_embeddings.zip -d .
```

These create:

```text
data_external/
  raw_chatlogs/
    llm/results/
    human/transcription_human_data/
  embeddings/
```

The raw data archives are used by the scripts in `preprocessing/`. The notebooks in `analysis/` reproduce the manuscript figures and tables from the compact CSV files already included in `data/`.

## Regenerating Trajectory Metrics

The release includes pre-computed trajectory metrics, so this step is not required to reproduce the manuscript analyses from the released data.

If turn-level embedding parquet files are available, the metric CSVs can be regenerated with:

```bash
python scripts/compute_trajectory_metrics.py \
  --turn-embeddings path/to/turns_embeddings_qwen3_0.6b.parquet \
  --output data/comprehensive_trajectory_metrics.csv
```

The input parquet file must contain `file_id`, `question_id`, and `embedding` columns.

## Generating and Preprocessing Raw Chat Logs

The `generation/` folder contains the multi-agent LLM code used to produce raw LLM chat logs. API keys are not included; set provider credentials as environment variables before running. See `generation/README.md`.

The `preprocessing/` folder contains scripts used to extract final ideas, match experimental conditions, combine ratings with human/LLM logs, and generate embeddings. Trajectory metrics can be recomputed with `scripts/compute_trajectory_metrics.py`. See `preprocessing/README.md`.

Because hosted model APIs can change, rerunning generation documents the workflow but is not expected to reproduce identical raw text outputs. Regenerating the full LLM chatlog corpus can also take substantial time and paid API credits; see `generation/README.md`.

## Notes

The notebooks reproduce the quantitative manuscript figures and tables from the released CSV files. The task-prompt and experimental-condition tables are static design tables in the manuscript. Transcript excerpt tables and turn-level example visualizations require raw conversation histories or turn-level embeddings rather than the compact analysis CSVs.

The original generation and preprocessing code uses the historical label `creative` for a discussion method that is called `progressive` in the manuscript and final edited figure labels. These refer to the same condition.
