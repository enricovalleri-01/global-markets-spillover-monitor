# How much of a Fed surprise reaches euro area markets?

*Enrico Valleri · October 2026 · Code and data: this repository*

**In brief.** Using 201 FOMC announcements between 1999 and 2023, this note
measures how euro area markets move in the days after a US monetary policy
surprise. Over the window that ends at the first observation after the
announcement, a 10 basis point tightening surprise raises the German 10-year
yield by about 2.4 basis points, roughly half the response of the US 10-year
yield, and the euro loses about 0.4% against the dollar. There is no
statistically detectable response of euro area systemic stress in the first
days. The early exchange-rate response holds in every variation tried; the
yield responses keep their sign but lose significance in some variations.

## Why it matters

When the Federal Reserve surprises markets, euro area asset prices can move
even if the ECB changes nothing. A large literature documents that US monetary
policy moves asset prices well beyond the United States (for example
Miranda-Agrippino and Rey, 2020). Two of these prices matter for the ECB's
assessment, through mechanisms that, all else equal, point in opposite
directions for inflation: higher long-term yields tend to make borrowing more
expensive, which weighs on demand, while a weaker euro tends to raise the price
of imports. This note does not estimate either mechanism. It asks a narrower
question: how much do euro area yields and the exchange rate move in the days
after a Fed surprise, measured with a high-frequency shock.

## Data and method

The shock is the monetary policy surprise of Bauer and Swanson (2023), updated
by the Federal Reserve Bank of San Francisco: the change in interest rate
futures in a 30-minute window around each FOMC announcement. I use their
orthogonalised version, which removes the part of the surprise that could be
predicted from economic and financial data released before the announcement.
The series is not available for March to December 2020 or for 17 September
2001, which leaves 201 announcements. Its standard deviation is 5.2 basis
points.

The responses are daily: the German 10-year yield estimated by the Bundesbank
from the term structure of Federal securities, the ECB reference rate for
EUR/USD, the ECB's composite indicator of systemic stress (CISS; Chavleishvili
and Kremer, 2023), and the US 10-year Treasury yield as a benchmark.

Most FOMC statements are released in the European evening, after that day's
European prices are recorded, so for each announcement I measure the change
from the last observation before the announcement day to the h-th observation
after it. Weekends and holidays are skipped, so h counts observations, not
calendar days. I regress this change on the surprise, one regression per series
and horizon, which is a local projection (Jordà, 2005). Standard errors are
Newey-West (1987) with two lags, because announcements that are close in time
have overlapping windows. Conclusions are based on horizons 1, 2 and 5, fixed
after the first baseline estimate and before any robustness check was run.

## Results

![Cumulative response to a 10 basis point US monetary policy surprise](../outputs/figures/lp_baseline.png)

| Response to a 10 bp tightening surprise | h = 1 | h = 2 | h = 5 |
| --- | ---: | ---: | ---: |
| US 10-year yield (bp) | 4.7 | 5.1 | 6.5 |
| German 10-year yield (bp) | 2.4 | 2.9 | 4.8 |
| EUR/USD (%) | -0.44 | -0.59 | -0.27 |
| CISS (index points) | -0.001 | -0.000 | 0.008 |

*All estimates are significant at the 10% level except EUR/USD at h = 5 and the
CISS at all three horizons. Newey-West standard errors.*

- **Yields.** At h = 1 the German yield rises by 2.4 basis points, about half
  the US response of 4.7. The ratio stays close to one half over the first four
  horizons, then moves between about 0.37 and 0.95 as the estimates become
  noisier. I report it as a description of the point estimates, not as a tested
  result.
- **Exchange rate.** The euro depreciates by 0.44% at h = 1 and by 0.59% at
  h = 2. At h = 5 the estimate is still negative but no longer distinguishable
  from zero.
- **Stress.** The CISS shows no statistically detectable response at the main
  horizons. Its point estimates turn slightly positive from h = 3 and become
  pointwise significant only after about two and a half weeks, far from the
  horizons fixed in advance. With 80 coefficients estimated, some will look
  significant by chance, so I treat this later pattern as exploratory.

For scale: a surprise of one standard deviation (5.2 basis points) is
associated at h = 1 with a rise of about 1.3 basis points in the German yield
and a depreciation of the euro of about 0.2%.

## Robustness

![Baseline and four variations at the main horizons](../outputs/figures/lp_robustness.png)

I repeat the main horizons in four variations: excluding windows with a
recorded ECB Governing Council meeting (27 of 201 at h = 1) and the one
announcement that precedes the meeting calendar, which starts in March 1999;
using the raw instead of the orthogonalised surprise, which brings back March
to December 2020; keeping scheduled meetings only; and dropping 8 October 2008,
when the Fed and the ECB cut rates together.

- **The early exchange-rate response is the most stable result.** At h = 1 it
  ranges from -0.44% to -0.54% across the five specifications, and at h = 1 and
  h = 2 it is significant in all of them. At h = 5 it is significant in none.
- **The yield responses keep their sign everywhere.** The German estimates
  range from 1.8 to 5.6 basis points. Four yield estimates lose significance at
  the 10% level: the German yield at h = 2 and the US yield at h = 2 when
  windows with an ECB meeting are excluded, and the German yield at h = 2 and
  h = 5 with the raw surprise. The German estimate is therefore sensitive to
  excluding windows that overlap an ECB meeting; the comparison cannot tell
  whether this reflects ECB news or a different sample of announcements.
- **With scheduled meetings only, both yield responses are larger and more
  precisely estimated.** One possible explanation, not tested here, is that
  emergency announcements tend to coincide with turbulent markets.

## Implications

In the first days after a Fed surprise, the German 10-year yield moves in the
same direction as the US yield, by about half as much, and the euro moves the
opposite way. Part of the change in euro area market conditions around FOMC
meetings is therefore associated with US policy news. For the assessment of the
euro area monetary policy stance, the two prices measured here relate to
mechanisms that would push inflation in opposite directions; whether either
mechanism operates, and which would dominate, is not estimated here.

## What this analysis does not show

- **The effect on financing costs, inflation or activity.** The note measures a
  German government bond yield and a bilateral exchange rate, not euro area
  borrowing costs, import prices or inflation. I expect a monthly analysis of
  inflation to be too imprecise to conclude much with surprises of a few basis
  points, but that is a judgement, not a result.
- **The channel behind the yield response.** The estimates do not separate
  expected future short rates from term premia.
- **Intraday reactions.** Daily windows also contain other news, and the
  overlap with ECB meetings is identified by date, not by time of day.
- **Recent years.** The surprise series ends in December 2023, so the
  2024-2025 easing cycle is outside the sample.
- **Same horizon, same day.** Holidays differ between countries, so the same
  horizon can end on different calendar days for German and US yields.

## References

Bauer, M. D. and Swanson, E. T. (2023). A reassessment of monetary policy
surprises and high-frequency identification. *NBER Macroeconomics Annual* 37.

Chavleishvili, S. and Kremer, M. (2023). Measuring systemic financial stress
and its risks for growth. ECB Working Paper 2842.

Jordà, Ò. (2005). Estimation and inference of impulse responses by local
projections. *American Economic Review* 95(1), 161-182.

Miranda-Agrippino, S. and Rey, H. (2020). U.S. monetary policy and the global
financial cycle. *Review of Economic Studies* 87(6), 2754-2776.

Newey, W. K. and West, K. D. (1987). A simple, positive semi-definite,
heteroskedasticity and autocorrelation consistent covariance matrix.
*Econometrica* 55(3), 703-708.
