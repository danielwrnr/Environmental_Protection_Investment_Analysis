import json
from pathlib import Path
from datetime import datetime, timezone

MADMP_FILE = Path("docs/dmp/maDMP-FINAL_Do_Rich_Countries_Invest_More_in_Saving_the_Planet__Analysis_of_Europe_s_Green_Investment_Landscape_20260530.json")

GITHUB_URL = "https://github.com/danielwrnr/Environmental_Protection_Investment_Analysis"
ZENODO_DOI = "https://doi.org/10.5281/zenodo.20455989"
DBREPO_DOI = "https://doi.org/10.82556/2wmj-nz26"

MODEL_DEPOSIT_DOI = "10.70124/wzjz7-cbj65"
GENERATED_DATA_DEPOSIT_DOI = "10.70124/cyysd-qvw90"
FINAL_DMP_DOI = "10.70124/fcqeh-0vp73"
INITIAL_DMP_DOI = "10.70124/fqq87-vwa35"

EUROSTAT_REUSE_TERMS = "https://ec.europa.eu/eurostat/help/copyright-notice"


with MADMP_FILE.open("r", encoding="utf-8") as f:
    madmp = json.load(f)

# DMP level metadata 

madmp["title"] = (
    "Final maDMP: Do Rich Countries Invest More in Saving the Planet? "
    "Analysis of Europe’s Green Investment Landscape"
)

madmp["language"] = "eng"

madmp["dmp_id"] = {
    "identifier": FINAL_DMP_DOI,
    "type": "doi"
}

madmp["modified"] = datetime.now(timezone.utc).isoformat()

madmp["ethical_issues_exist"] = "no"

# Related identifiers

madmp["related_identifier"] = [
    {
        "identifier": GITHUB_URL,
        "type": "url",
        "relation": "is_documented_by",
        "descriptor": "GitHub repository containing source code and workflow"
    },
    {
        "identifier": ZENODO_DOI,
        "type": "doi",
        "relation": "is_supplemented_by",
        "descriptor": "Archived software release"
    },
    {
        "identifier": DBREPO_DOI,
        "type": "doi",
        "relation": "is_derived_from",
        "descriptor": "DBRepo database used as structured source data"
    },
    {
        "identifier": MODEL_DEPOSIT_DOI,
        "type": "doi",
        "relation": "is_supplement_to",
        "descriptor": "Related trained model deposit"
    },
    {
        "identifier": GENERATED_DATA_DEPOSIT_DOI,
        "type": "doi",
        "relation": "has_part",
        "descriptor": "Generated output data deposit"
    },
    {
        "identifier": INITIAL_DMP_DOI,
        "type": "doi",
        "relation": "continues",
        "descriptor": "Initial DMP continued by this final DMP"
    }
]

#  Add dataset IDs P1-P7 and R1-R5

dataset_ids = [
    "P1", "P2", "P3", "P4", "P5", "P6", "P7",
    "R1", "R2", "R3", "R4", "R5"
]

for dataset, dataset_id in zip(madmp.get("dataset", []), dataset_ids):
    dataset["dataset_id"] = {
        "identifier": dataset_id,
        "type": "other"
    }

# Fix Eurostat reused dataset licence references
# R1-R5 are the reused Eurostat input datasets which are the last five datasets.

for dataset in madmp.get("dataset", [])[-5:]:
    dataset["rights"] = [
        {
            "license_ref": EUROSTAT_REUSE_TERMS,
            "description": (
                "Eurostat copyright notice and free reuse policy. "
                "Reuse is permitted with source attribution and indication of modifications."
            )
        }
    ]

# Write back formatted JSON

with MADMP_FILE.open("w", encoding="utf-8") as f:
    json.dump(madmp, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"Updated {MADMP_FILE}")