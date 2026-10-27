# Closer to AI, Easier to Replace?

Does a closer connection to AI mean a greater risk of job replacement? This project compares occupational AI exposure and task coverage with projected U.S. employment growth. It reproduces the interactive Plotly visualization in [Blog 7](https://xia071212.github.io/myrepo/blog/posts/post7/), using the same 722 occupations throughout.

## Data and sources

The original source files needed for the article are included in `data/raw/`. Reproduction uses these saved versions rather than downloading changing releases.

| Source and saved file | Fields used | Purpose |
|---|---|---|
| [Anthropic Economic Index](https://huggingface.co/datasets/Anthropic/EconomicIndex/tree/main/labor_market_impacts), `job_exposure.csv` | `occ_code`, `observed_exposure` | Occupational AI exposure |
| Same release, `task_penetration.csv` | `task`, `penetration` | Observed AI penetration of individual tasks |
| [O*NET 30.0](https://www.onetcenter.org/database.html), `onet30_task_statements.xlsx` | `O*NET-SOC Code`, `Task` | Map task descriptions to occupations |
| [BLS 2024–2034 archive](https://www.bls.gov/emp/projections-archive/2024-34.zip), `bls_projections_2024_2034.zip` | `occupation.xlsx`, Table 1.2: occupation title, SOC code, occupation type, employment in 2024 and 2034, percentage change | Baseline employment and projected growth |

Anthropic's [methodology](https://www.anthropic.com/research/labor-market-impacts) explains the exposure measure. The saved release is identified in `anthropic_revision.json`; its README records attribution and licensing. BLS employment levels are reported in thousands and converted to people. Detailed occupations use BLS “Line item” rows; official major-group totals provide coverage denominators.

## Definitions and sample

Tasks are matched by lowercasing descriptions, collapsing whitespace, and trimming surrounding spaces. O*NET specializations are collapsed to seven-character SOC codes, with duplicate task descriptions removed within each occupation. Unmatched tasks remain missing rather than becoming zero.

Task breadth is the number of matched tasks with positive penetration divided by all matched tasks. Each task counts equally; this is not a share of working time. Occupational AI exposure comes directly from Anthropic and incorporates different task weights and usage information. Neither indicator is a worker's probability of replacement.

The analysis joins exposure, tasks, and BLS projections by SOC, retaining occupations with at least 95% task matching. The resulting sample has 722 occupations across 22 major groups. Detailed growth uses the published BLS percentage change. Group exposure and breadth use 2024 employment weights; group growth is 100 times summed 2034 employment divided by summed 2024 employment, minus 100. Bubble area represents matched-sample employment, and hover information reports its coverage of the official group total. Detailed dots are equal-sized.

Supplementary regressions, retained for reproducibility but not used in the article’s chart-based discussion, relate projected percentage employment growth to exposure and breadth. Coefficients represent a ten-percentage-point increase in the indicator. The main specification weights by 2024 employment; alternatives add major-group intercepts or use equal occupation weights. The table reports 95% HC3 robust confidence intervals with Student-t critical values. These describe model-based uncertainty across occupations, not BLS forecast uncertainty; they do not model within-group error dependence. Projections of net employment do not identify AI-caused displacement.

## Code and outputs

[code/reproduce.py](code/reproduce.py) runs four numbered stages: setup, task matching, projection analysis and regressions, and the English interactive chart. Paths resolve relative to the project, and output directories are created automatically.

| Code | Role |
|---|---|
| `code/reproduce.py` | Entry point; rebuild task matches and run the article workflow |
| `code/build_interactive_sample.py` | Clean BLS projections, match occupations, aggregate groups, and construct the linked Plotly chart |
| `code/regress_projections.py` | Estimate OLS/WLS models and save coefficients, intervals, and a supplementary table |
| `code/build_blog_assets.py` | Produce the English chart; optionally copy deployment assets and create the download package for the website |

| Output | Connection to the article |
|---|---|
| `results/interactive.html` | English offline Plotly visualization: group selection, occupation search, metric switching, and task details |
| `data/processed/projections_2024_2034_task_sample.csv` | The 722 detailed occupations plotted and used in regressions |
| `data/processed/projections_major_groups.csv` | Employment-weighted bubbles and coverage of each major group |
| `results/tasks/task_matches.csv`, `soc_task_metrics.csv` | Task panel, matching coverage, and task breadth |
| `results/projection_patterns/regressions.csv`, `regression_table.md` | Supplementary regression estimates; not displayed or used to draw the article’s conclusions |

The article and decorative illustration are maintained in the separate website repository. Ordinary analysis reproduction does not edit or render the website. Earlier OEWS/CPS explorations are outside the current article's replication workflow.

## Reproducing the analysis

1. Download this repository with its `code/`, `data/`, and `results/` folders intact. Prepare Python 3.12 and install the packages listed in `requirements.txt`.
2. Open `code/reproduce.py` and run it with Python. The saved inputs allow the complete workflow to run without network access or Quarto.
3. Open `results/interactive.html` in a browser and inspect the rebuilt CSV and Markdown tables. Select a group, search for an occupation to isolate its dot, and clear the search to restore the group.

The code checks unique SOC joins, consistent task matches, reconciliation of group employment totals, and coverage bounds. The regressions and chart data are generated from the same retained sample. No random sampling is used.
