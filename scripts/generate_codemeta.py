"""
Generate codemeta.json from requirements.txt for T3.2 CodeMeta

Run from the repo root:
    python scripts/generate_codemeta.py
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
OUTPUT_FILE = PROJECT_ROOT / "codemeta.json"

PROJECT_NAME = "Environmental Protection Investment Analysis"
PROJECT_VERSION = "1.2.0"
GITHUB_URL = "https://github.com/danielwrnr/Environmental_Protection_Investment_Analysis"

AUTHORS = [
    {
        "name": "Daniel Werner",
        "orcid": "https://orcid.org/0009-0008-1686-7801"
    },
    {
        "name": "Georgios Papadopoulos",
        "orcid": "https://orcid.org/0009-0006-9997-3188"
    },
    {
        "name": "Johannes Oster",
        "orcid": "https://orcid.org/0009-0001-1344-1492"
    },
    {
        "name": "Luka Premuš",
        "orcid": "https://orcid.org/0009-0002-2938-9235"
    }
]

def read_dependencies_from_requirements():
    dependencies = []

    for line in REQUIREMENTS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if "==" not in line:
            raise ValueError(f"Requirement must use exact pin with ==: {line}")

        package_name, package_version = line.split("==", 1)

        dependencies.append({
            "@type": "SoftwareApplication",
            "name": package_name.strip(),
            "version": package_version.strip()
        })

    return dependencies


codemeta = {
    "@context": "https://doi.org/10.5063/schema/codemeta-2.0",
    "@type": "SoftwareSourceCode",
    "name": PROJECT_NAME,
    "version": PROJECT_VERSION,
    "description": "A reproducible data science project analysing Eurostat environmental protection investment data with DBRepo and machine learning.",
    "author": [
        {
            "@type": "Person",
            "name": author["name"],
            "@id": author["orcid"]
        }
        for author in AUTHORS
    ],
    "license": "https://spdx.org/licenses/MIT.html",
    "programmingLanguage": "Python",
    "runtimePlatform": "Python >=3.10",
    "softwareRequirements": read_dependencies_from_requirements(),
    "codeRepository": GITHUB_URL
}

OUTPUT_FILE.write_text(
    json.dumps(codemeta, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8"
)

print(f"Generated {OUTPUT_FILE}")
print(f"Dependencies included: {len(codemeta['softwareRequirements'])}")