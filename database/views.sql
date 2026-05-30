-- ============================================================
-- T2.4 View definitions (DBRepo / MariaDB)
-- ============================================================
-- These definitions reflect the views actually registered in the
-- live DBRepo deployment of this project. They were created via
-- the DBRepo UI, which has two constraints:
--   1. No computed columns. The UI only lets you pick existing
--      columns; expressions (`CASE WHEN x < 0 ...`, `a + b`,
--      `LN(1 + x)`) cannot be added to a view.
--   2. No multi-column join conditions. Only single-column
--      equality predicates can be specified per join.
--
-- Consequently the views below are intentionally minimal: no
-- clipping, no aggregation, no logarithmic transformations.
-- All derived columns the analysis needs - `inv_corp_total`,
-- `inv_total`, `inv_per_capita`, the `log_*` regression
-- features - and the per-row negative clipping are applied in
-- pandas after the REST fetch. See
-- notebooks/investment_analysis.ipynb (T2.6) and the
-- "Data loading from DBRepo" section of the README.

-- --------------------------------------------------------------
-- View 1: v_investment_sector_breakdown
-- --------------------------------------------------------------
-- NOTE: The two joins below are accidental self-joins introduced
-- when the view was created in the DBRepo UI - the join target
-- columns were selected from the wrong table. As a result the
-- view returns zero usable rows. The notebook ignores this view
-- and reconstructs the sector breakdown in pandas from the base
-- Environmental_Investment / Country / Environmental_Activity
-- tables.
CREATE OR REPLACE VIEW v_investment_sector_breakdown AS
SELECT
    ei.inv_corp_spec,
    ei.inv_gov,
    ei.inv_corp_anc,
    ei.country_code,
    ei.year,
    ei.ceparema_code
FROM Environmental_Investment ei
JOIN Country               c  ON c.country_name  = c.country_code
JOIN Environmental_Activity ea ON ea.activity_name = ea.ceparema_code
WHERE ea.ceparema_code <> 'TOT_CEPA';

-- --------------------------------------------------------------
-- View 2: v_investment_national_totals
-- --------------------------------------------------------------
-- NOTE: The LEFT JOIN on Macroeconomic_Indicator only matches on
-- country_code (the year predicate cannot be expressed in the
-- DBRepo UI), so each TOT_CEPA row is joined with every macro
-- record for the country: e.g. Austria/2014 is returned nine
-- times with nine different `gdp_per_capita` values. The
-- notebook fetches the base tables and joins on
-- (country_code, year) in pandas.
CREATE OR REPLACE VIEW v_investment_national_totals AS
SELECT
    ei.inv_corp_anc,
    ea.activity_name,
    ei.year,
    m.gdp_per_capita,
    ei.inv_corp_spec,
    ei.inv_gov,
    ei.country_code,
    c.country_name,
    ei.ceparema_code,
    m.population
FROM Environmental_Investment ei
LEFT OUTER JOIN Macroeconomic_Indicator m   ON ei.country_code  = m.country_code
JOIN            Country                  c  ON ei.country_code  = c.country_code
JOIN            Environmental_Activity   ea ON ei.ceparema_code = ea.ceparema_code
WHERE ei.ceparema_code = 'TOT_CEPA';

-- --------------------------------------------------------------
-- View 3: v_ml_regression_features
-- --------------------------------------------------------------
-- NOTE: The three `log_*` regression features and
-- `inv_per_capita` cannot be expressed here for the same reason
-- (no computed columns in the DBRepo UI). The notebook applies
-- LN(1 + x) in pandas. This view also inherits the cartesian
-- explosion from v_investment_national_totals.
CREATE OR REPLACE VIEW v_ml_regression_features AS
SELECT
    year,
    gdp_per_capita,
    country_name,
    country_code,
    population
FROM v_investment_national_totals
WHERE gdp_per_capita IS NOT NULL
  AND population     IS NOT NULL;
