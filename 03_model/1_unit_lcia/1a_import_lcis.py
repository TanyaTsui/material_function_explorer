"""
Step 1a: import the LCI sheets into one table.

Reads every Excel file in 01_data/01_raw/LCIs/ (one file per case: 27 baselines and 8 RAW cases) and writes all their
exchanges to one table, one row per exchange. Nothing is calculated here.

Input:  01_data/01_raw/LCIs/*.xlsx (Brightway Excel format, one block per activity)
Output: 01_data/02_processed/unit_lcia_steps/1a_lci_exchanges.csv

How an LCI sheet is read: a row starting with 'Activity' opens a new activity; the rows under it give its reference
product, unit, location and module; the row after 'Exchanges' holds the column names of the exchange rows that follow.
Only the 'amount' column is used (the value at the typical parameter values); formulas and ranges are ignored, because
the model is deterministic.
"""
# %% Setup
import sys
from pathlib import Path

import openpyxl
import pandas as pd

try:
    HERE = Path(__file__).resolve().parent      # run as a script
except NameError:
    HERE = Path.cwd()                           # run cell by cell in VS Code (the working folder is this file's folder)
sys.path.append(str(HERE.parent))
import settings as s

s.STEPS_FOLDER.mkdir(parents=True, exist_ok=True)


# %% Function: read one LCI file
def read_lci_file(path):
    """Return a list of exchanges (one dict per exchange) of every activity in the file."""
    case_id = path.stem                          # e.g. baseline_cork, raw_timber_scaled_up
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    exchanges = []

    for sheet in workbook.worksheets:
        if sheet.title == "README":
            continue
        activity = {}                            # the activity being read
        columns = None                           # column names of the exchange rows, once we are in an 'Exchanges' part

        for row in sheet.iter_rows(values_only=True):
            row = list(row)
            first = row[0] if row else None
            if first is None:                    # an empty row ends an exchange table
                columns = None
                continue
            if first == "Activity":
                activity = {"activity": row[1]}
                columns = None
            elif first in ("reference product", "unit", "location", "module") and columns is None:
                activity[first] = row[1]
            elif first == "Exchanges":
                columns = "next row"             # the next row holds the column names
            elif columns == "next row":
                columns = [c for c in row if c is not None]
            elif isinstance(columns, list):      # an exchange row
                values = dict(zip(columns, row))
                if values.get("type") == "note":     # a row kept only as a remark (e.g. "(no row) ... × reuse")
                    continue
                exchanges.append({
                    "case_id": case_id,
                    "activity": activity["activity"],
                    "activity_reference_product": activity.get("reference product"),
                    "activity_module": activity.get("module"),
                    "exchange_type": values.get("type"),
                    "input_name": values.get("name"),
                    "input_reference_product": values.get("reference product"),
                    "input_location": values.get("location"),
                    "input_unit": values.get("unit"),
                    "input_database": values.get("database"),
                    "amount": float(values.get("amount")),
                })
    return exchanges


# %% Read all LCI files
lci_files = sorted(s.LCI_FOLDER.glob("*.xlsx"))      # the archive/ subfolder is not included
all_exchanges = []
for path in lci_files:
    all_exchanges += read_lci_file(path)
exchanges = pd.DataFrame(all_exchanges)

print(f"{len(lci_files)} LCI files, {len(exchanges)} exchanges")
exchanges.groupby("case_id").size()


# %% Label each input as foreground (an activity of the same LCI file) or background (an ecoinvent dataset)
exchanges["input_is"] = "background"
exchanges.loc[exchanges.exchange_type == "production", "input_is"] = "production"
foreground_activities = set(zip(exchanges.case_id, exchanges.activity, exchanges.activity_reference_product))
is_foreground = pd.Series([(c, n, r) in foreground_activities for c, n, r in
                           zip(exchanges.case_id, exchanges.input_name, exchanges.input_reference_product)],
                          index=exchanges.index)
exchanges.loc[is_foreground & (exchanges.exchange_type == "technosphere"), "input_is"] = "foreground"
exchanges.input_is.value_counts()


# %% Checks: stop here if an LCI file does not have the expected shape
problems = []

# every case has the six modules A1–A3 ... C3–C4, and nothing else (module B is added in component 2)
for case_id, group in exchanges.groupby("case_id"):
    modules = set(group.activity_module)
    if modules != set(s.MODULES):
        problems.append(f"{case_id}: modules are {sorted(modules)}, expected {s.MODULES}")

# only production and technosphere exchanges (the LCIs have no direct emissions; the model would ignore them)
for exchange_type in set(exchanges.exchange_type) - {"production", "technosphere"}:
    problems.append(f"exchanges of type '{exchange_type}' are not handled by the model")

# every background input points to the ecoinvent database named in settings
background = exchanges[exchanges.input_is == "background"]
wrong_database = background[background.input_database != s.LCI_BACKGROUND_DATABASE]
for _, row in wrong_database.iterrows():
    problems.append(f"{row.case_id}: '{row.input_name}' is not found in the file and is not from "
                    f"{s.LCI_BACKGROUND_DATABASE} (database '{row.input_database}')")

# every activity has exactly one production exchange
production = exchanges[exchanges.exchange_type == "production"].groupby(["case_id", "activity"]).size()
for (case_id, activity), n in production[production != 1].items():
    problems.append(f"{case_id}: activity '{activity}' has {n} production exchanges")

# activity names are unique within a case (step 1c finds an input by its name)
names = exchanges[exchanges.exchange_type == "production"][["case_id", "activity", "activity_reference_product"]]
for (case_id, activity), n in names.drop_duplicates().groupby(["case_id", "activity"]).size().items():
    if n > 1:
        problems.append(f"{case_id}: two activities are called '{activity}'")

if problems:
    raise ValueError("Problems in the LCI files:\n  " + "\n  ".join(problems))
print("Checks passed: every case has the six modules, every background input is an ecoinvent dataset.")


# %% Save
exchanges.to_csv(s.STEPS_FOLDER / "1a_lci_exchanges.csv", index=False)
print("Saved", s.STEPS_FOLDER / "1a_lci_exchanges.csv")
