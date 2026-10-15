# Response to the final review of 15 October 2026

The review found that every estimate reproduces from a clean copy, one test
that fails in another environment, and twelve points on reporting and
interpretation. All were accepted. No estimate in the baseline changed; the
"no ECB meeting" robustness check lost one announcement (see 5).

| # | Finding | Decision | What changed |
|---|---|---|---|
| 1 | The SQL/Python test fails when Pandas and DuckDB store dates at different resolutions | Accepted | `tests/test_event_windows.py` converts both date columns to the same type and checks that the indexes are equal before comparing changes and flags. `requirements.txt` pins the versions that produced the committed results, and `make setup` uses Python 3.12 |
| 2 | The robustness summary named one loss of significance; there are four | Accepted | Note and README list all four: German and US yields at h = 2 without ECB windows, German yield at h = 2 and 5 with the raw surprise |
| 3 | The two inflation mechanisms and "without any ECB action" were presented as findings | Accepted | Note and README present them as possible mechanisms, all else equal, that are not estimated. "Without any ECB action" removed. "About half" restricted to the first horizons |
| 4 | Excluding ECB windows cannot show that ECB decisions explain part of the response | Accepted | The note says the German estimate is sensitive to those windows and that the comparison cannot distinguish ECB news from sample composition |
| 5 | The no-ECB check treated the missing meeting calendar before March 1999 as "no meeting" | Accepted | `build_panel` marks windows that start before the calendar; the no-ECB specification drops them (the announcement of 3 February 1999). The robustness table and figure were regenerated |
| 6 | January 2020 is in the sample; only March-December 2020 is missing | Accepted | Note, README, figure captions and code comments corrected; a correction is appended to the 13 October response |
| 7 | "The day after" and "after two days" suggest calendar days | Accepted | Results are described at h = 1, 2 and 5, with h defined as observations after the announcement day |
| 8 | "Does not react" claims a zero effect; the timing of the later CISS rise was wrong | Accepted | "No statistically detectable response"; point estimates positive from h = 3, pointwise significant from h = 12, treated as exploratory |
| 9 | The standard deviation of the surprise is 5.2 bp, not 5.3 | Accepted | Corrected in both places |
| 10 | "Most robust" needs a horizon; the turbulence explanation is a hypothesis | Accepted | "The early exchange-rate response" (h = 1 and 2); turbulence described as one possible explanation, not tested |
| 11 | The percentile of the broad dollar index starts in 2006 | Accepted | Marked in the monitor table and in the README |
| 12 | Personal email in commit metadata; private brief tracked | Accepted | The brief was removed from the repository and its history, and the commit author address was replaced with the GitHub noreply address, before publication |
| 13 | README commands assume an active environment; versions not recorded | Accepted | Commands use `.venv/bin/python`; versions pinned; README states that figures can differ pixel by pixel with other versions |
| - | No license | Accepted | MIT License for the code; the README says the raw data belong to their providers and remain subject to their terms |
| - | Citations listed but not attached in the text | Accepted | The note cites Chavleishvili and Kremer (2023) for the CISS and Newey and West (1987) for the standard errors |
