# Model Card: Linear Regression Model for Environmental Protection Investment

## Model Description
This document provides details about the Linear Regression model trained for the Environmental Protection Investment Analysis project. This baseline model predicts environmental protection investments using macroeconomic indicators as features, specifically focusing on the relationship between national wealth (GDP), population, and sustainability spending across EU countries.

## Intended Use
This model is intended for academic research and exploratory analysis within the field of environmental economics. It provides a simple linear baseline for understanding how macroeconomic factors might influence environmental investments at a national level. Researchers and policy analysts can use this model to identify broad linear trends and correlations.

## Out-of-scope Uses
The model is strictly out-of-scope for making direct policy decisions or financial investment allocations. It should not be used for causal inference, as it relies on observational data and simplified macroeconomic indicators that do not capture the full complexity of national environmental policies. Additionally, using this model to predict outcomes for non-EU countries or time periods far outside the 2014-2022 range is not recommended.

## Training Data
The model was trained using a merged dataset derived from five public Eurostat datasets, covering the period from 2014 to 2022. The datasets include macroeconomic indicators such as Real GDP per Capita (DOI: 10.2908/SDG_08_10) and Population (DOI: 10.2908/DEMO_PJAN), as well as environmental protection investments by governments and corporations (DOIs: 10.2908/ENV_AC_EPIGG1, 10.2908/ENV_AC_EPISSP1, 10.2908/ENV_AC_EPIAP1). The data was preprocessed to resolve missing values and aggregated at the national level.

## Evaluation Results
The model was evaluated using standard regression metrics, including Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and R-squared (R2). The evaluation was performed on a held-out test set to ensure an unbiased estimate of model performance.

| Model | MAE | RMSE | R2 |
|---|---|---|---|
| Linear Regression | 0.335 | 0.417 | 0.556 |

## Limitations
The Linear Regression model exhibits significant limitations due to the assumption of linearity between macroeconomic indicators and environmental investments, which are often non-linear. The reliance on broad macroeconomic indicators means that specific, localized policy shifts or external economic shocks are not captured effectively. Furthermore, the limited sample size associated with country-year aggregations limits the predictive power and generalization capabilities of the model.

## Ethical Considerations
While the data consists of aggregated national statistics and does not contain Personally Identifiable Information (PII), ethical considerations remain regarding the interpretation of the results. There is a risk that the model could be misinterpreted to justify reduced environmental spending in lower-GDP nations under the assumption that green investment is inherently a "luxury" of wealthier countries. Care must be taken to communicate the model's uncertainties and the observational nature of the data.

## FAIR4ML Metadata
The FAIR4ML-compliant metadata for this model is registered in [20260505_linear_regression_fair4ml.jsonld](20260505_linear_regression_fair4ml.jsonld).

## Licence
The trained model and associated artifacts are distributed under the Creative Commons Attribution 4.0 International (CC BY 4.0) license. This open license permits free use, sharing, and adaptation of the model by anyone, provided that appropriate credit is given to the original authors. We encourage downstream users to adhere to open science principles when reusing these assets.
