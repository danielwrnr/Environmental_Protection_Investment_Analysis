"""Local validation of T2.4 view definitions.

Uses DuckDB (in-process, supports GREATEST / LN / NULLIF / COALESCE
with MariaDB-compatible semantics for our cases) to:

  1. Build the 3NF base tables from the processed CSV
     (data/processed/20260505_investments_sector_breakdown.csv +
      data/processed/20260505_investments_national_totals.csv).
  2. Create the views from database/views.sql.
  3. Assert SQL invariants and diff view output against the
     notebook's processed CSVs.

Run:  python database/tests/test_views.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import duckdb
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
BREAKDOWN_CSV = REPO / "data" / "processed" / "20260505_investments_sector_breakdown.csv"
TOTALS_CSV    = REPO / "data" / "processed" / "20260505_investments_national_totals.csv"
VIEWS_SQL     = REPO / "database" / "views.sql"

FLOAT_TOL = 1e-6


def build_base_tables(con: duckdb.DuckDBPyConnection) -> None:
    """Reconstruct the 3NF base tables from the notebook's processed CSVs.

    The processed CSVs already contain everything we need: country code +
    name, ceparema code + activity, year, the three investment columns,
    population and gdp_per_capita. We re-split them into the four 3NF
    tables to test the views as they will run in DBRepo.
    """
    breakdown = pd.read_csv(BREAKDOWN_CSV)
    totals    = pd.read_csv(TOTALS_CSV)

    # Country dimension - union of codes seen in both views.
    country = (
        pd.concat([breakdown[["geo", "country_name"]], totals[["geo", "country_name"]]])
        .drop_duplicates()
        .rename(columns={"geo": "country_code"})
        .sort_values("country_code")
    )

    # Environmental activity dimension - includes TOT_CEPA.
    activity = (
        pd.concat([breakdown[["ceparema", "activity"]], totals[["ceparema", "activity"]]])
        .drop_duplicates()
        .rename(columns={"ceparema": "ceparema_code", "activity": "activity_name"})
        .sort_values("ceparema_code")
    )

    # Macroeconomic indicators - one row per (country, year) from totals.
    macro = (
        totals[["geo", "year", "population", "gdp_per_capita"]]
        .drop_duplicates(subset=["geo", "year"])
        .rename(columns={"geo": "country_code"})
    )

    # Investment fact table - sector rows + TOT_CEPA rows.
    inv_cols = ["year", "geo", "ceparema", "inv_gov", "inv_corp_spec", "inv_corp_anc"]
    investment = pd.concat([breakdown[inv_cols], totals[inv_cols]], ignore_index=True)
    investment = investment.rename(columns={"geo": "country_code", "ceparema": "ceparema_code"})

    con.execute("""
        CREATE TABLE Country (
            country_code VARCHAR PRIMARY KEY,
            country_name VARCHAR NOT NULL
        );
        CREATE TABLE Environmental_Activity (
            ceparema_code VARCHAR PRIMARY KEY,
            activity_name VARCHAR NOT NULL
        );
        CREATE TABLE Macroeconomic_Indicator (
            country_code VARCHAR,
            year INTEGER,
            population BIGINT,
            gdp_per_capita DECIMAL(15,2),
            PRIMARY KEY (country_code, year)
        );
        CREATE TABLE Environmental_Investment (
            country_code VARCHAR,
            year INTEGER,
            ceparema_code VARCHAR,
            inv_gov DECIMAL(15,2),
            inv_corp_spec DECIMAL(15,2),
            inv_corp_anc DECIMAL(15,2),
            PRIMARY KEY (country_code, year, ceparema_code)
        );
    """)
    con.register("country_df",    country)
    con.register("activity_df",   activity)
    con.register("macro_df",      macro)
    con.register("investment_df", investment)
    con.execute("INSERT INTO Country SELECT country_code, country_name FROM country_df;")
    con.execute("INSERT INTO Environmental_Activity SELECT ceparema_code, activity_name FROM activity_df;")
    con.execute("INSERT INTO Macroeconomic_Indicator SELECT country_code, year, population, gdp_per_capita FROM macro_df;")
    con.execute("""
        INSERT INTO Environmental_Investment
        SELECT country_code, year, ceparema_code, inv_gov, inv_corp_spec, inv_corp_anc
        FROM investment_df;
    """)


def create_views(con: duckdb.DuckDBPyConnection) -> None:
    raw = VIEWS_SQL.read_text()
    # Strip line comments first so leftover prose doesn't get parsed as SQL.
    lines = [ln for ln in raw.splitlines() if not ln.lstrip().startswith("--")]
    sql = "\n".join(lines)
    for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
        con.execute(stmt + ";")


def check(condition: bool, label: str, detail: str = "") -> None:
    mark = "PASS" if condition else "FAIL"
    print(f"  [{mark}] {label}" + (f"  -- {detail}" if detail and not condition else ""))
    if not condition:
        check.failed = True  # type: ignore[attr-defined]


def main() -> int:
    check.failed = False  # type: ignore[attr-defined]
    con = duckdb.connect()
    print(f"Building base tables from {BREAKDOWN_CSV.name} + {TOTALS_CSV.name}")
    build_base_tables(con)
    print(f"Creating views from {VIEWS_SQL.relative_to(REPO)}")
    create_views(con)

    # --- 1. Invariants on v_investment_sector_breakdown ---
    print("\nv_investment_sector_breakdown")
    bd = con.execute("SELECT * FROM v_investment_sector_breakdown").df()
    check(len(bd) > 0, "non-empty result")
    check("TOT_CEPA" not in set(bd["ceparema_code"]),
          "excludes TOT_CEPA aggregate")
    check(bd[["year", "country_code", "ceparema_code"]].duplicated().sum() == 0,
          "primary key (year, country_code, ceparema_code) unique")
    nn = bd.dropna(subset=["inv_gov", "inv_corp_spec", "inv_corp_anc"])
    check(((nn["inv_gov"] >= 0) & (nn["inv_corp_spec"] >= 0) & (nn["inv_corp_anc"] >= 0)).all(),
          "non-null investment values clipped >= 0")
    inv_total_check = (
        bd["inv_gov"].fillna(0) + bd["inv_corp_spec"].fillna(0) + bd["inv_corp_anc"].fillna(0)
    )
    check((bd["inv_total"] - inv_total_check).abs().max() < FLOAT_TOL,
          "inv_total = inv_gov + inv_corp_spec + inv_corp_anc (NULLs as 0)")

    # --- 2. Invariants on v_investment_national_totals ---
    print("\nv_investment_national_totals")
    tt = con.execute("SELECT * FROM v_investment_national_totals").df()
    check(len(tt) > 0, "non-empty result")
    check(set(tt["ceparema_code"]) == {"TOT_CEPA"},
          "contains only TOT_CEPA rows")
    check(tt[["year", "country_code"]].duplicated().sum() == 0,
          "primary key (year, country_code) unique - one row per country-year")
    pc_check = tt["inv_total"] / tt["population"]
    delta = (tt["inv_per_capita"] - pc_check).abs()
    check(delta.dropna().max() < 1e-9, "inv_per_capita = inv_total / population")

    # --- 3. Invariants on v_ml_regression_features ---
    print("\nv_ml_regression_features")
    ml = con.execute("SELECT * FROM v_ml_regression_features").df()
    check(len(ml) > 0, "non-empty result")
    check(ml.isnull().sum().sum() == 0, "no NULLs (all log inputs were non-NULL)")
    sample = tt.dropna(subset=["gdp_per_capita", "population", "inv_per_capita"]).iloc[0]
    expected = math.log1p(float(sample["gdp_per_capita"]))
    got = float(ml[(ml["country_code"] == sample["country_code"]) &
                   (ml["year"] == sample["year"])]["log_gdp_per_capita"].iloc[0])
    check(abs(expected - got) < 1e-9, "log_gdp_per_capita = LN(1 + gdp_per_capita)")

    # --- 4. Diff against notebook's processed CSVs ---
    print("\nDiff vs notebook processed CSVs")
    notebook_bd = pd.read_csv(BREAKDOWN_CSV).rename(
        columns={"geo": "country_code", "ceparema": "ceparema_code", "activity": "activity_name"}
    )
    key = ["year", "country_code", "ceparema_code"]
    merged_bd = bd.merge(notebook_bd, on=key, suffixes=("_view", "_nb"))
    check(len(merged_bd) == len(notebook_bd),
          "breakdown row count matches notebook",
          f"view={len(bd)} notebook={len(notebook_bd)} matched={len(merged_bd)}")
    for col in ["inv_gov", "inv_corp_spec", "inv_corp_anc", "inv_corp_total", "inv_total"]:
        diff = (merged_bd[f"{col}_view"].fillna(-1) - merged_bd[f"{col}_nb"].fillna(-1)).abs().max()
        check(diff < FLOAT_TOL, f"breakdown.{col} matches notebook (max abs diff {diff:g})")

    notebook_tt = pd.read_csv(TOTALS_CSV).rename(
        columns={"geo": "country_code", "ceparema": "ceparema_code", "activity": "activity_name"}
    )
    key2 = ["year", "country_code"]
    merged_tt = tt.merge(notebook_tt, on=key2, suffixes=("_view", "_nb"))
    check(len(merged_tt) == len(notebook_tt),
          "totals row count matches notebook",
          f"view={len(tt)} notebook={len(notebook_tt)} matched={len(merged_tt)}")
    for col in ["inv_gov", "inv_corp_spec", "inv_corp_anc", "inv_corp_total",
                "inv_total", "population", "gdp_per_capita", "inv_per_capita"]:
        diff = (merged_tt[f"{col}_view"].fillna(-1) - merged_tt[f"{col}_nb"].fillna(-1)).abs().max()
        # inv_per_capita is a division; allow slightly larger tolerance.
        tol = 1e-6 if col != "inv_per_capita" else 1e-6
        check(diff < tol, f"totals.{col} matches notebook (max abs diff {diff:g})")

    print("\n" + ("ALL CHECKS PASSED" if not check.failed else "FAILURES DETECTED"))  # type: ignore[attr-defined]
    return 1 if check.failed else 0  # type: ignore[attr-defined]


if __name__ == "__main__":
    sys.exit(main())
