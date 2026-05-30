# Environmental Protection Investment Analysis
This project analyzes environmental protection investments across EU countries (2014–2022) using Eurostat data. It explores the relationship between national wealth and sustainability spending through data preprocessing, exploratory analysis, clustering and predictive modeling (Linear Regression and Random Forest).


##  Requirements and Installation

### Software requirements

- Python: 3.11.14
- pip (package manager)

### Installation

Install dependencies from the project root or directly within the notebook environment. 

**Option 1 (recommended)**

Run the following cell in any notebook before executing any other part of the notebook. This cell is already included in the provided notebooks.

```python
%pip install -r ../requirements.txt
```

**Option 2 (Terminal)**

From the project root:

```bash
pip install -r ../requirements.txt
```

## Reproducibility Instructions (Step-by-step)

1. Clone the repository: 

```bash
git clone https://github.com/danielwrnr/Environmental_Protection_Investment_Analysis.git
```

2. Navigate to the project folder 

```bash
cd Environmental_Protection_Investment_Analysis
```

3. Open the analysis notebook: notebooks/investment_analysis.ipynb

4. Install dependencies (see above)
5. Run the notebook cells. The generated outputs will be written to 
- data/
- figures/
- models/
- results/


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


## Inputs

The project uses the following Eurostat input datasets: `ENV_AC_EPIGG1`, `ENV_AC_EPISSP1`, `ENV_AC_EPIAP1`, `SDG_08_10`, and `DEMO_PJAN`

## Outputs 

...


## Licences

This project separates among three categories of artefacts: input data, software/code, and produced/output data. These categories are licensed separately because they have different rights holders and reuse conditions.

### Input data

The input data are reused from Eurostat and remain subject to the Eurostat copyright notice and free reuse of data policy. This is the official Eurostat reuse policy for statistical data and metadata.

The intended use is permitted because Eurostat allows reuse of statistical data and metadata for both non commercial and commercial purposes. No payment or  written licence is needed, but the source must be indicated and modifications must be clearly stated. This project acknowledges Eurostat as the source of the input data and documents that the data were processed for analysis and machine learning.

Obligations: any reuse of the input data or derived outputs should acknowledge Eurostat as the source and state that the data have been modified from the original Eurostat datasets. No ShareAlike obligation was identified.

Eurostat copyright notice and free reuse policy: https://ec.europa.eu/eurostat/help/copyright-notice

### Software and code

The software and code in this repository are licensed under the **MIT License**. This includes notebooks, scripts, SQL files and other implementation files specific to this project. The full licence text is provided in the repository root as `LICENSE`.

The MIT License was chosen because it is a flexible, minimally restrictive open-source licence that allows reuse, modification, distribution, and adaptation of our project code. This is appropriate for a reproducible open project because others can inspect, rerun, and extend the analysis.

The MIT License applies only to the project software/code. It does not apply to the Eurostat input data and does not change the Eurostat reuse terms. This makes it compatible with the input data licence/reuse terms. Namely users may reuse the code under MIT but they must still acknowledge Eurostat as the source of the input data and indicate any modifications to the data. The MIT License does not prevent this attribution and does not impose additional restrictions on the reused Eurostat data.

### Produced and output data

Produced and output artefacts are licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)** unless otherwise stated in a specific deposit record. This includes generated datasets, result files, prediction outputs, figures and trained model artefacts.

CC BY 4.0 was chosen because it allows reuse, sharing and adaptation with attribution. It is appropriate for open research outputs and is compatible with the Eurostat reuse terms because it preserves attribution obligations and allows the project to state that the outputs are derived from modified Eurostat data.

The CC BY 4.0 licence will also be stated in the metadata of each deposit that contains produced or output artefacts.

## Contributors

- Daniel Werner, ORCID: https://orcid.org/0009-0008-1686-7801
- Georgios Papadopoulos, ORCID: https://orcid.org/0009-0006-9997-3188
- Johannes Oster, ORCID: https://orcid.org/0009-0001-1344-1492
- Luka Premus, ORCID: https://orcid.org/0009-0002-2938-9235

## Zenodo DOI

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20455989.svg)](https://doi.org/10.5281/zenodo.20455989)

The badge points to the **concept DOI**, which always resolves to the latest version of the deposit. The Zenodo record is auto-archived from the GitHub repository via the GitHub-Zenodo integration.

Citation metadata is also provided in `CITATION.cff` at the repository root.
