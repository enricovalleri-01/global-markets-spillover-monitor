# Review request: data layer and baseline local projections

You are reviewing a small research repository. Do not modify any file except
the review you write. Write your review to `reviews/2026-10-13-baseline-review.md`.

## What the project does

It estimates how euro area financial variables respond to US monetary policy
surprises. The shock is the Bauer-Swanson (2023) high-frequency surprise
around FOMC announcements (San Francisco Fed file, sample 1988-2023). The
responses are daily: German 10-year Bund yield (Bundesbank), EUR/USD ECB
reference rate, euro area CISS (ECB), and the US 10-year Treasury yield (FRED)
as a benchmark. The method is a daily local projection on announcement days:

    y(h trading days after the announcement) - y(last day before) = a + b * shock + e

for h = 1..20, one regression per series and horizon, HC1 standard errors,
shock scaled so that b is the response to 10 basis points. Baseline sample:
201 announcements, 1999-2023, with the orthogonalised surprise (not available
for 2020).

## How to run it

    .venv/bin/python -m src.ingest.download        # optional, raw files are in the repo
    .venv/bin/python -m src.transform.build_database
    .venv/bin/python -m src.models.local_projections
    .venv/bin/python -m src.models.plot_baseline
    .venv/bin/python -m pytest -q

## Files to read

- `src/ingest/download.py`
- `sql/schema.sql`, `sql/event_windows.sql`
- `src/transform/build_database.py`
- `src/models/local_projections.py`, `src/models/plot_baseline.py`
- `tests/test_event_windows.py`
- `outputs/tables/lp_baseline.csv`, `outputs/figures/lp_baseline.png`

## Questions, in order of importance

1. **Timing of the event window.** The window runs from the last observation
   strictly before the announcement day to the h-th observation strictly after
   it. Most announcements are at 2:00 or 2:15 pm US Eastern time, but some are
   in the morning, one is on a Sunday at 5:00 pm (15 March 2020) and several
   are unscheduled. For each response series, given the time of day at which
   it is recorded (ECB reference rate at 2:15 pm CET, Bundesbank end-of-day
   yield, FRED DGS10, CISS), is the reaction always inside the window and
   never outside it? Is there an off-by-one error in the `np.searchsorted`
   logic of `build_panel`, or a disagreement with `sql/event_windows.sql`?

2. **Units and scaling.** The source file stores MPS and MPS_ORTH in
   percentage points; `build_database.py` multiplies by 100 and
   `local_projections.py` divides by 10. Check this against the data, and
   check the three change types (`diff_bp`, `log_pct`, `diff`).

3. **Sample construction.** `load()` joins the announcements with the
   `event_windows` view for `bund_10y`. Does this join silently drop or
   duplicate announcements? Are there announcement days with more than one
   announcement, or announcements closer to each other than 20 trading days,
   whose windows overlap?

4. **Inference.** Are HC1 standard errors adequate here? If windows of
   different announcements overlap at longer horizons, the errors are
   correlated: say whether this matters in practice and what a simple,
   defensible alternative would be. Comment on the fact that 80 coefficients
   are estimated and read individually.

5. **Horizons across series.** Horizon h is counted in the trading days of
   each series, and the calendars differ (TARGET, German and US holidays). Is
   comparing the US and German yield responses at the same h misleading?

6. **Data parsing.** Check the three readers in `build_database.py`,
   especially the Bundesbank one, for rows that are dropped or misread.

7. **ECB meeting flag.** Check the definition of `ecb_meeting_in_window` in
   `sql/event_windows.sql`. The meeting dates start in March 1999.

8. **Tests.** Are the two tests meaningful? Name the two or three tests that
   would catch the most likely remaining mistakes.

9. **Interpretation.** The author intends to state: (a) the Bund yield rises
   by about half as much as the Treasury yield in the days after a surprise;
   (b) the euro depreciates on impact; (c) the delayed rise in the CISS is not
   reported as an effect. Do the numbers support (a) and (b) as stated? Is
   (c) the right call?

## What I want back

- Findings ordered by severity (blocking, important, minor), each with the
  file and line, what is wrong, how you verified it (run code, do not guess),
  and the smallest fix.
- A separate list of things you checked and found correct.
- No rewrite of the code and no new features. The author must be able to
  explain every line in an interview, so prefer the simplest fix.
- If you could not verify something, say so plainly.
