# gtm-plan-2027

A free Claude skill that builds a board-ready 2027 go-to-market plan for B2B SaaS.

It's built for AI-native CMOs at venture-backed, mid-market SaaS companies (roughly $10M to $150M ARR). It interviews you, builds the math, stress-tests the plan with the questions your board will ask, and hands you the deliverables.

Made by [Brandon Redlinger](https://stackandscale.ai) at Stack & Scale.

## What you get

- A one-page plan
- A full plan doc
- A live Excel model: ARR bridge, sales capacity, inverted funnel with time-based close rates, pipeline by source, starting coverage, budget, and three scenarios with a 2028 out-year
- Quarterly OKRs
- A board deck outline (Claude builds the actual slides if your setup has a slides tool)

## How it works

Twelve phases, in order:

1. Intake
2. Look back at 2026
3. Strategy before spreadsheet
4. Bookings and the ARR bridge
5. Sales capacity
6. Pipeline model
7. The demand system
8. Budget
9. AI-era assumptions
10. Scenarios
11. Board red-team
12. Outputs and operating cadence

## Where the ideas come from

Dave Kellogg's Kellblog is the backbone. Plan vs. budget, the inverted funnel, time-based close rates, starting coverage over rolling pipeline, the four sources of pipeline, and the board's questions on the marketing budget all come from his writing.

On top of that, the skill adds how to get the plan approved (start with finance, a few themes, three budget buckets, one page) and a modern demand system (one revenue plan, capture then create, a waste audit, and self-reported attribution).

When these ideas pull in different directions, Kellogg's math wins. The skill names the tension out loud. See `references/tensions.md`.

Kyle Poyar, Emily Kramer, Maja Voje, and others fill gaps.

All of this is in my own words, with links to Kellogg's originals in `references/sources.md`. Nobody named here is affiliated with or endorses this skill. Go read their stuff. It's better than any summary.

## Install

### Claude (web, desktop, mobile)
1. Download this repo as a ZIP (green Code button, then Download ZIP).
2. Unzip it, rename the folder to `gtm-plan-2027`, and zip that folder again (`SKILL.md` should sit right inside it).
3. In Claude, go to Settings, then Capabilities (or Skills), and upload the ZIP.
4. Start a chat and say: "Help me build my 2027 GTM plan."

### Claude Code
```
git clone https://github.com/guerrilla2799/gtm-plan-2027.git ~/.claude/skills/gtm-plan-2027
```
Then ask Claude Code to build your 2027 plan.

Menu names change, so check Anthropic's help center if you can't find the skills setting.

## Run the model on its own

```
pip install openpyxl
cp templates/inputs.json my_inputs.json   # then edit the numbers
python scripts/build_model.py my_inputs.json gtm_plan_2027.xlsx
```

Open the workbook in Excel or Google Sheets. Blue cells are inputs. Change one and everything updates.

## Worked example

`examples/acme-flow/` is a full run for a made-up $30M ARR company: inputs, the Excel model, the one-page plan, and the board red-team scorecard.

## Repo map

```
SKILL.md                  The skill itself
references/               One file per framework, plus tensions, benchmarks, sources
templates/                One-page plan, plan doc, OKRs, board deck, inputs
scripts/build_model.py    Builds the Excel model
examples/acme-flow/       Worked example
```

## License

MIT for the code and original writing. Ideas from the people credited above stay theirs. Kellblog materials are under their own Creative Commons license and aren't copied here.

## Feedback

Open an issue or find me on LinkedIn. If you use it for your plan, I'd love to hear what broke.
