# Baseline review — 13 October 2026

The saved estimates are reproducible and the specified date-window arithmetic is correct. The main concerns are interpretation of the recording times, inference at longer horizons, and the meaning of the ECB flag. I found no blocking implementation error in the current 1999–2023 baseline.

## Verification performed

Read all requested files and inspected the PNG. Using the repository's `.venv/bin/python -B`, rebuilt the four tables and SQL view in an in-memory DuckDB database from the raw files, then ran `load`, `build_panel`, and `estimate`. All 80 result rows match the saved CSV after its four-decimal rounding. Independently parsed the CSV records with Python's `csv` reader, checked source-file hashes, compared raw-derived observations with the existing database, counted window overlaps and calendar differences, and refitted regressions with HAC standard errors. Temporary verification scripts and logs were outside the repository; no source, raw data, database, or output was changed.

The requested pytest command exits with signal 11 (exit 139) on this host, including with capture disabled. I cannot report a successful pytest run. Both existing test functions **pass when invoked directly**, with DuckDB restricted to one thread. This is an execution-environment limitation, not evidence that either assertion fails.

## Findings, ordered by severity

### Blocking

None for reproducing this baseline or implementing its explicitly stated date-based estimand. The causal and significance claims need the qualifications below.

### Important

**1. Recording-time explanations and “on impact” interpretation are too strong.**

- **Location:** `sql/event_windows.sql:4–7`; `src/transform/build_database.py:20`; `src/models/plot_baseline.py:15`; `src/models/local_projections.py:63–66`.
- **Problem:** Excluding announcement-day observations is consistent with the requested estimator, but the SQL explanation treats all announcements and European observations alike. Morning announcements can precede that day's European observations; DGS10 usually already incorporates an afternoon FOMC announcement on the announcement date. This does **not** remove the reaction from a difference ending the following day: the difference still includes announcement-day movements. It does make h=1 a broad cumulative window, not an intraday impact response, and adds an extra US post-announcement observation interval.
- **Verified:** For all 214 loaded announcements and all four series, the chosen lower date is strictly before the event date and the upper date strictly after it. The Sunday event, 15 March 2020, uses Friday 13 March to Monday 16 March in all four series. There is no Sunday-indexing mistake; this event is excluded from the orthogonalised baseline. Retained events include 7:00am, 8:00am, 8:30am and other morning announcements, so the blanket “European markets are closed” explanation is false.
- **Series-specific assessment:**

  | Series | What the recording convention implies |
  | --- | --- |
  | EUR/USD | The reference fixing is a European afternoon snapshot, before usual 2:00/2:15pm ET FOMC announcements, but after some morning US announcements. The next-date fixing brackets either case. Current ECB documentation says the concertation generally occurs around 14:10 CET and publication around 16:00; publication time is not fixing time. [ECB exchange-rate documentation](https://www.ecb.europa.eu/stats/exchange_rates/html/index.en.html). |
  | German yield | The raw header identifies a **yield derived from the term structure**, for a hypothetical annual-coupon security with ten years remaining, rather than an individual benchmark Bund's closing yield. Bundesbank describes its securities reference prices as fixed around noon. This contradicts the review premise of an end-of-day observation. [Bundesbank reference prices](https://www.bundesbank.de/en/service/federal-securities/prices-and-yields), [term-structure documentation](https://www.bundesbank.de/en/statistics/money-and-capital-markets/interest-rates-and-yields/term-structure-of-interest-rates/term-structure-of-interest-rates-793592). |
  | DGS10 | Treasury describes the constant-maturity par yields as derived from quotations at or near 3:30pm each trading day. The usual FOMC response is already inside that day's yield and remains inside the previous-date-to-next-date difference. [Treasury methodology](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?page=1&type=daily_treasury_yield_curve). |
  | CISS | `SS_CIN` is the **New CISS**, a daily composite, not one price observed at one common instant. ECB says it is updated with the previous day's data; that release lag does not justify shifting `TIME_PERIOD`. I could not verify one common intraday cutoff, or historical cutoffs for every component. [ECB CISS metadata](https://data.ecb.europa.eu/data/datasets/ciss/data-information). |

- **Conclusion:** For correctly dated contemporaneous market observations, the date bounds conservatively bracket the announcement, including morning, unscheduled and Sunday events. No observed timing case puts the immediate announcement outside those bounds. That is not a guarantee of capturing every component's reaction or its persistence, particularly for CISS. It also does not exclude unrelated news or pre-announcement movement from the window. Historical fixing times and the exact input timing of this Bundesbank series were not independently established for every date.
- **Smallest fix:** Keep the requested date arithmetic; correct the comments and yield description, and replace “on impact” with “over the window ending at the first post-announcement reference fixing.” Explicitly describe these as cumulative daily responses and name the fitted German yield accurately. Use proper Europe/Berlin and America/New_York time zones if subsequently documenting individual timestamps: the offset is not always six hours.

**2. HC1 ignores cross-announcement dependence; overlap is limited but real.**

- **Location:** `src/models/local_projections.py:77–80`.
- **Problem:** HC1 allows heteroskedasticity but omits covariance between different announcements' regression scores. Overlapping response intervals share daily innovations and can contain another policy surprise. The latter also complicates a single-shock interpretation. Overlap alone does not prove large covariance or coefficient bias; neither should be asserted without checking.
- **Verified:** Among the 201 retained events, using overlap of the change intervals `(date_before, endpoint]`, Bund, Treasury and EUR/USD have 0 overlapping pairs at h=1, 3 at h=5, 6 at h=10 and 13 at h=20. CISS has 12 at h=20. Twelve Bund h=20 windows contain a later retained announcement. Examples include 7/10/17 August 2007, 22/30 January 2008, and 16 September/8 October 2008. The August triple includes dependence two announcements apart. These are concentrated exceptional episodes, rather than overlap between most regularly scheduled meetings.
- **Practical size:** Sorted by announcement date, HAC with Bartlett weights, two announcement lags and finite-sample correction gives the following standard errors:

  | Series/h | HC1 | HAC(2) |
  | --- | ---: | ---: |
  | Bund, 1 | 1.0563 | 1.0784 |
  | Bund, 20 | 2.9726 | 3.1424 |
  | Treasury, 20 | 4.8313 | 5.2074 |
  | EUR/USD, 20 | 0.2955 | 0.3037 |
  | CISS, 20 | 0.01325 | 0.01525 |

  The early yield/FX signs survive this sensitivity check; some marginal horizon-level conclusions change. For example, Bund h=10 ceases to meet the 10% threshold, and CISS h=11 does too. CISS h=20 remains pointwise significant, with HAC(2) p≈0.0371. HAC need not always increase an SE.
- **Smallest fix:** Use chronologically sorted, announcement-level Newey–West HAC with two lags as a simple baseline sensitivity, checking one and three lags too. Lags count **announcements**, not trading days; two covers the maximum event-order separation of overlapping retained windows observed here. It remains an approximation for irregularly spaced events. Report that limitation and the HC1/HAC comparison. Do not cluster by individual announcement: there is only one row per announcement in each regression, so that would not address this dependence. HAC changes inference, not contamination by later shocks.

**3. The ECB flag is a horizon-1 calendar flag, not a measure of ECB reaction inside each LP window.**

- **Location:** `sql/event_windows.sql:37–43`; `src/models/local_projections.py:33–36,71`; `sql/schema.sql:36`.
- **Problem:** The SQL predicate correctly implements its advertised date interval `(date_before, date_after]`, including no-change meetings. However, `load()` imports only the Bund h=1 flag and repeats it over all series and horizons. Also, a date match does not establish that the ECB announcement preceded the endpoint's actual fixing. The comment “the change also contains the reaction” is too categorical. Meetings before March 1999 are absent, but `EXISTS` returns false rather than unknown.
- **Verified:** There are 27 flagged retained Bund h=1 events. Against the actual h=20 Bund endpoints, **142** retained windows contain a meeting in the supplied calendar: **115** additional windows retain false flags. The 13 December 2023 FOMC window ends 14 December and is flagged, but a noon German snapshot cannot include a later afternoon ECB decision simply because both share a date. The 3 February 1999 FOMC window runs 2–4 February and returns false; the ECB's [4 February 1999 statement](https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/1999/html/is990204.en.html) confirms a meeting that is missing from the supplied calendar. This is a missing date match, not proof that its decision affected the noon Bund endpoint.
- **Smallest fix:** If this flag remains unused, rename/document it as a **Bund h=1 calendar-overlap flag**, remove the claim of certain reaction inclusion, and treat pre-March-1999 coverage as unknown. No baseline coefficient currently uses it, so this does not change the estimates. Before using it for exclusions or interpretation, compute it for the response series and horizon being analysed and distinguish date candidates from timestamp-confirmed exposure. A false flag cannot support “no ECB news.”
- **Identification caution:** The retained 8 October 2008 event has orthogonalised shock +11.2797 bp and is flagged; the [ECB confirms a simultaneous coordinated rate cut](https://www.ecb.europa.eu/press/key/date/2009/html/sp090406.en.html). That observation cannot isolate a US-only action. The smallest robustness check is to omit that event and state the joint-policy limitation; merely adding a meeting dummy does not separate simultaneous shocks. I verified its inclusion and joint-policy nature, but did not estimate that exclusion sensitivity.

**4. The 90% bands are pointwise, and “half as much” is only an early-horizon description.**

- **Location:** `src/models/local_projections.py:80`; `src/models/plot_baseline.py:38–39`; `outputs/tables/lp_baseline.csv:2–81`.
- **Problem:** Eighty coefficients are estimated on substantially related data. Reading each 90% interval separately and selecting horizons after seeing them does not provide 90% coverage for the whole response path. Separate yield regressions also do not test the Bund/Treasury ratio, because their estimates share shocks and have cross-series covariance.
- **Verified interpretation:**
  - **(a)** At h=1, Bund +2.4293 bp versus Treasury +4.6777 bp gives a ratio of **0.519**. Ratios at h=2–4 are 0.574, 0.530 and 0.497. Thus “about half at the first few horizons” describes the point estimates. It is not a stable ratio over 20 days: h=5 gives 0.744, h=7 0.955 and h=20 0.368. At h=20 both yield intervals include zero. No formal test of “half” is supplied.
  - **(b)** EUR/USD h=1 is **−0.4435 log-percent**, HC1 SE 0.1457, 90% interval [−0.6831, −0.2039], p=0.0023. This supports a weaker euro in the first post-announcement fixing window, conditional on the design. It does not establish an intraday impact effect.
  - **(c)** CISS is close to zero initially (h=1 −0.0007, p=0.8043), but the delayed positive association is real in the saved estimates: h=20 +0.0318 index points, HC1 p=0.0165. Not claiming a demonstrated causal stress effect is the right call; saying “no effect” or hiding the delayed estimates is not. The positive path remains exploratory because of dependence, multiple comparisons, recording-time uncertainty and intervening news. Its minimum saved p-value, 0.0118, would not pass a simple 5% Bonferroni threshold of 0.05/80=0.000625; that adjustment is conservative and the tests are not independent.
- **Smallest fix:** Label the shading “pointwise 90% intervals,” qualify (a) and (b) as above, and retain CISS as an exploratory result without a causal claim. Avoid selecting individually significant horizons as independent evidence. A prespecified early horizon is the simplest basis for the main comparison; a formal ratio claim would need joint inference and is not necessary for this descriptive baseline.

**5. Equal horizon numbers do not mean equal elapsed time across series.**

- **Location:** `src/models/local_projections.py:57–66`; `src/models/plot_baseline.py:34`.
- **Problem:** This implements the requested series-specific calendars correctly, but an unqualified US/German comparison at equal h suggests common dates and recording times that are often absent.
- **Verified:** Among 201 retained events, Bund and Treasury endpoints differ for 4 events at h=1, 34 at h=5, 81 at h=10 and **168 at h=20**. At h=20, Treasury minus Bund endpoint differences range from −5 to +5 calendar days. For 10 November 2004, h=1 ends 11 November for Bund and 12 November for Treasury. For 30 April 2008, it ends 2 May for Bund and 1 May for Treasury. Typical h=20 elapsed times are 28 days for Bund and 29 for Treasury, but individual dates vary. Intraday cutoffs differ even when dates agree.
- **Smallest fix:** Change the axis/caption to “h subsequent observations in each series' calendar” and disclose the mismatch. This is adequate for descriptive comparisons. If asserting responses at the same elapsed time, compare common calendar-date endpoints; do not silently relabel the current results.

### Minor

**6. Same-date announcements would multiply panel rows, although none occur in this baseline.**

- **Location:** `src/models/local_projections.py:61,69–71`; `sql/schema.sql:33`.
- **Problem:** The database identifies events by `(date, time_et)`, but Python iterates dates and merges on date alone. Two events on one day generate four rows per series/horizon instead of two.
- **Verified:** The entire workbook has seven dates with two announcements, all in 1988–1991; there are no repeated announcement dates from 1999 onward. Injecting a second timestamp on one retained date gives **320** panel rows rather than the expected 160 (2 events × 4 series × 20 horizons). The current baseline is unaffected; expanding `START` would expose the bug.
- **Smallest fix:** Assert event-date uniqueness before building the current daily baseline. Supporting multiple events would require carrying the timestamp through the panel and specifying how same-day shocks are treated; that is beyond this review's requested scope.

**7. Existing tests are useful integration checks, but not independent validation of window semantics or sample completeness.**

- **Location:** `tests/test_event_windows.py:9–21,24–30`.
- **Problem:** The first test can catch SQL/Python disagreement, but both implementations can share the same timing assumption. Its intersection check ensures existing Python rows are in SQL; it does not detect announcements already lost by `load()`. Neither test checks h>1, scaling, or duplicate-event behavior. Both depend on the existing database rather than fresh fixtures.
- **Verified:** Direct execution passes both assertions. Independent fresh-data calculation produces **856** h=1 rows (214 events × 4 responses), with maximum SQL/Python change discrepancy exactly zero. The known Bund window is indeed 2.25% to 2.09%, −16 bp.
- **Smallest fix:** Keep these checks and add the three compact tests listed below. No test code was changed.

**8. The stated sample exclusion is incomplete.**

- **Location:** `src/models/local_projections.py:77`; `src/models/plot_baseline.py:38`.
- **Problem:** “2020 excluded” is true but does not explain all 13 dropped events.
- **Verified:** There are 214 post-1999 announcements, of which 201 have `MPS_ORTH`. Missing values comprise all 12 recorded 2020 events and **17 September 2001**. The workbook's Description sheet explains the latter's terrorist-attack/market-closure contamination. The Bund join drops and duplicates **zero** post-1999 announcements, and every fitted series/horizon has n=201.
- **Smallest fix:** State “201 announcements; 2020 and 17 September 2001 excluded because the orthogonalised surprise is missing.” No change to the estimation is needed.

## Checked and found correct

- **No searchsorted off-by-one:** `side="left" - 1` selects the last strictly earlier observation; `side="right"` selects the first strictly later one; `i_after + h - 1` selects the h-th strictly later observation. SQL uses the same strict inequalities. Changing `right` to `left` would violate the requested definition on observation dates.
- **Shock scaling:** The source values have the percentage-point scale specified in the request. For 3 January 2001, raw MPS is approximately −0.126589 and MPS_ORTH −0.102945; database values are −12.658904 and −10.294493 bp. Dividing bp by 10 means a 10 bp surprise is one regressor unit. This is a surprise to the futures-implied policy path, not necessarily an actual 10 bp target-rate increase: the workbook describes a principal component normalised to ED4.
- **Changes:** `diff_bp` is appropriate for yields stored in percent; 2.25→2.09 gives −16 bp. `log_pct` is 100 times the log ratio; EUR/USD 1.100→1.089 gives −1.00503 log-percent, with negative meaning euro depreciation. `diff` preserves CISS index units; 0.20→0.21 is +0.01, not +1 or +100 bp. SQL and Python agree.
- **Readers on supplied files:** Independently enumerated CSV records match every stored date and numeric value, within floating-point rounding. Bundesbank has 10,665 date rows, 3,258 explicit `.` missing values and 7,407 retained values. Its BOM, quoted comma-containing description and third flag column are handled correctly; every discarded date row is flagged “No value available,” and every retained one has a blank flag. The first valid yield is 7 August 1997, 5.76%. No valid Bund row was silently lost. EUR/USD retains 7,112/7,174 rows; CISS 12,209/12,209; DGS10 16,178/16,898. Dates are unique. Auxiliary FRED series also parse correctly. Independent CISS parsing differs by at most 1.11×10⁻¹⁶, harmless binary-float rounding.
- **Stored database:** All 66,503 raw-derived observation keys and values match the existing database exactly. Pandas date-unit dtypes differ on readback, which is not a value discrepancy.
- **Provenance:** All nine raw-file SHA-256 values match their download-log entries. Download code checks HTTP errors and logs URL, UTC timestamp, byte count and digest. I did not redownload or validate future changes to upstream file formats.
- **Regression and figure:** Regressions include an intercept, drop missing shocks and use HC1 as advertised. The saved intervals are 90%, units/signs match the plotted series, and visual inspection agrees with the recomputed table. The displayed n=201 and 1999–2023 dates are accurate for these data.

## Three highest-value additional tests

1. **Small synthetic calendar fixture:** Include an event on an observation day, a Sunday, a holiday missing from only one series, and sample boundaries. Assert explicit before/after dates and changes at h=1 and h=2 in Python and SQL. Add two timestamps on one date and assert the proposed uniqueness check rejects them.
2. **Reader and scaling fixture:** Include Bundesbank BOM/quoted metadata, a valid yield, `.` plus its flag, and a negative yield; ECB/FRED missing values; and a known percentage-point shock such as 0.10. Assert retained rows, 10 bp conversion, regressor value 1, and all three change calculations. This catches the most likely unit and parsing regressions without testing every implementation line.
3. **Fresh-database sample/flag check:** Assert exact event keys before and after the Bund join, 214 loaded/201 retained events for the pinned raw files, all 80 regression sample counts, and h=1 SQL/Python equality without relying only on intersecting indices. Include an ECB meeting beyond h=1 but inside h=20, plus a pre-March-1999 coverage case, to enforce whichever limited flag semantics are chosen.

## Verification limits

I did not establish the exact historical intraday cutoff for every Bundesbank input or every CISS component, independently certify the completeness of the full ECB meeting calendar, estimate a joint Bund/Treasury ratio test or simultaneous confidence band, or refit after excluding coordinated policy actions. Those claims cannot be certified from this review. The numerical HAC checks establish sensitivity, not that HAC(2) fully resolves every source of dependence or identification risk.
