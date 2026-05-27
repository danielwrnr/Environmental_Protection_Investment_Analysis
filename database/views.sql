-- ============================================================
-- T2.4 View definitions (DBRepo / MariaDB)
-- ============================================================
-- Three SQL views denormalise the 3NF base schema into shapes
-- consumed by the ML pipeline (see notebooks/investment_analysis.ipynb).
--
-- Semantics notes:
--   * inv_gov / inv_corp_spec / inv_corp_anc:
--       Negative source values (e.g. Estonia 2021-2022 inv_gov)
--       are clipped to 0 via CASE WHEN x < 0 THEN 0 ELSE x END.
--       NULLs are preserved (CASE returns NULL when the test
--       evaluates to NULL). The CASE form is engine-portable
--       (MariaDB GREATEST returns NULL on any NULL arg, but
--       DuckDB's GREATEST is NULL-skipping - hence avoid it).
--   * inv_corp_total and inv_total:
--       Treat NULLs as 0 (matches notebook .fillna(0) before sum).
--   * Year filter (2014-2022) is enforced at load time (T2.5),
--       not in the views.

-- --------------------------------------------------------------
-- View 1: v_investment_sector_breakdown
-- Per-sector environmental investment facts, joined with country
-- and CEPA activity names. Excludes the TOT_CEPA aggregate row
-- (use v_investment_national_totals for totals).
-- --------------------------------------------------------------
CREATE OR REPLACE VIEW v_investment_sector_breakdown AS
SELECT
    ei.year                                                                       AS year,
    ei.country_code                                                               AS country_code,
    c.country_name                                                                AS country_name,
    ei.ceparema_code                                                              AS ceparema_code,
    ea.activity_name                                                              AS activity_name,
    CASE WHEN ei.inv_gov < 0 THEN 0 ELSE ei.inv_gov END                                                       AS inv_gov,
    CASE WHEN ei.inv_corp_spec < 0 THEN 0 ELSE ei.inv_corp_spec END                                                 AS inv_corp_spec,
    CASE WHEN ei.inv_corp_anc < 0 THEN 0 ELSE ei.inv_corp_anc END                                                  AS inv_corp_anc,
    COALESCE(CASE WHEN ei.inv_corp_spec < 0 THEN 0 ELSE ei.inv_corp_spec END, 0)
        + COALESCE(CASE WHEN ei.inv_corp_anc < 0 THEN 0 ELSE ei.inv_corp_anc END, 0)                               AS inv_corp_total,
    COALESCE(CASE WHEN ei.inv_gov < 0 THEN 0 ELSE ei.inv_gov END, 0)
        + COALESCE(CASE WHEN ei.inv_corp_spec < 0 THEN 0 ELSE ei.inv_corp_spec END, 0)
        + COALESCE(CASE WHEN ei.inv_corp_anc < 0 THEN 0 ELSE ei.inv_corp_anc END, 0)                               AS inv_total
FROM Environmental_Investment ei
JOIN Country c                 ON ei.country_code  = c.country_code
JOIN Environmental_Activity ea ON ei.ceparema_code = ea.ceparema_code
WHERE ei.ceparema_code <> 'TOT_CEPA';

-- --------------------------------------------------------------
-- View 2: v_investment_national_totals
-- National per-year totals (ceparema_code = 'TOT_CEPA') enriched
-- with population and GDP per capita. Adds inv_per_capita.
-- Used as the input table for regression and clustering.
-- --------------------------------------------------------------
CREATE OR REPLACE VIEW v_investment_national_totals AS
SELECT
    ei.year                                                                       AS year,
    ei.country_code                                                               AS country_code,
    c.country_name                                                                AS country_name,
    ei.ceparema_code                                                              AS ceparema_code,
    ea.activity_name                                                              AS activity_name,
    CASE WHEN ei.inv_gov < 0 THEN 0 ELSE ei.inv_gov END                                                       AS inv_gov,
    CASE WHEN ei.inv_corp_spec < 0 THEN 0 ELSE ei.inv_corp_spec END                                                 AS inv_corp_spec,
    CASE WHEN ei.inv_corp_anc < 0 THEN 0 ELSE ei.inv_corp_anc END                                                  AS inv_corp_anc,
    COALESCE(CASE WHEN ei.inv_corp_spec < 0 THEN 0 ELSE ei.inv_corp_spec END, 0)
        + COALESCE(CASE WHEN ei.inv_corp_anc < 0 THEN 0 ELSE ei.inv_corp_anc END, 0)                               AS inv_corp_total,
    COALESCE(CASE WHEN ei.inv_gov < 0 THEN 0 ELSE ei.inv_gov END, 0)
        + COALESCE(CASE WHEN ei.inv_corp_spec < 0 THEN 0 ELSE ei.inv_corp_spec END, 0)
        + COALESCE(CASE WHEN ei.inv_corp_anc < 0 THEN 0 ELSE ei.inv_corp_anc END, 0)                               AS inv_total,
    m.population                                                                  AS population,
    (COALESCE(CASE WHEN ei.inv_gov < 0 THEN 0 ELSE ei.inv_gov END, 0)
        + COALESCE(CASE WHEN ei.inv_corp_spec < 0 THEN 0 ELSE ei.inv_corp_spec END, 0)
        + COALESCE(CASE WHEN ei.inv_corp_anc < 0 THEN 0 ELSE ei.inv_corp_anc END, 0)
    ) / NULLIF(m.population, 0)                                                   AS inv_per_capita,
    m.gdp_per_capita                                                              AS gdp_per_capita
FROM Environmental_Investment ei
JOIN Country c                       ON ei.country_code  = c.country_code
JOIN Environmental_Activity ea       ON ei.ceparema_code = ea.ceparema_code
LEFT JOIN Macroeconomic_Indicator m  ON m.country_code   = ei.country_code
                                    AND m.year           = ei.year
WHERE ei.ceparema_code = 'TOT_CEPA';

-- --------------------------------------------------------------
-- View 3: v_ml_regression_features
-- ML-ready feature table built on v_investment_national_totals.
-- Applies LN(1 + x) (log1p) transformations matching the notebook
-- preprocessing for the GDP -> investment regression, and drops
-- rows with any NULL input. Consumed directly by T2.6.
-- --------------------------------------------------------------
CREATE OR REPLACE VIEW v_ml_regression_features AS
SELECT
    year,
    country_code,
    country_name,
    LN(1 + gdp_per_capita) AS log_gdp_per_capita,
    LN(1 + population)     AS log_population,
    LN(1 + inv_per_capita) AS log_inv_per_capita
FROM v_investment_national_totals
WHERE gdp_per_capita IS NOT NULL
  AND population     IS NOT NULL
  AND inv_per_capita IS NOT NULL;
