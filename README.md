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


## Data loading from DBRepo

The experiment notebook (`notebooks/investment_analysis.ipynb`) loads all input data **exclusively from DBRepo via REST** — there are no local CSV file reads in the data-loading code (T2.6).

**API base URL:** `https://test.dbrepo.tuwien.ac.at/api/v1`
**Database ID:** `123289f2-5218-4b32-b962-5f3dafec1fe3`
**Persistent DOI:** [`10.82556/2wmj-nz26`](https://doi.org/10.82556/2wmj-nz26)
**Authentication:** none required — the database is `is_public=true` and reads work anonymously. Writes (not used by the analysis pipeline) would require HTTP Basic auth with a DBRepo account.

**Endpoints used by the notebook:**

| Method | Path | Purpose |
|---|---|---|
| GET | `/database/{db_id}/table/{table_id}/data?page=N&size=M` | Fetch base table rows, paginated |
| GET | `/database/{db_id}/view/{view_id}/data?page=N&size=M` | Fetch view rows (not used in the final notebook — see below) |
| GET | `/database/{db_id}/view/{view_id}` | Inspect a view's SQL definition and column list |

All requests send `Accept: application/json`. NULL columns are stripped from individual response objects but materialise as NaN once loaded into pandas.

### Why base tables instead of views

The three views from `database/views.sql` are registered in DBRepo (`v_investment_sector_breakdown`, `v_investment_national_totals`, `v_ml_regression_features`), but the DBRepo UI does not support computed columns or multi-column join conditions. As a result the live view definitions differ materially from `views.sql`:

- `v_investment_national_totals` is missing the `year` condition on the join to `Macroeconomic_Indicator`, which causes a cartesian explosion (Austria/2014 returns 9 rows with different `gdp_per_capita` values).
- `v_ml_regression_features` inherits that explosion and additionally has none of the `log_*` or `inv_per_capita` columns it should compute.
- `v_investment_sector_breakdown` is encoded with self-joins on the `Country` and `Environmental_Activity` tables and returns no usable rows.

The notebook therefore fetches the four base tables — `Country`, `Environmental_Activity`, `Macroeconomic_Indicator`, `Environmental_Investment` — and reproduces the view logic (joins, derived `inv_corp_total` / `inv_total` / `inv_per_capita`, negative clipping, log transformations) in pandas. The behaviour is equivalent to the pristine definitions in `database/views.sql`.

## Input dataset metadata (Croissant)

Each of the five Eurostat input datasets is described by a Croissant 1.0 JSON-LD record in `metadata/croissant/`:

| File | Eurostat dataset | DOI |
|---|---|---|
| `env_ac_epigg1.json` | Environmental protection investments by general government | [`10.2908/ENV_AC_EPIGG1`](https://doi.org/10.2908/ENV_AC_EPIGG1) |
| `env_ac_epissp1.json` | Environmental protection investments by specialist and secondary producers | [`10.2908/ENV_AC_EPISSP1`](https://doi.org/10.2908/ENV_AC_EPISSP1) |
| `env_ac_epiap1.json` | Environmental protection investments by ancillary producers | [`10.2908/ENV_AC_EPIAP1`](https://doi.org/10.2908/ENV_AC_EPIAP1) |
| `sdg_08_10.json` | Real GDP per capita (chain-linked volumes, base 2020) | [`10.2908/SDG_08_10`](https://doi.org/10.2908/SDG_08_10) |
| `demo_pjan.json` | Population on 1 January by age and sex | [`10.2908/DEMO_PJAN`](https://doi.org/10.2908/DEMO_PJAN) |

Each record describes the raw CSV (path, sha256, encoding), its categorical fields, the 2014–2022 year columns used by the analysis (with QUDT unit URIs from T2.3 — `https://qudt.org/vocab/unit/CCY_EUR`, `.../NUM`, `.../YR`), and the Eurostat reuse licence. All five validate against the official `mlcroissant` 1.0 validator; output captured in `docs/validation/croissant-validation.txt`.

## Database views

Three views are registered in DBRepo on top of the 3NF base schema (`database/schema.sql`); their definitions are mirrored in `database/views.sql`. They were created through the DBRepo UI, which does not allow computed columns or multi-column join conditions, so the views are intentionally minimal — no negative-value clipping, no derived totals, no logarithmic transformations.

| View | What it returns | Known limitation |
|---|---|---|
| `v_investment_sector_breakdown` | Intended to expose per-CEPA-category facts excluding `TOT_CEPA`. | Both joins are accidental self-joins on `Country` and `Environmental_Activity`, so the view returns no usable rows. |
| `v_investment_national_totals` | National totals (`ceparema_code = 'TOT_CEPA'`) joined with country names and macroeconomic indicators. | The `Macroeconomic_Indicator` join matches on `country_code` only — the year predicate cannot be expressed in the UI. Each TOT_CEPA row is therefore returned once per macro record for the same country (e.g. Austria/2014 returns nine rows). |
| `v_ml_regression_features` | Subset of the totals view that drops rows with NULL `gdp_per_capita` or `population`. | Missing all `log_*` columns and `inv_per_capita`; inherits the cartesian explosion from view 2. |

All clipping, derived columns, log transformations, the `(country_code, year)` macro join, and the country-scope filter are applied in pandas after the REST fetch — see `notebooks/investment_analysis.ipynb` and the "Data loading from DBRepo" section above. The notebook's run is verified end-to-end against the original local-file baseline (`results/20260505_reg_model_performance_comparison.csv`).

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
