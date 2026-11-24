"""Helpers for batch_7: row specs, CSV writers, LCI sheet writer (read-only use of Brightway)."""
import csv, os, datetime
import bwx
from openpyxl import Workbook
from openpyxl.styles import Font

RUN = "batch_7"
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATE = "2026-11-19"
DB = bwx.DB
CH = "raw_baselines"

# fixed datasets (workbook sheet fixed_settings) -> ecoinvent codes found with search_ecoinvent.py
LORRY = "dd736ab7d965646d04b091ae5fa68d97"
SEA = "1d2cb4018daf428aebf419380c6a2975"
DIESEL = "d8636b2f3daa827949cbe33db9f47ffe"
ELEC = "42ec2f4634364ee86921b4c6dfe2de31"
HEAT = "eda02fda34ab477c467e7913b32b7649"
MACH = "5a0b37c3a698f020385f42dbdfbf1b1f"


def ger(loc):
    if loc in ("RER", "Europe without Switzerland"): return 1
    if loc in ("DE", "FR", "IT", "ES", "NL", "AT", "SE", "FI", "PL", "CH", "GB"): return 2
    if loc == "GLO": return 3
    if loc == "RoW": return 4
    return 5


def act(code):
    a = bwx.get(code)
    return dict(name=a["name"], product=a["reference product"], location=a["location"], unit=a["unit"], code=code)


class Rows:
    """Collects csv rows."""
    HEAD = {
        "decisions.csv": "run_id,material_id,question_id,answer,value,unit,evidence,source_link,search_step,date".split(","),
        "dataset_choices.csv": "run_id,material_id,module,row_purpose,search_terms,candidates_considered,chosen_activity,reference_product,location,unit,amount,database,rule_applied,proxy,TeR,GeR,TiR,machine_type,machine_candidates,machine_used,power_kW,throughput_kg_per_h,machine_mass_kg,machine_life_h,values_as_found,value_source,value_link,conversions,per_kg_processed,ecoinvent_version,search_date".split(","),
        "epd_check.csv": "run_id,material_id,check_id,okobaudat_release,category,epd_ids,n_epds,epd_median,our_gwp_fossil_a1a3,ratio_to_median,result,flag_units_mass,flag_dataset_state,flag_indicator,flag_machine_rows,likely_reason,wear_share_of_gwp_fossil_a1a3,route,distance_to_median,lci_kept".split(","),
        "cff_inputs.csv": "run_id,material_id,cff_archetype,recycling_share,reuse_share,incineration_share,landfill_share,flag,note".split(","),
        "bioc_inputs.csv": "run_id,material_id,constituent,kg_per_kg_product,carbon_archetype,moisture_content,flag,note".split(","),
    }

    def __init__(self):
        self.d = {k: [] for k in self.HEAD}

    def add(self, f, **kw):
        row = {h: "" for h in self.HEAD[f]}
        row["run_id"] = RUN
        for k, v in kw.items():
            assert k in row, (f, k)
            row[k] = v
        self.d[f].append(row)

    def dec(self, mat, qid, answer, value="", unit="", evidence="", link="", step=""):
        self.add("decisions.csv", material_id=mat, question_id=qid, answer=answer, value=value, unit=unit,
                 evidence=evidence, source_link=link, search_step=step, date=DATE)

    def ds(self, mat, module, purpose, code=None, amount="", rule="", proxy="", TeR="", GeR=None, TiR=1, search_terms="",
           candidates="", name=None, product=None, location=None, unit=None, **kw):
        if code:
            a = act(code)
            name, product, location, unit = a["name"], a["product"], a["location"], a["unit"]
        if GeR is None and location: GeR = ger(location)
        self.add("dataset_choices.csv", material_id=mat, module=module, row_purpose=purpose, search_terms=search_terms,
                 candidates_considered=candidates, chosen_activity=name or "", reference_product=product or "",
                 location=location or "", unit=unit or "", amount=amount, database=DB if code else "",
                 rule_applied=rule, proxy=proxy, TeR=TeR, GeR=GeR if GeR is not None else "", TiR=TiR,
                 ecoinvent_version="3.12 cut-off", search_date=DATE, **kw)

    def write(self):
        for f, rows in self.d.items():
            with open(os.path.join(OUT, f), "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=self.HEAD[f])
                w.writeheader()
                for r in rows: w.writerow(r)


def fmt(x, n=6):
    return float(f"{x:.{n}g}")


class Block:
    def __init__(self, module, mat, prev_product=None, prev_name=None, out_name=None, out_prod=None, prev_amount=1):
        self.module = module
        self.mat = mat
        self.rows = []
        self.prev = (prev_name, prev_product, prev_amount)
        self.out_name = out_name
        self.out_prod = out_prod
        self.comment = ""

    def add(self, code=None, amount=0, rule="", TeR="", GeR=None, TiR=1, comment="", name=None, product=None,
            location=None, unit=None):
        if code:
            a = act(code)
            name, product, location, unit = a["name"], a["product"], a["location"], a["unit"]
        if GeR is None: GeR = ger(location)
        d = (TeR + GeR + TiR) / 3 if isinstance(TeR, (int, float)) else ""
        self.rows.append(dict(name=name, amount=fmt(amount), unit=unit, location=location, product=product,
                              database=DB, type="technosphere", module=self.module, rule=rule, TeR=TeR, GeR=GeR,
                              TiR=TiR, DQR=round(d, 2) if d != "" else "", comment=comment))


HDR = ["name", "amount", "unit", "location", "reference product", "database", "type", "module", "rule", "TeR", "GeR",
       "TiR", "DQR", "comment"]


def write_sheet(mat, blocks, path):
    wb = Workbook()
    ws = wb.active
    ws.title = "LCI"
    bold = Font(bold=True)
    ws["A1"], ws["B1"] = "Database", CH
    r = 3
    for b in blocks:
        for k, v in [("Activity", b.out_name), ("reference product", b.out_prod), ("unit", "kilogram"),
                     ("location", "RER"), ("module", b.module), ("comment", b.comment)]:
            ws.cell(r, 1, k).font = bold
            ws.cell(r, 2, v)
            r += 1
        ws.cell(r, 1, "Exchanges").font = bold
        r += 1
        for i, h in enumerate(HDR, 1):
            ws.cell(r, i, h).font = bold
        r += 1
        # production row
        prod = [b.out_name, 1, "kilogram", "RER", b.out_prod, CH, "production", b.module, "–"]
        for i, v in enumerate(prod, 1): ws.cell(r, i, v)
        r += 1
        if b.prev[0]:
            prev = [b.prev[0], b.prev[2], "kilogram", "RER", b.prev[1], CH, "technosphere", b.module, "–", "", "", "", "",
                    "previous block" + (" (A5 takes 1 + loss)" if b.module == "A5" else "")]
            for i, v in enumerate(prev, 1): ws.cell(r, i, v)
            r += 1
        for x in b.rows:
            vals = [x["name"], x["amount"], x["unit"], x["location"], x["product"], x["database"], x["type"],
                    x["module"], x["rule"], x["TeR"], x["GeR"], x["TiR"], x["DQR"], x["comment"]]
            for i, v in enumerate(vals, 1): ws.cell(r, i, v)
            r += 1
        r += 1
    for col, w in zip("ABCDEFGHIJKLMN", [58, 12, 12, 26, 44, 22, 14, 8, 8, 5, 5, 5, 6, 80]):
        ws.column_dimensions[col].width = w
    wb.save(path)
