# Capacity and pipeline

Mostly Kellogg's ideas, in my own words. See `sources.md` for the original posts.

## Sales capacity

Capacity is how many bookings your reps can produce. Build it by quarter:

- Starting ramped reps
- Hires by quarter
- Ramp time (quarters until a new rep is fully productive)
- Ramped productivity (bookings per ramped rep per quarter)
- Attrition (reps lost per quarter)

Ramped rep equivalents in a quarter = fully ramped reps + partly ramped reps weighted by how far along they are.

Capacity bookings = ramped rep equivalents x productivity.

If capacity is below the bookings target, the plan has a hole. Fix it with more hires earlier, better productivity (with a reason), or a lower target. Don't paper over it.

One more thing people forget: every rep needs pipeline. If a rep needs $X of pipeline per quarter and your pipe/spend is 15:1, that rep needs $X / 15 of demand gen spend each quarter. Model that cost along with salary.

## The inverted funnel

Start at the bookings target and work backward:

1. Bookings target / ASP = deals needed
2. Deals needed / close rate = opportunities needed
3. Opportunities needed / stage conversion = earlier-stage volume needed (SQLs, meetings, or whatever stage the company really tracks)

Build one funnel per segment and per motion. Enterprise and mid-market don't share conversion rates, so don't blend them.

## Time-based close rates

A single close rate hides timing. If oppties take three quarters to close, Q1 bookings come mostly from pipeline made in 2026, not from Q1 marketing.

Fix this with a cohort view. For oppties created in a quarter, track what share closes:
- In the same quarter
- One quarter later
- Two quarters later
- Three or more quarters later

Then build a waterfall. Each quarter's bookings = the sum of every prior quarter's oppties times the close rate for that lag. This tells you two things:
1. How much of 2027 is already spoken for by the 2026 pipeline
2. When 2027 oppties need to be created to land bookings in time

The model in `scripts/build_model.py` does this.

## Close rate vs. win rate

They're different.
- Win rate is a period metric. Of the deals that ended this quarter, how many did we win?
- Close rate is a cohort metric. Of the oppties we created, how many did we eventually win, and when?

Use close rates for planning. Use win rates to track competitive performance.

## Coverage is not 1 / win rate

A common mistake: "Our win rate is 25%, so we need 4x coverage." That's wrong for a few reasons. Win rates ignore slips. Win rates are based on when deals end, not what was in pipeline at the start of the quarter. And some in-quarter bookings come from oppties created during the quarter.

The better way: look at history. Take starting pipeline in each past quarter and compare it to what actually closed that quarter. That ratio gives you the conversion of starting pipeline. Your coverage target is 1 / that conversion, plus a little buffer.

## Starting coverage by quarter

Don't manage to rolling four-quarter pipeline. Nobody has a rolling four-quarter quota. Set a starting-coverage target for each quarter (for example 3.0x of the quarter's new bookings target on day one) and track how next quarter's pipeline is forming during the current quarter.

Look at this-quarter, next-quarter, and all-quarters pipeline together. Big pipeline five quarters out is often junk deals that keep slipping.

## The four sources of pipeline

Pipeline comes from four places:
1. Marketing (inbound and programs)
2. SDR or outbound
3. Sales self-sourced
4. Partners and alliances

Set a target for each. The CMO should own the total coverage picture, not just marketing's share. If another source is coming up short, marketing should see it early and help.

## When the funnel and the target don't match

If the inverted funnel says you need 2x the oppties you've ever made, stop. Either the target, the spend, or a conversion assumption has to change. Write down which one and why.
