---
name: gtm-plan-2027
description: Build a board-ready 2027 go-to-market plan for a venture-backed B2B SaaS company. Use when a CMO, CRO, or CEO asks for an annual plan, operating plan, marketing plan, pipeline model, inverted funnel, GTM budget, sales capacity model, planning OKRs, or a board planning deck. Interviews the user, models bookings, capacity, pipeline, and budget, stress-tests the plan with board questions, and produces a one-page plan, full plan doc, Excel model, OKRs, and a board deck outline.
---

# 2027 GTM Plan

You're helping an AI-native CMO at a venture-backed, mid-market B2B SaaS company (roughly $10M to $150M ARR) build their 2027 go-to-market plan. The plan covers the full GTM system: new logo, expansion, churn, sales capacity, pipeline, marketing budget, and the board story.

The method is built mainly on Dave Kellogg's planning work (Kellblog). It adds a playbook for getting the plan approved and a modern demand system. Other voices fill gaps. See `references/sources.md` for credits and links. Nobody named here is affiliated with or endorses this skill.

## Ground rules

1. The math comes first. Every target traces back to a driver the user can defend with history. If a ratio improves vs. 2026, the plan must say why. If it can't, flag it as "spreadsheet magic" and ask the user to either explain it or drop it. (Kellogg)
2. Strategy before spreadsheet. Agree on 3 to 5 strategic objectives before building the model. A plan is a set of choices. A budget is just the cost of those choices. (Kellogg)
3. When ideas conflict, Kellogg's math wins. Read `references/tensions.md` and name the tension out loud in the plan instead of hiding it.
4. Build a plan the team can beat. Targets should be hard but likely. Put upside in a separate scenario, not in the base plan.
5. Never invent the user's numbers. If they don't have a number, use a labeled benchmark from `references/benchmarks.md`, mark it as an assumption, and list it in the assumptions log.
6. Keep the user moving. Ask one phase at a time. Offer defaults. Don't dump all questions at once.

## Workflow

Work through these 12 phases in order. Each phase lists what to ask, what to build, and which reference to read. Track every assumption in an assumptions log as you go.

### Phase 1. Intake
Ask for: company name, ARR today, 2026 expected ending ARR, stage and last round, motions (sales-led, PLG, hybrid), segments (SMB, mid-market, enterprise), ACV by segment, sales cycle length, and the 2027 target the CEO or board has floated. Ask if they can upload 2026 actuals (CRM export or a summary sheet). Offer the template in `templates/inputs.md`.
Read: `references/benchmarks.md` if they lack data.

### Phase 2. Look back at 2026
Build the ARR leaky bucket for 2026: starting ARR, plus new logo ARR, plus expansion, minus churn and downsell, equals ending ARR. Show the 2026 forecast vs. the 2026 plan. Pull 2026 efficiency: CAC ratio, magic number, pipe/spend, cost per oppty, win rate, sales cycle. Note what went right and wrong in plain words.
Read: `references/kellogg-planning.md` (look back section).

### Phase 3. Strategy before spreadsheet
Help the user pick 3 to 5 strategic objectives for 2027 (for example: win the mid-market, launch the AI product line, fix net retention). For each, write one sentence on why and one on what it costs. Run the plan vs. budget test: if the CFO cuts 15%, which objective goes? If the answer is "cut everything 15%," the user has a budget, not a plan.
Read: `references/kellogg-planning.md` (plan vs. budget), `references/plan-approval.md` (themes).

### Phase 4. Bookings and the ARR bridge
Turn the ARR target into a bookings plan. Ending ARR equals starting ARR plus new logo plus expansion minus churn. Split by segment and by quarter. Check the growth rate and burn against the Rule of 40 and the board's expectations.
Read: `references/kellogg-planning.md` (ARR bridge).

### Phase 5. Sales capacity
Build the capacity model: starting reps, hires by quarter, ramp time, ramped productivity, attrition. Compare capacity to the new logo plus expansion bookings target. If capacity is short, the plan is wrong, not the reps. Remember that every new rep needs demand spend behind them, not just a salary.
Read: `references/capacity-and-pipeline.md` (capacity section).

### Phase 6. Pipeline model
Build the inverted funnel by segment. Work back from bookings to won deals, to opportunities, to the earlier stage the company actually tracks. Use time-based close rates (what share of a quarter's oppties close in-quarter, next quarter, and later) instead of one blended rate. Split the pipeline target across the four sources: marketing, SDR or outbound, sales self-sourced, and partners. Set a starting-coverage target for each quarter. Don't set coverage by flipping the win rate.
Read: `references/capacity-and-pipeline.md` (all of it).

### Phase 7. The demand system
Map where pipeline gets captured today (3 to 6 sources) and what each yields, using win rate to compare quality. Split the demand budget into capture (in-market buyers) and create (future buyers). Run a waste audit on low-intent leads that burn SDR and AE time. Add self-reported attribution ("How did you hear about us?") as a second lens next to pipe/spend.
Read: `references/demand-system.md`, then `references/tensions.md`.

### Phase 8. Budget
Build the marketing budget three ways. First, people vs. programs vs. infrastructure (tools and AI). Second, the three buckets: strategic programs (about 55 to 75%), fixed costs, and experiments (about 10 to 20%). Third, demand gen spend by channel with pipe/spend and cost per oppty for each. Ask if any marketing money lives outside marketing (a CEO's pet project, a user conference in another budget). Tie total spend to CAC ratio and payback.
Read: `references/plan-approval.md` (budget buckets), `references/kellogg-planning.md` (board questions).

### Phase 9. AI-era assumptions
This is its own phase on purpose. Walk through: AI leverage on headcount (which roles get fewer hires and why), AI agents in SDR and inbound work, answer engines and AEO in the channel mix, AI tool spend as a real line item, and data quality needed to make any of it work. Every AI efficiency gain must show its mechanism and a test to prove it by mid-year. Gains without a mechanism go into the upside scenario only.
Read: `references/ai-era-assumptions.md`.

### Phase 10. Scenarios
Build three cases: Baseline (the plan you can beat), Growth (more spend, faster hiring), and Profit (less burn). For each, show 2027 and a simple 2028 out-year. Recommend one and say why.
Run `scripts/build_model.py` to generate the Excel model (see the Model section below).

### Phase 11. Board red-team
Run every question in `references/board-questions.md` against the plan. Score each one as Strong, Weak, or Missing. Fix the weak ones or list them as open risks. This step is what makes the plan board-ready.

### Phase 12. Outputs and operating cadence
Produce the deliverables below. Then set the cadence: monthly pipeline review, quarterly reforecast, the leading indicators to watch (next-quarter pipeline coverage forming, pipe/spend, rep ramp), and the trigger points for moving money between scenarios.

## Deliverables

Produce these in order. Use the templates in `templates/`.

1. One-page plan (`templates/one-page-plan.md`). The whole plan on a single page.
2. Full plan doc (`templates/plan-doc.md`). Strategy, model summary, budget, risks, assumptions log, and appendix.
3. The Excel model, from `scripts/build_model.py`.
4. Quarterly OKRs (`templates/okrs.md`). 3 to 5 objectives, each with 2 to 4 measurable key results.
5. Board deck (`templates/board-deck.md`). A slide-by-slide outline with titles, the message of each slide, and the chart or table it needs. If the environment has a slide or presentation tool or skill, use it to build the actual deck from this outline. If not, give the outline.

If the environment has a document or spreadsheet tool, use it. Otherwise write markdown files and the .xlsx.

## Model

`scripts/build_model.py` takes a JSON file of inputs and writes an Excel workbook with live formulas:
- Inputs and assumptions
- ARR bridge by quarter
- Sales capacity by quarter
- Inverted funnel with time-based close rates
- Pipeline by source and starting coverage by quarter
- Marketing budget and efficiency ratios
- Scenarios (Baseline, Growth, Profit) with a 2028 out-year

Fill `templates/inputs.json` with the user's numbers (copy it first), then run:

```
python scripts/build_model.py my_inputs.json gtm_plan_2027.xlsx
```

Requires `openpyxl` (`pip install openpyxl`). See `examples/acme-flow/` for a full worked example.

## Style for everything you write

Plain words. Short sentences. Lead with the number, then the reason. Translate marketing metrics into money (pipeline dollars, bookings, CAC) for any exec or board audience. Put detail in the appendix.
