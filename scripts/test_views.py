"""Local validation of T2.4 view definitions against the minimal
column set actually exposed by the DBRepo views.

The DBRepo UI does not allow computed columns or multi-column join
predicates, so the views registered in DBRepo (and mirrored in
database/views.sql) intentionally:

  * v_investment_sector_breakdown
      - returns the three raw investment values per
        (country, year, ceparema) for non-TOT_CEPA rows
      - does NOT expose country_name, activity_name,
        inv_corp_total, or inv_total

  * v_investment_national_totals
      - returns TOT_CEPA rows joined with macro indicators,
        but the macro LEFT JOIN matches on country_code only
        (no year predicate), so each TOT_CEPA row is multiplied
        by the number of macro records for the country
      - does NOT expose inv_corp_total, inv_total, inv_per_capita

  * v_ml_regression_features
      - subset of v_investment_national_totals with NULL filters
      - does NOT expose log_gdp_per_capita, log_population,
        log_inv_per_capita, inv_per_capita

This test asserts only what the views actually do. All derived
columns and the proper (country_code, year) macro join are
re-applied in pandas inside notebooks/investment_analysis.ipynb
(T2.6), and that pipeline's end-to-end output is verified against
the original local-file baseline. This file is for SQL-level
sanity-checking when iterating on views.sql, not a parity check.

Run:  python scripts/test_views.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
BREAKDOWN_CSV = REPO / "data" / "processed" / "20260505_investments_sector_breakdown.csv"
TOTALS_CSV    = REPO / "data" / "processed" / "20260505_investments_national_totals.csv"
VIEWS_SQL     = REPO / "database" / "views.sql"


def build_base_tables(con: duckdb.DuckDBPyConnection) -> None:
    """Reconstruct the 3NF base tables from the notebook's processed CSVs."""
    breakdown = pd.read_csv(BREAKDOWN_CSV)
    totals    = pd.read_csv(TOTALS_CSV)

    country = (
        pd.concat([breakdown[["geo", "country_name"]], totals[["geo", "country_name"]]])
        .drop_duplicates()
        .rename(columns={"geo": "country_code"})
        .sort_values("country_code")
    )
    activity = (
        pd.concat([breakdown[["ceparema", "activity"]], totals[["ceparema", "activity"]]])
        .drop_duplicates()
        .rename(columns={"ceparema": "ceparema_code", "activity": "activity_name"})
        .sort_values("ceparema_code")
    )
    macro = (
        totals[["geo", "year", "population", "gdp_per_capita"]]
        .drop_duplicates(subset=["geo", "year"])
        .rename(columns={"geo": "country_code"})
    )
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

    # --- v_investment_sector_breakdown ---
    print("\nv_investment_sector_breakdown")
    bd = con.execute("SELECT * FROM v_investment_sector_breakdown").df()
    check(len(bd) > 0, "non-empty result")
    check("TOT_CEPA" not in set(bd["ceparema_code"]), "excludes TOT_CEPA aggregate")
    check(bd[["year", "country_code", "ceparema_code"]].duplicated().sum() == 0,
          "primary key (year, country_code, ceparema_code) unique")
    expected_cols = {"year", "country_code", "ceparema_code", "inv_gov", "inv_corp_spec", "inv_corp_anc"}
    check(set(bd.columns) == expected_cols,
          f"exposes exactly {sorted(expected_cols)}",
          f"got {sorted(bd.columns)}")

    # --- v_investment_national_totals ---
    print("\nv_investment_national_totals")
    tt = con.execute("SELECT * FROM v_investment_national_totals").df()
    check(len(tt) > 0, "non-empty result")
    check(set(tt["ceparema_code"]) == {"TOT_CEPA"}, "contains only TOT_CEPA rows")
    # Cartesian explosion is expected here because the macro join lacks
    # a year predicate, so (year, country_code) is NOT unique. This is
    # documented in views.sql.
    expected_cols = {
        "year", "country_code", "country_name", "ceparema_code", "activity_name",
        "inv_gov", "inv_corp_spec", "inv_corp_anc", "gdp_per_capita", "population",
    }
    check(set(tt.columns) == expected_cols,
          f"exposes exactly {sorted(expected_cols)}",
          f"got {sorted(tt.columns)}")

    # --- v_ml_regression_features ---
    print("\nv_ml_regression_features")
    ml = con.execute("SELECT * FROM v_ml_regression_features").df()
    check(len(ml) > 0, "non-empty result")
    check(ml["gdp_per_capita"].notna().all() and ml["population"].notna().all(),
          "no NULL gdp_per_capita or population")
    expected_cols = {"year", "country_code", "country_name", "gdp_per_capita", "population"}
    check(set(ml.columns) == expected_cols,
          f"exposes exactly {sorted(expected_cols)}",
          f"got {sorted(ml.columns)}")

    print("\n" + ("ALL CHECKS PASSED" if not check.failed else "FAILURES DETECTED"))  # type: ignore[attr-defined]
    return 1 if check.failed else 0  # type: ignore[attr-defined]


if __name__ == "__main__":
    sys.exit(main())
