---
name: pipeline-model
description: Build or check a B2B SaaS pipeline model. Use when someone asks how much pipeline or how many opportunities they need, wants an inverted funnel, time-based close rates, pipeline coverage targets by quarter, pipeline targets by source, a sales capacity check, or a mid-year pipeline reforecast. Produces a live Excel model and a one-page pipeline brief.
---

# Pipeline model

Part of the 2027 Marketing Planning Skill Pack. For a full annual plan, use the `gtm-plan-2027` skill. Use this one when the person only needs the pipeline math, or needs to redo it mid-year.

The method is built on Dave Kellogg's Kellblog writing on inverted funnels, time-based close rates, and pipeline coverage. See `references/sources.md`. He isn't affiliated with this skill.

## Ground rules

1. Plan on opportunities and pipeline dollars, not leads.
2. Use time-based close rates, not one blended rate. Most deals close in later quarters than the oppty was created.
3. Set coverage from history, not 1 / win rate. Read `references/capacity-and-pipeline.md` before you set a coverage target.
4. Manage to starting coverage for each quarter. Don't use rolling four-quarter pipeline.
5. Never invent numbers. If the person lacks one, use a labeled benchmark from `references/benchmarks.md` and list it as an assumption.
6. Ask for one block of inputs at a time. Offer defaults.

## Workflow

### 1. Inputs
Ask for:
- New logo ARR target by quarter, and average deal size (by segment if they sell to more than one)
- Oppties created per quarter for the last 4 to 8 quarters
- When those oppties closed (to build close rates by quarter after creation). If they don't have this, help them pull it: for each creation quarter, count wins in the same quarter, one later, two later, and so on.
- Pipeline mix by source: marketing, SDR or outbound, sales self-sourced, partners
- AE headcount, hires by quarter, ramp time, ramped productivity, attrition
- Historical conversion of starting pipeline (for the coverage target)
- Meeting to oppty conversion (or whatever earlier stage they track)

Use `templates/inputs.md` as the checklist. If they're mid-year, use actuals for past quarters and plan for the rest.

### 2. Build the model
Copy `templates/inputs.json`, fill it in, and run:

```
python scripts/build_model.py my_inputs.json pipeline_model.xlsx
```

Needs `openpyxl`. The workbook has live formulas. For this skill, focus on the Capacity, Funnel, and Pipeline tabs. The other tabs are there if they want them.

### 3. Read the results
Pull out:
- Deals needed and oppties to create by quarter
- Share of this year's deals that come from pipeline that already exists
- The quarter-by-quarter gap between expected deals and target (H2 gaps are common)
- Ratio of planned oppty creation to last year's run rate. Above about 1.3x is a warning.
- Required starting pipeline for each quarter
- Pipeline target by source
- Sales capacity vs. target

### 4. Pressure-test
Ask:
- Is the jump in oppty creation realistic given spend and headcount?
- Which quarter is most at risk, and what's the early warning?
- Which source is most likely to miss, and who owns it?
- If capacity is short, is the fix hiring earlier, better productivity (with a reason), or a lower target?

### 5. Deliver
Write a one-page pipeline brief:
1. The number: deals, oppties, and pipeline dollars needed
2. How much is already in hand from existing pipeline
3. Coverage targets by quarter
4. Targets by source with owners
5. The riskiest quarter and its early warning
6. Assumptions log

Then hand over the Excel file.

## Style
Plain words. Short sentences. Lead with the number, then the reason. Translate into money for exec audiences.
