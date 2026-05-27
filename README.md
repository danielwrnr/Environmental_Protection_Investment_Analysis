# Environmental Protection Investment Analysis
This project analyzes environmental protection investments across EU countries (2014–2022) using Eurostat data. It explores the relationship between national wealth and sustainability spending through data preprocessing, exploratory analysis, clustering and predictive modeling (Linear Regression and Random Forest).


##  Setup

Dependencies are listed in `requirements.txt` at the project root. They are installed directly from the first cell of `notebooks/investment_analysis.ipynb`:

```python
%pip install -r ../requirements.txt
```

Run this cell before executing any other part of the notebook.


## Database views

The 3NF base schema (`database/schema.sql`) is denormalised by three SQL views (`database/views.sql`) for consumption by the ML pipeline. All views clip negative investment values to zero while preserving NULLs.

| View | Purpose | Grain |
|---|---|---|
| `v_investment_sector_breakdown` | Per-CEPA-category investments joined with country and activity names. Adds derived `inv_corp_total` and `inv_total`. Excludes the `TOT_CEPA` aggregate. Used for trend analysis and category exploration. | (year, country_code, ceparema_code), excluding `TOT_CEPA` |
| `v_investment_national_totals` | National totals (`ceparema_code = 'TOT_CEPA'`) enriched with `population`, `gdp_per_capita`, and derived `inv_per_capita`. Used as the source for the regression and clustering pipelines. | One row per (year, country_code) |
| `v_ml_regression_features` | ML-ready feature table built on the totals view. Applies `LN(1 + x)` to `gdp_per_capita`, `population`, and `inv_per_capita`, and drops any row with a NULL input. Consumed directly by the regression notebook. | One row per (year, country_code) with no NULLs |

Correctness of the views is verified by `database/tests/test_views.py`, which reconstructs the base tables from the notebook's processed CSVs, runs the views in an in-process DuckDB engine (MariaDB-compatible for the SQL surface used here), and asserts:

- SQL invariants: PK uniqueness, value bounds (clipped to ≥ 0), `inv_total` and `inv_corp_total` arithmetic, `inv_per_capita = inv_total / population`, `log_x = LN(1 + x)`.
- Value-by-value parity against `data/processed/20260505_investments_*.csv` (the notebook outputs) within float tolerance.

Run with `python database/tests/test_views.py` (requires `duckdb` and `pandas`).

## File organisation

This section documents the naming convention.

### Folder structure

```
├── data/
│   ├── raw/                              # Original downloaded datasets
│   └── processed/                        # Cleaned and transformed datasets
├── figures/                              # Generated plots and visualisations
├── models/                               # Trained model artefacts
├── notebooks/
│   └── investment_analysis.ipynb         # Primary analysis and experiment notebook
├── results/                              # Model evaluation outputs and performance metrics
├── README.md                             # Project documentation
└── requirements.txt                      # Python package dependencies
```



### General Convention

All generated files are prefixed with a date (`YYYYMMDD`) for chronological ordering and traceability:

```
<YYYYMMDD>_<descriptor>.<extension>
```

- **Date prefix** (`YYYYMMDD`): the date on which the file was produced.
- **Descriptor**: a lowercase, underscore-separated label describing the file's content.
- **Extension**: file type

### Overview by File Type

| File type            | Location           | Pattern                                              |
|----------------------|--------------------|------------------------------------------------------|
| Raw data             | `data/raw/`        | `YYYYMMDD_raw_<dataset_code>.csv`                    |
| Processed data       | `data/processed/`  | `YYYYMMDD_<content_descriptor>.csv`                  |
| Figures              | `figures/`         | `YYYYMMDD_<chart_description>.png`                   |
| Model artefacts      | `models/`          | `YYYYMMDD_<algorithm>.joblib`            |
| Results              | `results/`         | `YYYYMMDD_<evaluation_descriptor>.csv`               |
| Main notebook        | `notebooks/`       | `investment_analysis.ipynb`                          |

---

## Notes on Reproducibility

- The date prefix in file names corresponds to the run date, not the date of the underlying data.
- Re-running the pipeline on the same day will overwrite same-date files unless output paths are parameterised to include a run ID or time suffix.
- To support multiple runs per day, the pattern has to be extended to `<YYYYMMDD>_<HH-MM>_<descriptor>.<extension>` if needed.