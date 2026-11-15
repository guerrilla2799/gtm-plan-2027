#!/usr/bin/env python3
"""Build a driver-based 2027 GTM plan model in Excel.

Usage:
    python build_model.py inputs.json output.xlsx

Every output cell is a live formula that points back to the Inputs sheet,
so you can change an assumption in Excel and the whole plan updates.

Blue text = inputs you can change. Black = formulas. Green = links to another sheet.
Yellow fill = key assumptions to review.
"""
import json
import sys

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

FONT = "Arial"
BLUE = Font(name=FONT, color="0000FF")
BLACK = Font(name=FONT, color="000000")
GREEN = Font(name=FONT, color="008000")
BOLD = Font(name=FONT, bold=True)
TITLE = Font(name=FONT, bold=True, size=14)
HEAD = Font(name=FONT, bold=True, color="FFFFFF")
HEAD_FILL = PatternFill("solid", fgColor="1A1A1A")
ACCENT_FILL = PatternFill("solid", fgColor="E8500A")
YELLOW = PatternFill("solid", fgColor="FFFF00")
THIN = Border(bottom=Side(style="thin", color="999999"))

MONEY = '$#,##0;($#,##0);"-"'
NUM = '#,##0;(#,##0);"-"'
NUM1 = '#,##0.0;(#,##0.0);"-"'
PCT = '0.0%;(0.0%);"-"'
MULT = '0.0"x"'

Q = ["Q1", "Q2", "Q3", "Q4"]
QCOLS = ["B", "C", "D", "E"]  # quarter columns on every sheet
TOTAL_COL = "F"


def style(cell, font=BLACK, fmt=None, fill=None):
    cell.font = font
    if fmt:
        cell.number_format = fmt
    if fill:
        cell.fill = fill


def header_row(ws, row, labels, start_col=1):
    for i, label in enumerate(labels):
        c = ws.cell(row=row, column=start_col + i, value=label)
        c.font = HEAD
        c.fill = HEAD_FILL
        c.alignment = Alignment(horizontal="center")


def title(ws, text, sub):
    ws["A1"] = text
    ws["A1"].font = TITLE
    ws["A2"] = sub
    ws["A2"].font = Font(name=FONT, italic=True, color="666666")
    ws.column_dimensions["A"].width = 46
    for col in "BCDEFGHIJ":
        ws.column_dimensions[col].width = 16


class Inputs:
    """Writes the Inputs sheet and remembers where each input lives."""

    def __init__(self, ws):
        self.ws = ws
        self.row = 4
        self.ref = {}

    def section(self, name):
        self.row += 1
        c = self.ws.cell(row=self.row, column=1, value=name)
        c.font = Font(name=FONT, bold=True, color="FFFFFF")
        c.fill = ACCENT_FILL
        self.row += 1

    def scalar(self, key, label, value, fmt, note=None, key_assumption=False):
        ws = self.ws
        ws.cell(row=self.row, column=1, value=label).font = BLACK
        c = ws.cell(row=self.row, column=2, value=value)
        style(c, BLUE, fmt, YELLOW if key_assumption else None)
        if note:
            ws.cell(row=self.row, column=3, value=note).font = Font(name=FONT, italic=True, color="666666")
        self.ref[key] = f"Inputs!$B${self.row}"
        self.row += 1

    def quarterly(self, key, label, values, fmt, note=None):
        ws = self.ws
        ws.cell(row=self.row, column=1, value=label).font = BLACK
        cells = []
        for col, v in zip(QCOLS, values):
            c = ws[f"{col}{self.row}"]
            c.value = v
            style(c, BLUE, fmt)
            cells.append(f"Inputs!${col}${self.row}")
        t = ws[f"{TOTAL_COL}{self.row}"]
        t.value = f"=SUM(B{self.row}:E{self.row})"
        style(t, BOLD, fmt)
        if note:
            ws.cell(row=self.row, column=7, value=note).font = Font(name=FONT, italic=True, color="666666")
        self.ref[key] = cells
        self.ref[key + "_total"] = f"Inputs!${TOTAL_COL}${self.row}"
        self.row += 1

    def quarter_header(self):
        header_row(self.ws, self.row, ["", *Q, "Total"])
        self.row += 1


def build(inp, out_path):
    wb = Workbook()

    # ------------------------------------------------------------------ Inputs
    ws = wb.active
    ws.title = "Inputs"
    title(ws, f"{inp['company']}: {inp['plan_year']} GTM plan inputs",
          "Blue cells are inputs. Yellow cells are key assumptions to defend. Change them here and every other tab updates.")
    I = Inputs(ws)
    ws.cell(row=3, column=1, value="Legend: blue = input, black = formula, green = link from another tab, yellow = key assumption").font = Font(name=FONT, size=9, color="666666")

    I.section("ARR plan")
    I.scalar("start_arr", "Starting ARR (end of prior year)", inp["starting_arr"], MONEY)
    I.quarter_header()
    I.quarterly("new_logo", "New logo ARR target", inp["new_logo_arr_target"], MONEY)
    I.quarterly("expansion", "Expansion ARR", inp["expansion_arr"], MONEY)
    I.quarterly("churn", "Churn and downsell ARR", inp["churn_arr"], MONEY)
    I.scalar("gm", "Gross margin", inp["gross_margin"], PCT)
    I.scalar("other_opex", "R&D plus G&A as % of revenue", inp["other_opex_pct_of_revenue"], PCT,
             "Used only for a rough operating margin and Rule of 40")

    s = inp["sales"]
    I.section("Sales capacity")
    I.scalar("aes_start", "Ramped AEs at start of year", s["starting_ramped_aes"], NUM1)
    I.quarter_header()
    I.quarterly("hires", "AE hires (start of quarter)", s["hires"], NUM1)
    I.scalar("ramp", "Ramp time (quarters to full productivity)", s["ramp_quarters"], NUM1, key_assumption=True)
    I.scalar("prod", "Ramped productivity (new ARR per AE per quarter)", s["ramped_productivity_per_qtr"], MONEY, key_assumption=True)
    I.scalar("attr", "AE attrition (reps lost per quarter)", s["attrition_per_qtr"], NUM1)
    I.scalar("ae_cost", "Fully loaded cost per AE per year", s["fully_loaded_cost_per_ae_per_year"], MONEY)
    I.scalar("sales_other", "Other sales cost per year (SDRs, SEs, mgmt, tools)", s["other_sales_cost_per_year"], MONEY)

    f = inp["funnel"]
    rates = f["close_rates_by_lag"]
    I.section("Funnel (new logo)")
    I.scalar("asp", "Average new logo deal size (ARR)", f["asp"], MONEY, key_assumption=True)
    ws.cell(row=I.row, column=1, value="Time-based close rates: share of a quarter's oppties won").font = BLACK
    I.row += 1
    header_row(ws, I.row, ["Quarters after creation", "Same qtr", "1 later", "2 later", "3 later", "4 later", "5 later", "Eventual"])
    I.row += 1
    ws.cell(row=I.row, column=1, value="Close rate").font = BLACK
    rate_refs = []
    for i, r in enumerate(rates):
        c = ws.cell(row=I.row, column=2 + i, value=r)
        style(c, BLUE, PCT, YELLOW)
        rate_refs.append(f"Inputs!${get_column_letter(2 + i)}${I.row}")
    last = get_column_letter(1 + len(rates))
    ev = ws.cell(row=I.row, column=2 + len(rates), value=f"=SUM(B{I.row}:{last}{I.row})")
    style(ev, BOLD, PCT)
    ws.cell(row=I.row, column=1).comment = Comment(
        "Build these from a cohort analysis of your own oppties: for oppties created in a quarter, "
        "what share were won in the same quarter, one quarter later, and so on. Idea credit: Dave Kellogg, Kellblog.", "gtm-plan-2027")
    I.ref["rates"] = rate_refs
    I.ref["eventual"] = f"Inputs!${get_column_letter(2 + len(rates))}${I.row}"
    I.row += 1
    I.scalar("opp_growth", "Planned oppty growth per quarter", f["oppty_growth_per_qtr"], PCT)
    I.scalar("mtg_to_opp", "Meeting to oppty conversion", f["meeting_to_oppty"], PCT)
    I.quarter_header()
    I.quarterly("prior_opps", "Oppties created in prior year (by quarter)", f["oppties_created_prior_year"], NUM)

    p = inp["pipeline"]
    I.section("Pipeline")
    I.scalar("coverage", "Starting coverage target (x of quarter's new logo target)", p["starting_coverage_target"], MULT,
             "Set from your own history, not 1 / win rate", key_assumption=True)
    I.scalar("pipe_spend", "Pipe/spend ratio (pipeline $ per demand capture $)", p["pipe_to_spend"], MULT, key_assumption=True)
    src_refs = {}
    for name, share in p["source_mix"].items():
        I.scalar("src_" + name, f"Pipeline source mix: {name}", share, PCT)
        src_refs[name] = I.ref["src_" + name]

    m = inp["marketing_budget"]
    I.section("Marketing budget (annual)")
    budget_lines = [
        ("mb_people", "People (fully loaded)", m["people"]),
        ("mb_capture", "Programs: strategic, demand capture", m["programs_strategic_capture"]),
        ("mb_create", "Programs: strategic, demand creation", m["programs_strategic_create"]),
        ("mb_fixed", "Programs: fixed, non-strategic", m["programs_fixed"]),
        ("mb_exp", "Programs: experiments", m["programs_experiments"]),
        ("mb_infra", "Infrastructure: martech", m["infrastructure_tools"]),
        ("mb_ai", "Infrastructure: AI tools and usage", m["ai_tools_and_usage"]),
    ]
    for key, label, val in budget_lines:
        I.scalar(key, label, val, MONEY)

    I.section("Scenario levers")
    header_row(ws, I.row, ["Lever", *inp["scenarios"].keys()])
    I.row += 1
    scen_names = list(inp["scenarios"].keys())
    lever_labels = [("new_logo_mult", "New logo ARR multiplier", MULT),
                    ("spend_mult", "S&M spend multiplier", MULT),
                    ("out_year_new_logo_growth", "Out-year new logo growth", PCT)]
    scen_ref = {n: {} for n in scen_names}
    for key, label, fmt in lever_labels:
        ws.cell(row=I.row, column=1, value=label).font = BLACK
        for j, n in enumerate(scen_names):
            c = ws.cell(row=I.row, column=2 + j, value=inp["scenarios"][n][key])
            style(c, BLUE, '0.00"x"' if fmt == MULT else fmt)
            scen_ref[n][key] = f"Inputs!${get_column_letter(2 + j)}${I.row}"
        I.row += 1
    R = I.ref

    # ------------------------------------------------------------- ARR bridge
    ab = wb.create_sheet("ARR Bridge")
    title(ab, "ARR bridge (leaky bucket)", "Starting ARR + new logo + expansion - churn = ending ARR")
    header_row(ab, 4, ["", *Q, "Full year"])
    rows = ["Starting ARR", "New logo ARR", "Expansion ARR", "Churn and downsell", "Ending ARR", "Net new ARR", "Growth vs. start of year"]
    for i, label in enumerate(rows):
        ab.cell(row=5 + i, column=1, value=label).font = BOLD if label in ("Ending ARR",) else BLACK
    for qi, col in enumerate(QCOLS):
        start = f"={R['start_arr']}" if qi == 0 else f"={QCOLS[qi-1]}9"
        style(ab[f"{col}5"], GREEN if qi == 0 else BLACK, MONEY)
        ab[f"{col}5"] = start
        ab[f"{col}6"] = f"={R['new_logo'][qi]}"
        ab[f"{col}7"] = f"={R['expansion'][qi]}"
        ab[f"{col}8"] = f"=-{R['churn'][qi]}"
        ab[f"{col}9"] = f"=SUM({col}5:{col}8)"
        ab[f"{col}10"] = f"=SUM({col}6:{col}8)"
        ab[f"{col}11"] = f"=IFERROR({col}9/$B$5-1,0)"
        for r in (6, 7, 8):
            style(ab[f"{col}{r}"], GREEN, MONEY)
        style(ab[f"{col}9"], BOLD, MONEY)
        style(ab[f"{col}10"], BLACK, MONEY)
        style(ab[f"{col}11"], BLACK, PCT)
    ab["F5"] = "=B5"
    for r in (6, 7, 8, 10):
        ab[f"F{r}"] = f"=SUM(B{r}:E{r})"
    ab["F9"] = "=E9"
    ab["F11"] = "=E11"
    for r in range(5, 12):
        style(ab[f"F{r}"], BOLD, PCT if r == 11 else MONEY)

    # --------------------------------------------------------------- Capacity
    cp = wb.create_sheet("Capacity")
    title(cp, "Sales capacity", "Can the team we plan to have actually sell the number?")
    header_row(cp, 4, ["", *Q, "Full year"])
    labels = ["Hires this quarter", "Ending AE headcount", "Ramped rep equivalents", "Capacity (new logo ARR)",
              "New logo ARR target", "Capacity minus target", "Capacity coverage of target"]
    for i, label in enumerate(labels):
        cp.cell(row=5 + i, column=1, value=label).font = BLACK
    for qi, col in enumerate(QCOLS):
        cp[f"{col}5"] = f"={R['hires'][qi]}"
        style(cp[f"{col}5"], GREEN, NUM1)
        hires_sum = "+".join(R["hires"][: qi + 1])
        cp[f"{col}6"] = f"={R['aes_start']}+{hires_sum}-{R['attr']}*{qi + 1}"
        # ramp: a rep hired in quarter h contributes MIN(1,(q-h)/ramp) in quarter q (0 in the hire quarter)
        ramp_terms = [f"{R['hires'][h]}*MIN(1,{qi - h}/{R['ramp']})" for h in range(qi + 1)]
        cp[f"{col}7"] = f"=MAX(0,{R['aes_start']}-{R['attr']}*{qi + 1}+{'+'.join(ramp_terms)})"
        cp[f"{col}8"] = f"={col}7*{R['prod']}"
        cp[f"{col}9"] = f"={R['new_logo'][qi]}"
        cp[f"{col}10"] = f"={col}8-{col}9"
        cp[f"{col}11"] = f"=IFERROR({col}8/{col}9,0)"
        for r, fmt in ((6, NUM1), (7, NUM1), (8, MONEY), (9, MONEY), (10, MONEY), (11, MULT)):
            style(cp[f"{col}{r}"], GREEN if r == 9 else BLACK, fmt)
    cp["F5"] = "=SUM(B5:E5)"
    cp["F6"] = "=E6"
    cp["F7"] = "=AVERAGE(B7:E7)"
    for r in (8, 9, 10):
        cp[f"F{r}"] = f"=SUM(B{r}:E{r})"
    cp["F11"] = "=IFERROR(F8/F9,0)"
    for r, fmt in ((5, NUM1), (6, NUM1), (7, NUM1), (8, MONEY), (9, MONEY), (10, MONEY), (11, MULT)):
        style(cp[f"F{r}"], BOLD, fmt)
    cp["A13"] = "If capacity coverage is under 1.0x, the plan has a hole. Hire earlier, prove better productivity, or lower the target."
    cp["A13"].font = Font(name=FONT, italic=True, color="666666")

    # ----------------------------------------------------------------- Funnel
    fn = wb.create_sheet("Funnel")
    title(fn, "Inverted funnel with time-based close rates",
          "Bookings come from oppties created over many quarters. Idea credit: Dave Kellogg, Kellblog.")
    fn["A4"] = "Step 1. How many new logo deals do we need?"
    fn["A4"].font = BOLD
    header_row(fn, 5, ["", *Q, "Full year"])
    fn["A6"] = "New logo ARR target"
    fn["A7"] = "Deals needed (target / ASP)"
    for qi, col in enumerate(QCOLS):
        fn[f"{col}6"] = f"={R['new_logo'][qi]}"
        fn[f"{col}7"] = f"=IFERROR({col}6/{R['asp']},0)"
        style(fn[f"{col}6"], GREEN, MONEY)
        style(fn[f"{col}7"], BLACK, NUM1)
    fn["F6"] = "=SUM(B6:E6)"
    fn["F7"] = "=SUM(B7:E7)"
    style(fn["F6"], BOLD, MONEY)
    style(fn["F7"], BOLD, NUM1)

    fn["A9"] = "Step 2. Oppties to create this year"
    fn["A9"].font = BOLD
    header_row(fn, 10, ["", *Q, "Full year"])
    fn["A11"] = "Close rate reachable inside the plan year"
    fn["A12"] = "Growth weight"
    fn["A13"] = "Oppties to create"
    fn["A14"] = "Meetings needed"
    fn["A15"] = "New pipeline created ($)"
    nr = len(R["rates"])
    for qi, col in enumerate(QCOLS):
        reachable = min(nr, 4 - qi)  # lags 0..(3-qi) close inside the year
        fn[f"{col}11"] = "=" + "+".join(R["rates"][:reachable])
        fn[f"{col}12"] = f"=(1+{R['opp_growth']})^{qi}"
        fn[f"{col}13"] = f"=$B$27*{col}12"
        fn[f"{col}14"] = f"=IFERROR({col}13/{R['mtg_to_opp']},0)"
        fn[f"{col}15"] = f"={col}13*{R['asp']}"
        for r, fmt in ((11, PCT), (12, '0.000'), (13, NUM1), (14, NUM1), (15, MONEY)):
            style(fn[f"{col}{r}"], BLACK, fmt)
    for r, fmt in ((13, NUM1), (14, NUM1), (15, MONEY)):
        fn[f"F{r}"] = f"=SUM(B{r}:E{r})"
        style(fn[f"F{r}"], BOLD, fmt)

    # Waterfall grid: rows = creation cohorts (prior year Q1..Q4 + plan year Q1..Q4), cols = close quarter
    fn["A17"] = "Step 3. Waterfall: expected new logo deals by close quarter"
    fn["A17"].font = BOLD
    header_row(fn, 18, ["Cohort (quarter created)", *[f"Closes {q}" for q in Q], "In plan year", "Oppties"])
    py = inp["plan_year"]
    cohorts = [(f"{q} {py - 1}", -4 + i, R["prior_opps"][i], GREEN) for i, q in enumerate(Q)]
    cohorts += [(f"{q} {py}", i, f"{QCOLS[i]}13", BLACK) for i, q in enumerate(Q)]
    for k, (label, cq, opp_ref, fnt) in enumerate(cohorts):
        r = 19 + k
        fn.cell(row=r, column=1, value=label).font = BLACK
        fn[f"G{r}"] = f"={opp_ref}"
        style(fn[f"G{r}"], fnt, NUM1)
        for qi, col in enumerate(QCOLS):
            lag = qi - cq
            if 0 <= lag < nr:
                fn[f"{col}{r}"] = f"=$G{r}*{R['rates'][lag]}"
            else:
                fn[f"{col}{r}"] = 0
            style(fn[f"{col}{r}"], BLACK, NUM1)
        fn[f"F{r}"] = f"=SUM(B{r}:E{r})"
        style(fn[f"F{r}"], BOLD, NUM1)
    # rows 19..26 are cohorts
    fn["A27"] = "Base oppties per quarter (solved)"
    fn["A27"].font = BOLD
    fn["B27"] = "=IFERROR(MAX(0,(F7-SUM(F19:F22))/SUMPRODUCT(B11:E11,B12:E12)),0)"
    style(fn["B27"], BOLD, NUM1, YELLOW)
    fn["C27"] = "Q1 oppties needed so that prior-year pipeline plus this year's oppties hit the full-year deal target."
    fn["C27"].font = Font(name=FONT, italic=True, color="666666")

    fn["A29"] = "Expected deals (all cohorts)"
    fn["A30"] = "  from prior-year pipeline"
    fn["A31"] = "Expected new logo ARR"
    fn["A32"] = "Gap vs. target (positive = ahead)"
    fn["A33"] = "Prior-year oppty level vs. plan Q1 level"
    for col in QCOLS + ["F"]:
        fn[f"{col}29"] = f"=SUM({col}19:{col}26)"
        fn[f"{col}30"] = f"=SUM({col}19:{col}22)"
        fn[f"{col}31"] = f"={col}29*{R['asp']}"
        fn[f"{col}32"] = f"={col}31-{col}6"
        for r, fmt in ((29, NUM1), (30, NUM1), (31, MONEY), (32, MONEY)):
            style(fn[f"{col}{r}"], BOLD if col == "F" else BLACK, fmt)
    fn["B33"] = f"=IFERROR(B27/{R['prior_opps'][3]},0)"
    style(fn["B33"], BOLD, MULT)
    fn["C33"] = "Above about 1.3x means oppty creation must jump fast. Check spend, sources, and the target."
    fn["C33"].font = Font(name=FONT, italic=True, color="666666")
    fn["A34"] = "Oppties made this year still open at year end will close next year. That's the head start for the out-year."
    fn["A34"].font = Font(name=FONT, italic=True, color="666666")

    # ---------------------------------------------------------------- Pipeline
    pl = wb.create_sheet("Pipeline")
    title(pl, "Pipeline by source and starting coverage",
          "Plan pipeline across all four sources. Manage to starting coverage each quarter, not rolling four-quarter pipeline.")
    header_row(pl, 4, ["New pipeline by source ($)", *Q, "Full year", "Mix"])
    r = 5
    src_rows = {}
    for name, ref in src_refs.items():
        pl.cell(row=r, column=1, value=name).font = BLACK
        for qi, col in enumerate(QCOLS):
            pl[f"{col}{r}"] = f"=Funnel!{col}15*{ref}"
            style(pl[f"{col}{r}"], BLACK, MONEY)
        pl[f"F{r}"] = f"=SUM(B{r}:E{r})"
        style(pl[f"F{r}"], BOLD, MONEY)
        pl[f"G{r}"] = f"={ref}"
        style(pl[f"G{r}"], GREEN, PCT)
        src_rows[name] = r
        r += 1
    first, lastr = 5, r - 1
    pl.cell(row=r, column=1, value="Total new pipeline").font = BOLD
    for col in QCOLS + ["F", "G"]:
        pl[f"{col}{r}"] = f"=SUM({col}{first}:{col}{lastr})"
        style(pl[f"{col}{r}"], BOLD, PCT if col == "G" else MONEY)
    total_row = r
    pl[f"H{total_row}"] = '=IF(ABS(G{0}-1)>0.001,"Mix must sum to 100%","OK")'.format(total_row)
    pl[f"H{total_row}"].font = Font(name=FONT, bold=True, color="C00000")

    r += 2
    header_row(pl, r, ["Starting coverage", *Q, "", ""])
    r += 1
    pl.cell(row=r, column=1, value="New logo ARR target")
    pl.cell(row=r + 1, column=1, value="Required starting pipeline (day 1 of quarter)")
    pl.cell(row=r + 2, column=1, value="Coverage target")
    for qi, col in enumerate(QCOLS):
        pl[f"{col}{r}"] = f"={R['new_logo'][qi]}"
        pl[f"{col}{r + 1}"] = f"={col}{r}*{R['coverage']}"
        pl[f"{col}{r + 2}"] = f"={R['coverage']}"
        style(pl[f"{col}{r}"], GREEN, MONEY)
        style(pl[f"{col}{r + 1}"], BOLD, MONEY)
        style(pl[f"{col}{r + 2}"], GREEN, MULT)
    pl.cell(row=r + 4, column=1, value="Track next quarter's pipeline as it forms during this quarter. Look at this-quarter, next-quarter, and all-quarters pipeline together.").font = Font(name=FONT, italic=True, color="666666")
    mkt_row = src_rows.get("Marketing", first)

    # ------------------------------------------------------------------ Budget
    bd = wb.create_sheet("Budget")
    title(bd, "Marketing budget and GTM efficiency", "Three views of the same budget, plus the ratios the board will ask about.")
    header_row(bd, 4, ["Line", "Annual $", "% of marketing"])
    r = 5
    line_rows = {}
    for key, label, _ in budget_lines:
        bd.cell(row=r, column=1, value=label).font = BLACK
        bd[f"B{r}"] = f"={R[key]}"
        style(bd[f"B{r}"], GREEN, MONEY)
        line_rows[key] = r
        r += 1
    bd.cell(row=r, column=1, value="Total marketing").font = BOLD
    bd[f"B{r}"] = f"=SUM(B5:B{r - 1})"
    style(bd[f"B{r}"], BOLD, MONEY)
    tot = r
    for rr in range(5, r + 1):
        bd[f"C{rr}"] = f"=IFERROR(B{rr}/$B${tot},0)"
        style(bd[f"C{rr}"], BOLD if rr == tot else BLACK, PCT)

    def L(k):
        return f"B{line_rows[k]}"

    r = tot + 2
    header_row(bd, r, ["View 1. People, programs, infrastructure", "Annual $", "% of marketing"])
    views = [
        ("People", f"={L('mb_people')}"),
        ("Programs", f"={L('mb_capture')}+{L('mb_create')}+{L('mb_fixed')}+{L('mb_exp')}"),
        ("Infrastructure (incl. AI)", f"={L('mb_infra')}+{L('mb_ai')}"),
    ]
    r += 1
    for label, fml in views:
        bd.cell(row=r, column=1, value=label)
        bd[f"B{r}"] = fml
        bd[f"C{r}"] = f"=IFERROR(B{r}/$B${tot},0)"
        style(bd[f"B{r}"], BLACK, MONEY)
        style(bd[f"C{r}"], BLACK, PCT)
        r += 1

    r += 1
    header_row(bd, r, ["View 2. Three program buckets", "Annual $", "% of programs", "Guide"])
    r += 1
    prog_total = f"({L('mb_capture')}+{L('mb_create')}+{L('mb_fixed')}+{L('mb_exp')})"
    buckets = [
        ("Strategic (capture + create)", f"={L('mb_capture')}+{L('mb_create')}", "55% to 75%"),
        ("Fixed, non-strategic", f"={L('mb_fixed')}", "the rest"),
        ("Experiments", f"={L('mb_exp')}", "10% to 20%"),
    ]
    for label, fml, guide in buckets:
        bd.cell(row=r, column=1, value=label)
        bd[f"B{r}"] = fml
        bd[f"C{r}"] = f"=IFERROR(B{r}/{prog_total},0)"
        bd[f"D{r}"] = guide
        style(bd[f"B{r}"], BLACK, MONEY)
        style(bd[f"C{r}"], BLACK, PCT)
        r += 1
    bd.cell(row=r, column=1, value="Demand creation share of strategic").font = BLACK
    bd[f"C{r}"] = f"=IFERROR({L('mb_create')}/({L('mb_capture')}+{L('mb_create')}),0)"
    style(bd[f"C{r}"], BLACK, PCT)
    r += 2

    header_row(bd, r, ["View 3. Demand gen math", "Value", "", "Check"])
    r += 1
    demand_spend = f"({L('mb_capture')}+{L('mb_create')}+{L('mb_exp')})"
    dg = [
        ("Marketing-sourced pipeline needed", f"=Pipeline!F{mkt_row}", MONEY, None),
        ("Capture spend needed (pipeline / pipe-spend)", f"=IFERROR(B{r}/{R['pipe_spend']},0)", MONEY, None),
        ("Capture spend planned", f"={L('mb_capture')}", MONEY, None),
        ("Planned minus needed", f"=B{r + 2}-B{r + 1}", MONEY,
         f'=IF(B{r + 3}<0,"Underfunded for the pipeline target",IF(B{r + 2}>1.5*B{r + 1},"Spend is well above need. Check the pipe/spend ratio.","OK"))'),
        ("Marketing-sourced oppties", f"=Funnel!F13*{src_refs.get('Marketing', '0')}", NUM1, None),
        ("Cost per marketing oppty (capture + create + experiments)", f"=IFERROR({demand_spend}/B{r + 4},0)", MONEY, None),
        ("Implied pipe/spend at planned capture spend", f"=IFERROR(B{r}/B{r + 2},0)", MULT, None),
    ]
    for label, fml, fmt, check in dg:
        bd.cell(row=r, column=1, value=label)
        bd[f"B{r}"] = fml
        style(bd[f"B{r}"], BLACK, fmt)
        if check:
            bd[f"D{r}"] = check
            bd[f"D{r}"].font = Font(name=FONT, bold=True, color="C00000")
        r += 1
    bd.cell(row=r, column=1, value="Demand creation and experiments aren't in the pipe/spend check. They build next year's pipeline and get their own leading indicators.").font = Font(name=FONT, italic=True, color="666666")
    r += 2

    header_row(bd, r, ["GTM efficiency (plan year)", "Value"])
    r += 1
    eff_start = r
    eff = [
        ("Average AE headcount", "=AVERAGE(Capacity!B6:E6)", NUM1),
        ("Sales cost (AEs + other)", f"=B{r}*{R['ae_cost']}+{R['sales_other']}", MONEY),
        ("Marketing cost", f"=B{tot}", MONEY),
        ("Total S&M", f"=B{r + 1}+B{r + 2}", MONEY),
        ("Marketing share of S&M", f"=IFERROR(B{r + 2}/B{r + 3},0)", PCT),
        ("New logo + expansion ARR", "='ARR Bridge'!F6+'ARR Bridge'!F7", MONEY),
        ("CAC ratio (S&M / new + expansion ARR)", f"=IFERROR(B{r + 3}/B{r + 5},0)", '0.00"x"'),
        ("Average ARR (revenue proxy)", "=('ARR Bridge'!B5+'ARR Bridge'!F9)/2", MONEY),
        ("Rough operating margin", f"=IFERROR({R['gm']}-B{r + 3}/B{r + 7}-{R['other_opex']},0)", PCT),
        ("ARR growth", "='ARR Bridge'!F11", PCT),
        ("Rule of 40 (growth + operating margin)", f"=B{r + 9}+B{r + 8}", PCT),
        ("Burn ratio (operating loss / net new ARR)", f"=IFERROR(MAX(0,-B{r + 8}*B{r + 7})/'ARR Bridge'!F10,0)", '0.00"x"'),
    ]
    for label, fml, fmt in eff:
        bd.cell(row=r, column=1, value=label)
        bd[f"B{r}"] = fml
        style(bd[f"B{r}"], BLACK, fmt)
        r += 1
    bd.cell(row=r, column=1, value="Operating margin and burn are rough. They use average ARR as revenue and skip timing and non-cash items. Use finance's P&L for the board.").font = Font(name=FONT, italic=True, color="666666")
    cac_cell = f"Budget!$B${eff_start + 6}"
    sm_cell = f"Budget!$B${eff_start + 3}"

    # --------------------------------------------------------------- Scenarios
    sc = wb.create_sheet("Scenarios")
    title(sc, "Scenarios with out-year", "Baseline is the plan you can beat. Growth and Profit show the tradeoff. Out-year holds the CAC ratio flat.")
    cols = []
    head = ["Metric"]
    for n in scen_names:
        head += [f"{n} {py}", f"{n} {py + 1}"]
    header_row(sc, 4, head)
    metrics = ["Starting ARR", "New logo ARR", "Expansion ARR", "Churn and downsell", "Ending ARR", "ARR growth",
               "S&M spend", "CAC ratio", "Revenue (avg ARR)", "Rough operating margin", "Rule of 40", "Burn ratio"]
    for i, mtr in enumerate(metrics):
        sc.cell(row=5 + i, column=1, value=mtr).font = BOLD if mtr in ("Ending ARR", "Rule of 40") else BLACK
    for j, n in enumerate(scen_names):
        a = get_column_letter(2 + 2 * j)       # plan year
        b = get_column_letter(3 + 2 * j)       # out-year
        lv = scen_ref[n]
        # plan year
        sc[f"{a}5"] = f"={R['start_arr']}"
        sc[f"{a}6"] = f"={R['new_logo_total']}*{lv['new_logo_mult']}"
        sc[f"{a}7"] = f"={R['expansion_total']}"
        sc[f"{a}8"] = f"=-{R['churn_total']}"
        sc[f"{a}11"] = f"={sm_cell}*{lv['spend_mult']}"
        # out-year
        sc[f"{b}5"] = f"={a}9"
        sc[f"{b}6"] = f"={a}6*(1+{lv['out_year_new_logo_growth']})"
        sc[f"{b}7"] = f"=IFERROR({b}5*{a}7/{a}5,0)"
        sc[f"{b}8"] = f"=IFERROR({b}5*{a}8/{a}5,0)"
        sc[f"{b}11"] = f"={b}12*({b}6+{b}7)"
        for c in (a, b):
            sc[f"{c}9"] = f"=SUM({c}5:{c}8)"
            sc[f"{c}10"] = f"=IFERROR({c}9/{c}5-1,0)"
            sc[f"{c}13"] = f"=({c}5+{c}9)/2"
            sc[f"{c}14"] = f"=IFERROR({R['gm']}-{c}11/{c}13-{R['other_opex']},0)"
            sc[f"{c}15"] = f"={c}10+{c}14"
            sc[f"{c}16"] = f"=IFERROR(MAX(0,-{c}14*{c}13)/({c}9-{c}5),0)"
        sc[f"{a}12"] = f"=IFERROR({a}11/({a}6+{a}7),0)"
        sc[f"{b}12"] = f"={a}12"
        for c in (a, b):
            for rr, fmt in ((5, MONEY), (6, MONEY), (7, MONEY), (8, MONEY), (9, MONEY), (10, PCT), (11, MONEY),
                            (12, '0.00"x"'), (13, MONEY), (14, PCT), (15, PCT), (16, '0.00"x"')):
                style(sc[f"{c}{rr}"], BOLD if rr in (9, 15) else BLACK, fmt)
    sc.cell(row=18, column=1, value="Spend multipliers scale total S&M. Pipeline and capacity tabs show Baseline only. Rebuild with new inputs to see a scenario in full detail.").font = Font(name=FONT, italic=True, color="666666")

    # ------------------------------------------------------------ Assumptions
    al = wb.create_sheet("Assumptions Log")
    title(al, "Assumptions log", "Every number you can't back with history goes here, with an owner and a date to check it.")
    header_row(al, 4, ["Assumption", "Value", "Why we believe it", "Owner", "Check by", "Status"])
    examples = [
        ("Ramped AE productivity", "See Inputs", "2026 H2 average for reps past ramp", "CRO", "End of Q1", "Open"),
        ("Pipe/spend ratio", "See Inputs", "2026 trailing four quarters", "CMO", "End of Q1", "Open"),
        ("AI agent handles first-touch inbound", "Fewer SDR hires", "Q4 2026 pilot results. Prove by Q2 or move to upside.", "CMO", "End of Q2", "Open"),
    ]
    for i, row in enumerate(examples):
        for k, v in enumerate(row):
            c = al.cell(row=5 + i, column=1 + k, value=v)
            c.font = BLUE
    al.column_dimensions["C"].width = 50
    al.cell(row=9, column=1, value="Example rows. Replace them with your own.").font = Font(name=FONT, italic=True, color="666666")

    for sheet in wb.worksheets:
        sheet.freeze_panes = "B5" if sheet.title != "Inputs" else None
        sheet.sheet_view.showGridLines = False
    wb.save(out_path)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1]) as fh:
        inp = json.load(fh)
    build(inp, sys.argv[2])
    print(f"Wrote {sys.argv[2]}")


if __name__ == "__main__":
    main()
