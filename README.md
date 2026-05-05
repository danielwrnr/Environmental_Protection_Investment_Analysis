# Environmental Protection Investment Analysis
This project analyzes environmental protection investments across EU countries (2014–2022) using Eurostat data. It explores the relationship between national wealth and sustainability spending through data preprocessing, exploratory analysis, clustering and predictive modeling (Linear Regression and Random Forest).


##  Setup

Dependencies are listed in `requirements.txt` at the project root. They are installed directly from the first cell of `notebooks/investment_analysis.ipynb`:

```python
%pip install -r ../requirements.txt
```

Run this cell before executing any other part of the notebook.


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
- To support multiple runs per day, the pattern can be extended to `<YYYY-MM-DD>_<HH-MM>_<descriptor>.<ext>` if needed.