# Final review — 15 October 2026

The numerical estimates reproduce. Publication should wait for the clean-build test failure and the important reporting/interpretation issues below. No exposed credential was found. Only this review was written in the source repository; builds and diagnostic scripts ran in temporary storage.

Reviewed commit: `da4e27b`. I read the 13 October review and response first. Previously resolved issues are not listed again. The sample-description correction below also corrects an error in that earlier review.

## Findings ordered by severity

### Blocking

**1. The documented clean build fails a test under an allowed dependency combination.**

- **Location:** `tests/test_event_windows.py:18–30`; `requirements.txt:1,5`; `README.md:122–126`.
- **Problem:** `make setup` succeeds, but `make` ends with one failed and five passed tests. The ECB-flag comparison raises `ValueError: Can only compare identically-labeled Series objects`. This is an index representation problem, not unequal flags. The advertised Python 3 requirement permits the system Python 3.9.6 used in this clean build.
- **Verification:** Cloned the repository into `/private/tmp/gmsm-final-review`, ran the two documented commands. Installed Pandas 2.3.3, DuckDB 1.4.5, NumPy 2.0.2, Statsmodels 0.14.6, Matplotlib 3.9.4 and Openpyxl 3.1.5. Python's panel index is `datetime64[ns]`; DuckDB's SQL result index is `datetime64[us]`. Both contain 856 rows. Converting both date columns to `datetime64[ns]` before indexing produces equal indexes, equal flags and equal changes. The other five tests pass unmodified. Setup initially encountered sandbox network restrictions; the authorized network retry succeeded, so that initial failure is not a repository defect.
- **Smallest fix:** Normalize both date columns to the same resolution before setting indexes, assert index equality, then compare changes and flags. Keep the substantive test. Merely converting flags to arrays would conceal misaligned event keys. Re-run the documented build after the fix.

### Important

**2. The robustness summary omits two failures of significance.**

- **Location:** `note/policy_note.md:96–99`; `README.md:101–103`.
- **Problem:** The text singles out German h=2 as losing significance. German h=5 with the raw shock also fails the stated 10% threshold; US h=2 without ECB windows does too. Calling German h=2 “the weakest estimate” is ambiguous without defining weakest.
- **Verification:** Reproduced `lp_robustness.csv` exactly. The four non-significant yield cells are German h=2/no-ECB (`p=0.1867`), German h=2/raw (`0.1545`), German h=5/raw (`0.1105`, interval `[-0.0955, 6.3429]`) and US h=2/no-ECB (`0.1395`). Every other yield cell at h=1,2,5 has p<0.10. Rounding 0.1105 to “about 0.1” cannot turn it into a significant result.
- **Smallest fix:** Name all four exceptions, or describe the sensitivity without implying that h=2 German yield is the only exception. Keep the correct claim that all yield point estimates retain their positive sign.

**3. The inflation channels and “without any ECB action” are presented as findings the design does not establish.**

- **Location:** `note/policy_note.md:17–26,106–111`; `README.md:107–109`.
- **Problem:** Higher financing costs and exchange-rate pass-through are plausible mechanisms, but these regressions estimate neither firms' borrowing costs nor import prices, inflation, activity or separate transmission channels. A German sovereign yield is not an estimate of euro area financing conditions as a whole. A bilateral depreciation does not identify aggregate import-price pass-through. “Its two components pull inflation in opposite directions” is too categorical as an empirical conclusion. “Without any ECB action” also contradicts the baseline's inclusion of meeting-overlap windows and the coordinated cut. The “about half” statement in Implications lacks the early-horizon restriction stated correctly elsewhere.
- **Verification:** Read and ran the regression specification: one shock plus an intercept, four market outcomes, no inflation outcome or mediation exercise. At Bund h=1, 27 retained windows have an ECB meeting-date match; 8 October 2008 remains in baseline. Ratios are 0.519, 0.574, 0.530 and 0.497 at h=1–4, but 0.744 at h=5 and 0.955 at h=7.
- **Smallest fix:** Present the two inflation mechanisms as possible, all-else-equal interpretations rather than measured effects; retain the explicit statement that inflation effects are unestimated. Restrict “about half” to the first few observations, describe the measured German yield, and remove the assertion that the baseline isolates changes without ECB action. No new model is required.

**4. Excluding meeting dates does not identify an ECB contribution to the baseline coefficient.**

- **Location:** `note/policy_note.md:98–99`; `src/models/local_projections.py:125–126`.
- **Problem:** “May therefore reflect ECB decisions taken the day after the Fed, which happens often” attributes an explanation to a sample comparison that cannot establish it. Exclusion changes the event sample; loss of significance is not a test of a difference between coefficients. A calendar flag includes meetings anywhere in `(date_before, date_end]`, including same-day meetings, and does not establish that an ECB decision preceded a fixing or that a policy change occurred.
- **Verification:** German h=2 falls from 2.9189 (SE 1.3494, n=201) to 1.7985 (SE 1.3621, n=163). This is principally a smaller estimate, not a large increase in its SE. Bund counts are 27, 38 and 46 at h=1,2,5: these are window-overlap counts, not counts of next-day ECB actions. The code contains no coefficient-difference test or decomposition.
- **Smallest fix:** Say the German estimate is sensitive to excluding calendar-overlap windows and that the comparison cannot distinguish ECB news from sample composition. Remove “therefore” and the unsupported next-day frequency claim.

**5. The earlier calendar-coverage caveat was not carried into the new exclusion specification.**

- **Location:** `src/models/local_projections.py:83–85,125–126`; `sql/event_windows.sql:41–46`; `note/policy_note.md:87–88`.
- **Problem:** The first review warned that the supplied calendar starts in March 1999. That is now documented in SQL, but the new no-ECB robustness specification treats absence from this incomplete calendar as a confirmed absence of a meeting. The retained February 1999 event is classified as no meeting and enters that specification.
- **Verification:** `load()` returns first ECB date 4 March 1999; 3 February 1999 is retained. The known 4 February meeting is absent from the calendar, and `build_panel` returns false for this event's windows. The [ECB's dated statement](https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/1999/html/is990204.en.html) establishes the missing meeting; it does not establish exposure before the German fixing.
- **Smallest fix:** For the no-ECB specification only, omit windows whose starting date precedes calendar coverage and describe the exclusion as “no recorded meeting in the covered calendar.” Rebuild its table/figure and update numbers affected. This avoids inventing missing historical meeting dates and leaves baseline unchanged.

**6. The accepted sample-description fix is still wrong: January 2020 is retained.**

- **Location:** `note/policy_note.md:35–36,89`; `README.md:84–85`; `src/models/plot_baseline.py:40`; `src/models/local_projections.py:127`; `reviews/2026-10-13-baseline-response.md:16,20` and the corresponding earlier-review statements.
- **Problem:** “All of 2020”/“2020 excluded” is false. The previous review incorrectly described all twelve missing 2020 observations as the entire year's events; the response and new prose inherited that error. The raw-shock variation restores March–December 2020, not January.
- **Verification:** Both the rebuilt database and workbook sheet `FOMC (update 2023)` contain 13 announcements in 2020. On 29 January, `MPS_ORTH=0.02509770` percentage points, or about 2.509770 bp, and the event enters baseline. The workbook Description explicitly says MPS_ORTH is unavailable for **March–December 2020**. Twelve such events and 17 September 2001 are dropped: 214−13=201. Raw-shock n=213 because September 2001 remains unavailable.
- **Smallest fix:** Replace the year-wide exclusion wording with “March–December 2020 and 17 September 2001”; correct the response record and figure caption and regenerate the PNG. Do not change the estimation sample to fit the prose.

**7. Calendar-day wording reintroduces a limitation already resolved in the method and caption.**

- **Location:** `note/policy_note.md:8–9,66–73,79–81`; `README.md:19–20`.
- **Problem:** “The day after,” “after two days” and “after five days” imply elapsed calendar time. The code uses the first, second and fifth available observations strictly after the announcement date. Weekends and holidays matter even at h=1.
- **Verification:** Rebuilt the panel and checked actual endpoints. The German and US h=1 endpoints differ for four retained announcements; h=5 differs for 34. The synthetic weekend/holiday test passes. This is new result prose inconsistent with the now-correct method description.
- **Smallest fix:** Use “first post-announcement observation” or h=1, h=2 and h=5 throughout these result sentences. Keep the explanation of series-specific calendars.

**8. Non-rejection is described as no stress response; its later timing is also misstated.**

- **Location:** `note/policy_note.md:10,74–77`; `README.md:22,115–116`.
- **Problem:** “Does not react”/“shows no reaction” asserts a zero effect. “Turns positive after about three weeks” confuses the sign of the estimate with its later pointwise significance. The positive point estimates start much earlier.
- **Verification:** Baseline CISS h=1,2,5 estimates are −0.0007, −0.0002, +0.0082, with p=0.8140, 0.9690, 0.2831. It is positive from h=3 (+0.0004), reaches +0.0153 at h=10, first has p<0.10 at h=12 (0.0897), and p<0.05 at h=13 (0.0381). The no-ECB h=5 robustness estimate is positive and pointwise significant at 10% (0.0139, p=0.0938), so an all-specification absence claim would also fail.
- **Smallest fix:** Say there is no statistically detectable early response in baseline; describe later positive estimates as exploratory. If mentioning three weeks, connect it to the later inference rather than the first positive sign. The existing caution about multiple testing is appropriate.

### Minor

**9. The surprise SD rounds to 5.2 bp, not 5.3.**

- **Location:** `note/policy_note.md:36,79`.
- **Verification/problem:** On the 201 nonmissing baseline shocks, Pandas sample SD is **5.2451938033 bp**, population SD **5.2321297885 bp**. Both round to 5.2 at one decimal; 5.3 can result from rounding 5.245 to 5.25 first. The one-SD h=1 responses are approximately +1.274 bp German yield and −0.233 log-percent EUR/USD, so the reported “about 1.3” and “about 0.2%” remain valid.
- **Smallest fix:** Use 5.2 bp in both locations, calculated without intermediate rounding. No table change.

**10. “Most robust” needs a horizon qualifier; the unscheduled-event explanation remains a hypothesis.**

- **Location:** `note/policy_note.md:11,93–102`.
- **Verification/problem:** FX h=1 ranges from −0.5384 to −0.4435 with p<0.10 in all five specifications; h=2 also passes in all five. At h=5 none of the five FX estimates passes, while all five US yield estimates do. Thus an unqualified ranking is misleading. Scheduled-only yields are indeed larger and have smaller SEs at all three main horizons (German h=5 SE only falls from 2.0404 to 2.0368). The exercise does not measure turbulence or establish why emergency events change the regression.
- **Smallest fix:** Qualify robustness as the early h=1–2 exchange-rate result. Keep the scheduled-only numerical comparison; explicitly identify emergency-market turbulence as a possible explanation, not something tested. “Consistent with” is already appropriately cautious, but the bold heading should describe the sample comparison rather than assert its mechanism.

**11. The percentile label overstates the broad dollar index's history.**

- **Location:** `README.md:165–166`; `sql/monitor_summary.sql:1–2,51–53`; `src/dashboard/build_monitor.py:45`; `outputs/monitor/monitor.md:10`.
- **Verification/problem:** The query correctly computes the share strictly below the latest observation among available dates from 1999 onward. Broad dollar data begin 2 January 2006 (5,203 observations); its percentile is 89.986546%. It cannot be compared with its own 1999 level or treated as having the same historical reference sample as other rows. The monitor introduction already discloses 2006, but the README and common table heading do not.
- **Smallest fix:** Add “since 2006 for the broad dollar index” to the README and qualify the table heading with an asterisk referring to the existing explanation. Keep the query's percentile formula; do not fill nonexistent 1999–2005 observations.

**12. Public history exposes the author's personal email; the private project brief is tracked.**

- **Location:** Git author/committer headers for all ten commits `bf94b4e` through `da4e27b` (metadata has no file line); `brief-bce-monitor.md:3–4`.
- **Verification/problem:** `git log --all` exposes the author's personal email address in both headers (address redacted from this review before publication). The brief explicitly describes the ECB internship application and instructs use as a CLAUDE.md/initial prompt. These are publication choices, not credentials or accidental machine paths. The raw FRBSF workbook also contains the source author's public contact address `michael.bauer@sf.frb.org` in its Description/shared strings and mailto relationship; commit messages contain the Anthropic noreply co-author address.
- **Smallest fix:** Decide before first push whether the personal address and internal brief should be public. If the address is unwanted, use a GitHub noreply address for existing author/committer metadata before publication; changing only future Git configuration will leave the old address visible. Omit the brief if it is not intended portfolio material. Do not scrub public source attribution out of the raw workbook.

**13. Exact artifact reproduction is environment-dependent, and standalone README commands assume an interpreter that setup does not select.**

- **Location:** `requirements.txt:1–8`; `README.md:122,135–141`; `Makefile:19–20`.
- **Verification/problem:** Only lower bounds are recorded. The successful artifact-generation portion of the clean build uses different versions from the author's environment, with the binary differences documented below. `make setup` creates `.venv` but does not activate it; the README's standalone `python -m ...` commands therefore need that environment explicitly. The Figures row also shortens the second command to bare `plot_robustness`, which is not the module invocation.
- **Smallest fix:** Record the Python/package versions used for publication; use `.venv/bin/python -m ...` consistently in the steps table, including the full robustness module name. Pinning the tested dependencies is the simplest option if exact rendering is a publication requirement. Do not mistake metadata-only Excel differences for changed results.

## Checked and found correct

### Numerical claims and implementation

- Both saved CSVs reproduce **byte for byte** from committed raw files: baseline 80 rows; robustness 60 rows (five specifications × four series × three horizons). The baseline rows of the robustness table agree with baseline estimates.
- Every cell in both README and note result tables agrees with the saved baseline at the displayed precision. These are the underlying main-horizon values and HAC p-values:

  | Series | h=1 beta (p) | h=2 beta (p) | h=5 beta (p) |
  | --- | ---: | ---: | ---: |
  | US yield, bp | 4.6777 (.0138) | 5.0890 (.0298) | 6.4684 (.0153) |
  | German yield, bp | 2.4293 (.0243) | 2.9189 (.0305) | 4.8145 (.0183) |
  | EUR/USD, log-percent | −.4435 (.0019) | −.5938 (.0082) | −.2650 (.2597) |
  | CISS, index points | −.0007 (.8140) | −.0002 (.9690) | .0082 (.2831) |

- The note table's baseline significance footnote and README's corresponding sentence are correct. Rounded CISS zeros in the note are not exact zeros; with the footnote they are acceptable display rounding, but cannot support “no response.” FX is a log-percent change, as implemented; ordinary-percent approximations at these small magnitudes do not alter the stated 0.44/0.59 figures materially.
- German robustness range 1.8–5.6 bp is correct over all five specifications and h=1,2,5 (actual extrema 1.7985 and 5.5530). FX's reported h=1 range −0.44% to −0.54% and significance in all five specifications are correct. All yield and FX signs survive all variations.
- Baseline n=201 throughout, post-1999 loaded n=214, raw-shock n=213, scheduled-only n=193, coordinated-cut exclusion n=200. No-ECB n at h=1,2 is 174,163 for all four series; h=5 is 155 German, 158 US, 156 FX and 160 CISS. Counts vary as intended with series calendars.
- Bund ECB counts are 27/201 at h=1, 38/201 at h=2, 46/201 at h=5, 142/201 at h=20. At h=20 the other counts are US 144, FX 138, CISS 130. The published h=1 count is correct, with the coverage caveat above.
- Bund/Treasury ratios h=1–4 are 0.5193, 0.5736, 0.5301, 0.4973; the h=5–20 range is 0.3681–0.9550. The note's approximate 0.37–0.95 description and descriptive-only qualification are reasonable. It supplies no formal ratio test and says so.
- README's 168/201 unequal German/US endpoints at h=20 is correct. CISS h=20 +0.0318 and HAC p=0.0371 correctly round to 0.03 and 0.04.
- Chronological sorting, HAC two **announcement** lags, finite-sample correction, HC1 columns and pointwise 90% intervals agree with code and figure captions. The series/horizon-specific ECB flag and duplicate-date assertion are implemented. Remaining timing claims are limited by daily data, as already recognized in the earlier review.
- Code/comment/history consistently record main horizons 1,2,5, chosen after the first baseline and before the committed robustness implementation. I cannot independently certify when the author made a private analytical decision; “fixed in advance” should always retain that stated chronology, not imply selection before seeing baseline results.
- Shock source is a futures-implied path surprise, scaled to 10 bp; it is not necessarily a 10 bp actual target-rate change. The 30-minute description is supported by the workbook and [FRBSF documentation](https://www.frbsf.org/research-and-insights/data-and-indicators/monetary-policy-surprises/). December 2023 is the sample endpoint; 2024–2025 lie outside it. Twenty horizons, 80 baseline coefficients, five specifications and six test functions are all correct counts. Download log dates support 12 October 2026; chart data start in 2019 as stated.

### Monitor query

Independently selected comparison observations in Pandas using calendar offsets and last available date on/before each cutoff, then asserted all 24 SQL changes and all eight percentiles against that calculation. The actual comparator dates are:

| Series | Latest | 1 week comparator | 1 month comparator | 1 year comparator | Percent below latest |
| --- | --- | --- | --- | --- | ---: |
| EUR/USD | 2026-10-12 | 2026-10-05 | 2026-09-11 | 2025-10-10 | 35.461192 |
| Broad dollar | 2026-10-02 | 2026-09-25 | 2026-09-02 | 2025-10-02 | 89.986546 |
| US yield | 2026-10-08 | 2026-10-01 | 2026-09-08 | 2025-10-08 | 92.169282 |
| German yield | 2026-10-12 | 2026-10-05 | 2026-09-11 | 2025-10-10 | 65.065193 |
| US−German spread | 2026-10-08 | 2026-10-01 | 2026-09-08 | 2025-10-08 | 73.772894 |
| Brent | 2026-10-06 | 2026-09-29 | 2026-09-04 | 2025-10-06 | 98.812744 |
| VIX | 2026-10-09 | 2026-10-02 | 2026-09-09 | 2025-10-09 | 29.078216 |
| CISS | 2026-10-08 | 2026-10-01 | 2026-09-08 | 2025-10-08 | 18.709500 |

- These are calendar-week/month/year comparisons relative to **each series' latest observation**, not five/twenty/two-hundred-and-fifty observation lags or comparisons relative to today's date. The SQL is correct for its stated definition. The rendered page should be read as a dated snapshot, not live prices.
- The spread joins both yields on exactly the same date, including comparison dates; the chart subtraction also requires both observations. Latest spread is 5.22−3.54=1.68 percentage points on 8 October, not 5.22−3.49 using Germany's newer 12 October value. Units and yield/spread conversion to bp are correct.
- Percentile is explicitly the empirical share **strictly below** the latest value, including the latest observation in the denominator. This is a valid stated convention, not a quantile interpolation or a midrank. All displayed integer percentiles round correctly. It describes the distribution of observed daily levels, not a probability forecast or a change since 1999. Broad-dollar coverage is the labeling issue above.
- `INTERVAL 1 MONTH` is safe in DuckDB for this calendar-month definition: executed 31 March 2024 minus one month → 29 February; 31 March 2023 → 28 February. Executed 29 February 2024 minus one year → 28 February 2023. The subsequent on/before lookup handles weekends and missing dates. There is no month-end rollover bug to fix. It should not be relabeled “30 days.”

### References and support

All five note references have correct authors, year, title and listed publication details. README's two entries are also correct:

- [Bauer and Swanson (2023), NBER Macroeconomics Annual 37, pp. 87–155](https://www.journals.uchicago.edu/doi/abs/10.1086/723574), plus the FRBSF update documentation, support the shock construction and orthogonalization. “As clean as current data allow” is a judgment, not a documented comparison with every alternative identification scheme; omitting that superlative would be more precise.
- [Jordà (2005), AER 95(1), 161–182](https://www.aeaweb.org/articles?id=10.1257%2F0002828053828518) supports horizon-specific local projection regressions; it does not independently validate this project's identification.
- [Miranda-Agrippino and Rey (2020), REStud 87(6), 2754–2776](https://doi.org/10.1093/restud/rdaa019) supports the cited international financial-spillover claim. It does not establish the two inflation-channel signs from this repository's estimates.
- [Chavleishvili and Kremer (2023), ECB WP 2842](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp2842~9a4cb3f225.en.pdf) concerns the enhanced daily CISS used here and its growth-risk applications. It is listed but not explicitly attached to the CISS sentence; adding that citation would clarify its role.
- [Newey and West (1987), Econometrica 55(3), 703–708](https://www.nber.org/papers/t0055) supports HAC covariance estimation. It does not choose two lags for this sample or prove all contamination resolved. This reference is likewise listed without an explicit author-year citation in the method paragraph.

The emergency-announcement turbulence explanation is plausible but not separately tested or supported by a dedicated citation. The note's predictions of imprecision in a future monthly inflation exercise are opinions, not verified results. Neither needs a new feature; qualify or omit them. The Markdown note has no fixed page layout, so the README's “two-page” description cannot be verified as a literal pagination claim.

## Clean-copy artifact comparison

After `make setup`, `make` generated all artifacts before the test failure. Compared each tracked output against the committed blob, decoded PNG pixels/metadata, and inspected the XLSX ZIP XML and all worksheet values.

| File | Fresh installed environment versus committed | Explanation/verification |
| --- | --- | --- |
| `outputs/tables/lp_baseline.csv` | Identical bytes | All coefficients, SEs, intervals, p-values and n reproduce |
| `outputs/tables/lp_robustness.csv` | Identical bytes | All five specifications reproduce |
| `outputs/monitor/monitor.md` | Identical bytes | Table and surrounding text reproduce |
| `outputs/figures/lp_baseline.png` | Different | Same 1600×1040 dimensions; Matplotlib 3.9.4 versus committed 3.11.2, different pixels and Software metadata |
| `outputs/figures/lp_robustness.png` | Different | Same 1760×608 dimensions; same rendering/version explanation |
| `outputs/monitor/monitor_charts.png` | Different | Same 1500×1350 dimensions; same rendering/version explanation |
| `outputs/excel/global_markets_monitor.xlsx` | Different | All sheet values equal; core timestamps, header/index styles and associated worksheet style references differ |

To verify the explanation rather than assume it, reran only artifact rendering/export in the clone with the source repository's existing Python 3.12.9 environment: Pandas 3.0.6, NumPy 2.5.4, DuckDB 1.5.6, Statsmodels 0.15.0, Matplotlib 3.11.2, Openpyxl 3.1.5. **All three PNGs then match committed bytes exactly.** The workbook's only differing XML member becomes `docProps/core.xml`, containing creation/modification timestamps; all other XML members match. Thus no substantive artifact discrepancy was found. This second rendering run is not a claim that the clean setup selected those versions or that its failed test passed.

## Publication checks and verification limits

- Enumerated all tracked paths and all 53 unique reachable file blobs across all refs/history, searched for personal absolute paths, email addresses, common credential/token forms and private-key markers, and unpacked XLSX XML/relationships. Inspected author/committer headers and commit messages separately. No `/Users/...` or `/home/...` machine path, recognized access token, private key, `.env`, virtual environment, processed database or cache is tracked in reachable history. The contact addresses and internal brief are disclosed above. This is a targeted audit, not proof against every possible secret encoding; unreachable objects and remote history outside this local repository were not reviewed.
- Raw FRBSF workbook core creator/last-editor fields are blank. Generated workbook creator is `openpyxl`; its core properties contain no personal machine path. PNG Software metadata identifies Matplotlib, not a private path.
- There is no tracked LICENSE file. Decide the intended code license before inviting reuse, and establish whether the raw third-party files may be redistributed. I did not certify source-by-source redistribution permissions; “public data” alone does not answer that question. No raw file is identified here as requiring removal on verified licensing grounds.
- No upstream data were downloaded or refreshed. The review verifies committed data and outputs, not their agreement with today's provider vintages. The thesis-derived ECB calendar was not independently certified complete; the known coverage problem matters specifically because it is now used for exclusions.
- No formal joint Bund/Treasury ratio test, coefficient-difference test, simultaneous confidence band, causal channel decomposition or intraday exposure certification was performed. Claims needing those are identified above rather than guessed.

The smallest publication path is to repair the date-index comparison, correct the sample/significance/SD statements and qualify the interpretations. The existing estimates and monitor query do not require a redesign.
