# maDMP finalization notes

This document records the finalization steps performed for **T4.3 Export and finalize maDMP**.

The machine actionable DMP JSON was exported from the TU Wien Research Data Repository and reviewed against the final human readable DMP.

The exported JSON was updated to reflect the final project state. The updates included:

- adding final DMP level metadata, including title, language, DMP identifier and modification date
- checking the contact person and contributors including ORCID identifiers
- adding dataset identifiers for the produced and reused datasets
- adding related identifiers for the GitHub repository, Zenodo software release, DBRepo database, model deposit, generated data deposit, final DMP deposit and initial DMP. They were written in the human readable DMP but missing from the machine actionable.
- correcting reused Eurostat input data rights information to refer to the Eurostat copyright notice and free reuse policy
- checking that output data and model artefacts use CC BY 4.0 and project code uses MIT
- validating that the edited file remains syntactically valid JSON

The finalized maDMP JSON was validated with:

```bash
python -m json.tool docs/dmp/maDMP-FINAL_Do_Rich_Countries_Invest_More_in_Saving_the_Planet__Analysis_of_Europe_s_Green_Investment_Landscape_20260530.json