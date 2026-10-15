# Review request: policy note, monitor and publication readiness

You are reviewing a small research repository before it is published on GitHub
and cited in a job application. Do not modify any file except the review you
write. Write your review to `reviews/2026-10-15-final-review.md`.

A first review of the data layer and the baseline estimates was done on 13
October: see `reviews/2026-10-13-baseline-review.md` and the author's response
in `reviews/2026-10-13-baseline-response.md`. Do not repeat its findings unless
a fix was not applied or was applied wrongly.

## What changed since the first review

- `src/models/local_projections.py`: Newey-West standard errors, ECB meeting
  flag computed per series and horizon, a `robustness()` function with five
  specifications at h = 1, 2 and 5.
- `src/models/plot_robustness.py` and `outputs/figures/lp_robustness.png`.
- `note/policy_note.md`: a two-page policy note in the style of an ECB
  Economic Bulletin box.
- `sql/monitor_summary.sql`, `src/dashboard/build_monitor.py`,
  `outputs/monitor/`, `outputs/excel/`: a monitor of the latest market levels.
- `README.md`, `Makefile`, `tests/test_event_windows.py`.

## How to run it

    make setup
    make            # database, estimates, figures, monitor, tests

`make` does not download data; the raw files are in `data/raw/`.

## Questions, in order of importance

1. **Every number in the note and the README.** Check each number, range and
   significance statement in `note/policy_note.md` and `README.md` against
   `outputs/tables/lp_baseline.csv` and `outputs/tables/lp_robustness.csv`,
   and against the code where the tables do not contain it (sample sizes,
   standard deviation of the surprise, counts of windows with an ECB meeting,
   Bund/Treasury ratios). List every mismatch, including rounding that changes
   the meaning.

2. **Claims in the note.** Does each sentence say no more than the estimates
   support? Pay attention to: the two channels and their effect on inflation
   in "Why it matters" and "Implications"; "the most robust result"; the
   explanation offered for why unscheduled announcements weaken the estimates;
   the sentence that part of the baseline yield response "may reflect ECB
   decisions". Check that the references are correct and that each one
   supports what it is cited for.

3. **The monitor query.** In `sql/monitor_summary.sql`: are the one-week,
   one-month and one-year comparison values the right observations? Is the
   US-German spread computed on matching dates? Is the percentile correct, and
   is the comparison with 1999 meaningful for every series (the broad dollar
   index starts in 2006)? Is `INTERVAL 1 MONTH` safe at month ends?

4. **Reproducibility from a clean copy.** Clone the repository into a
   temporary folder, run `make setup` and `make`, and check that the tables,
   figures and monitor match the committed ones. Report any file that differs
   and why (for example matplotlib or Excel metadata).

5. **Publication readiness.** Before this goes public: any personal paths,
   email addresses, keys or tokens in tracked files or in the git history? Any
   file that should not be published? Anything in the README that a reader
   could not run or would misunderstand?

6. **Consistency.** Do the README, the note, the figure captions and the code
   comments describe the sample, the window, the standard errors and the
   horizons in the same way?

## What I want back

- Findings ordered by severity (blocking, important, minor), each with the
  file and line, what is wrong, how you verified it (run the code, do not
  guess), and the smallest fix.
- A separate list of what you checked and found correct.
- No rewrite and no new features. The author must be able to explain every
  line in an interview, so prefer the simplest fix.
- If you could not verify something, say so plainly.
