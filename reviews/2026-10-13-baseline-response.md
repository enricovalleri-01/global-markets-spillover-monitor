# Response to the baseline review of 13 October 2026

The review found no implementation error and eight points on interpretation,
inference and tests. This file records what was changed for each and what was
not. The estimates were re-run after the changes; the point estimates are
unchanged, the standard errors are now Newey-West.

| # | Finding | Decision | What changed |
|---|---|---|---|
| 1 | The explanation of recording times was too strong; "on impact" is not what a daily window measures | Accepted | Comments in `sql/event_windows.sql` rewritten: some announcements are in the New York morning, and the window contains the reaction in both cases. Responses are described as cumulative daily responses. The German yield is described as what the source file says it is: a 10-year yield derived from the term structure of listed Federal securities |
| 1 | The Bundesbank yield is based on prices fixed around noon | Not verified | I could not confirm the time of day from the Bundesbank documentation, so the project makes no statement about it |
| 2 | HC1 standard errors ignore the overlap between windows of nearby announcements | Accepted | Baseline standard errors are Newey-West with two announcement lags; HC1 is saved next to them in `lp_baseline.csv` |
| 3 | The ECB flag was computed for the one-observation window and reused at every horizon | Accepted | The flag is now computed for each series and horizon in `build_panel`. The SQL flag is renamed `ecb_meeting_in_h1_window`. It is a calendar match by date, and the meeting dates start in March 1999 |
| 3 | 8 October 2008 was a coordinated cut and cannot identify a US-only surprise | Accepted | Added as a robustness check (`no_coordinated_cut`) |
| 4 | The 90% bands are pointwise; "half as much" holds only at the first horizons | Accepted | Figure caption says "pointwise". Conclusions are based on horizons 1, 2 and 5, fixed in `MAIN_HORIZONS` after the first baseline run and before any robustness check |
| 4 | A formal test of the Bund/Treasury ratio would need joint inference | Not done | The ratio is reported as a description of the point estimates, not as a tested result |
| 5 | The same horizon ends on different calendar days for different series | Accepted as a stated limitation | Axis label and caption say that horizons are counted in each series' own calendar |
| 6 | Two announcements on one day would be double counted | Accepted | `build_panel` stops with an error if announcement dates are not unique; a test covers it |
| 7 | The tests did not check the sample, the scaling or horizons above 1 | Accepted | Four tests added: sample size (214 and 201), the three change types, windows on a small made-up calendar with a holiday, a Sunday and an ECB meeting, and the uniqueness check. The SQL/Python test now also compares the ECB flag and the number of rows |
| 8 | "2020 excluded" did not explain all 13 missing announcements | Accepted | Caption names 2020 and 17 September 2001 |

## What the review changed in the results

Nothing in the point estimates. With Newey-West errors the responses at
horizons 1, 2 and 5 keep their significance; the German yield at horizon 10 is
no longer significant at the 10% level, which is one reason the conclusions
stop at horizon 5.

The count of windows with an ECB meeting is 27 of 201 at horizon 1 and 142 of
201 at horizon 20. Excluding them is therefore only informative at short
horizons.
