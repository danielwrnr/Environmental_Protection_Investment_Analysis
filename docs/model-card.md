# Model Card: Environmental Protection Investment Prediction Models

## Model Description
This document provides details about the two predictive models trained for the Environmental Protection Investment Analysis project. The models include a Linear Regression model and a Random Forest Regressor. These models aim to predict environmental protection investments using macroeconomic indicators as features, specifically focusing on the relationship between national wealth (GDP) and sustainability spending across EU countries.

## Intended Use
These models are intended for academic research and exploratory analysis within the field of environmental economics. They provide a baseline for understanding how macroeconomic factors might influence environmental investments at a national level. Researchers and policy analysts can use these models to identify broad trends and potential correlations between economic wealth and green spending.

## Out-of-scope Uses
The models are strictly out-of-scope for making direct policy decisions or financial investment allocations. They should not be used for causal inference, as they rely on observational data and simplified macroeconomic indicators that do not capture the full complexity of national environmental policies. Additionally, using these models to predict outcomes for non-EU countries or time periods far outside the 2014-2022 range is not recommended.

## Training Data
The models were trained using a merged dataset derived from five public Eurostat datasets, covering the period from 2014 to 2022. The datasets include macroeconomic indicators such as Real GDP per Capita (DOI: 10.2908/SDG_08_10) and Population (DOI: 10.2908/DEMO_PJAN), as well as environmental protection investments by governments and corporations (DOIs: 10.2908/ENV_AC_EPIGG1, 10.2908/ENV_AC_EPISSP1, 10.2908/ENV_AC_EPIAP1). The data was preprocessed to resolve missing values and aggregated at the national level.

## Evaluation Results
The models were evaluated using standard regression metrics, including Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and R-squared (R2). The evaluation was performed on a held-out test set to ensure an unbiased estimate of model performance. The Random Forest model demonstrated superior predictive capability, explaining roughly 71.7% of the variance, compared to 55.6% for the Linear Regression model.

| Model | MAE | RMSE | R2 |
|---|---|---|---|
| Linear Regression | 0.335 | 0.417 | 0.556 |
| Random Forest | 0.272 | 0.333 | 0.717 |

## Limitations
Both models exhibit limitations due to the relatively simple set of features used for prediction. The reliance on broad macroeconomic indicators means that specific, localized policy shifts or external economic shocks are not captured effectively. Furthermore, the limited sample size associated with country-year aggregations limits the predictive power and generalization capabilities of the models.

## Ethical Considerations
While the data consists of aggregated national statistics and does not contain Personally Identifiable Information (PII), ethical considerations remain regarding the interpretation of the results. There is a risk that the models could be misinterpreted to justify reduced environmental spending in lower-GDP nations under the assumption that green investment is inherently a "luxury" of wealthier countries. Care must be taken to communicate the models' uncertainties and the observational nature of the data.

## Licence
The trained models and associated artifacts are distributed under the Creative Commons Attribution 4.0 International (CC BY 4.0) license. This open license permits free use, sharing, and adaptation of the models by anyone, provided that appropriate credit is given to the original authors. We encourage downstream users to adhere to open science principles when reusing these assets.
