# Semantic Mapping

This document describes the semantic mappings for the DBRepo schema and views used in the project.

This semantic mapping covers:
- the normalized DBRepo schema defined in `database/schema.sql` and 
- the derived attributes exposed by the DBRepo views in `database/views.sql`. 

Raw Eurostat download columns and temporary notebook variables are not mapped unless they are part of the final DBRepo schema or views.

## Ontology and vocabulary choice

The semantic mappings are based primarily on the Eurostat reference metadata for the datasets used in the project. General statistical dimensions such as `year` are mapped to SDMX (Statistical Data and Metadata eXchange).

Domain-specific attributes are mapped to the relevant Eurostat metadata:
- environmental protection investment and activity attributes are mapped to the Eurostat Environmental Protection Expenditure Accounts (EPEA) metadata and CEPA terminology, 
- GDP per capita is mapped to the Eurostat `sdg_08_10` metadata and 
- population is mapped to the Eurostat `demo_pop` metadata. 

Following Eurostat metadata structures are used as supporting references for the semantic mappings, not as replacements for each attribute mappings themselves.

| Metadata type       | Structure | Full name                            |
| ------------------- | --------- | ------------------------------------ |
| EPEA metadata       | SIMS      | Single Integrated Metadata Structure |
| GDP metadata        | ESMS      | Euro SDMX Metadata Structure         |
| Population metadata | ESMS      | Euro SDMX Metadata Structure         |

Generic vocabularies such as schema.org and Dublin Core are not needed because more specific statistical and domain-specific metadata sources are available.

## Source metadata references

- SDMX (Statistical Data and Metadata eXchange): https://sdmx.org/
- Eurostat EPEA metadata, SIMS: https://ec.europa.eu/eurostat/cache/metadata/en/env_ac_epea_sims.htm
- Eurostat real GDP per capita metadata (`sdg_08_10`), ESMS: https://ec.europa.eu/eurostat/cache/metadata/en/sdg_08_10_esmsip2.htm
- Eurostat population metadata (`demo_pop`), ESMS: https://ec.europa.eu/eurostat/cache/metadata/en/demo_pop_esms.htm


## Base DBRepo schema mappings


| DBRepo table | Attribute | Description | Ontology / Vocabulary | Semantic concept or reference | Justification |
|---|---|---|---|---|---|
| `Country` | `country_code` | Country or geographic area code | SDMX | Reference area | Identifies the geographic area of the statistical observation. |
| `Country` | `country_name` | Human-readable country name | SDMX / Eurostat geography | Reference area label | Provides the readable label for the country code. |
| `Environmental_Activity` | `ceparema_code` | Environmental protection activity code | Eurostat EPEA / CEPA | Classification of Environmental Protection Activities | Identifies the environmental protection activity category used in the investment data. |
| `Environmental_Activity` | `activity_name` | Human-readable environmental protection activity name | Eurostat EPEA / CEPA | CEPA activity label | Provides the readable label for the environmental protection activity category. |
| `Macroeconomic_Indicator` | `country_code` | Country or geographic area code | SDMX | Reference area | Links macroeconomic observations to a country. |
| `Macroeconomic_Indicator` | `year` | Observation year | SDMX | Time period | Identifies the time period of the statistical observation. |
| `Macroeconomic_Indicator` | `population` | Population count | Eurostat `demo_pop` / `DEMO_PJAN` | Population on 1 January | Describes the population value used for normalization and per capita analysis. |
| `Macroeconomic_Indicator` | `gdp_per_capita` | Real GDP per capita | Eurostat `sdg_08_10` | Real GDP per capita | Describes the economic indicator used in the analysis. |
| `Environmental_Investment` | `country_code` | Country or geographic area code | SDMX | Reference area | Links investment observations to a country. |
| `Environmental_Investment` | `year` | Observation year | SDMX | Time period | Identifies the time period of the investment observation. |
| `Environmental_Investment` | `ceparema_code` | Environmental protection activity code | Eurostat EPEA / CEPA | Classification of Environmental Protection Activities | Links investment observations to an environmental protection activity category. |
| `Environmental_Investment` | `inv_gov` | Government environmental protection investment | Eurostat EPEA / `ENV_AC_EPIGG1` | Environmental protection investment of general government | Monetary investment measure for the government sector. |
| `Environmental_Investment` | `inv_corp_spec` | Corporate specialist producer investment | Eurostat EPEA / `ENV_AC_EPISSP1` | Environmental protection investment of corporations as specialist and secondary producers | Monetary investment measure for specialist and secondary producers. |
| `Environmental_Investment` | `inv_corp_anc` | Corporate ancillary producer investment | Eurostat EPEA / `ENV_AC_EPIAP1` | Environmental protection investment of corporations as ancillary producers | Monetary investment measure for ancillary producers. |

## DBRepo metadata update

The semantic mappings are implemented in `notebooks/dbrepo_upload.ipynb` in the section `T2.2 Semantic Mapping`.