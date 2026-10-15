-- One row per series: the latest value, its change over one week, one month and
-- one year, and where the latest level stands in its history since 1999.
--
-- Changes use the last observation on or before the earlier date, so weekends
-- and holidays never leave a gap. The US-German 10-year spread is computed here
-- on the days when both yields are observed.

WITH obs AS (
    SELECT series, date, value FROM observations
    UNION ALL
    SELECT 'us_bund_spread', u.date, u.value - b.value
    FROM observations u
    JOIN observations b ON b.date = u.date AND b.series = 'bund_10y'
    WHERE u.series = 'us_10y'
),
types AS (
    SELECT series, change_type FROM series
    UNION ALL
    SELECT 'us_bund_spread', 'diff_bp'
),
latest AS (
    SELECT series, max(date) AS last_date FROM obs GROUP BY series
),
points AS (
    SELECT
        l.series,
        l.last_date,
        (SELECT value FROM obs o WHERE o.series = l.series AND o.date = l.last_date) AS last_value,
        (SELECT value FROM obs o WHERE o.series = l.series AND o.date <= l.last_date - INTERVAL 7 DAY
          ORDER BY o.date DESC LIMIT 1) AS value_1w,
        (SELECT value FROM obs o WHERE o.series = l.series AND o.date <= l.last_date - INTERVAL 1 MONTH
          ORDER BY o.date DESC LIMIT 1) AS value_1m,
        (SELECT value FROM obs o WHERE o.series = l.series AND o.date <= l.last_date - INTERVAL 1 YEAR
          ORDER BY o.date DESC LIMIT 1) AS value_1y
    FROM latest l
)
SELECT
    p.series,
    p.last_date,
    p.last_value,
    -- same units as the event study: basis points, percent or index points
    CASE t.change_type WHEN 'diff_bp' THEN (p.last_value - p.value_1w) * 100
                       WHEN 'log_pct' THEN 100 * ln(p.last_value / p.value_1w)
                       ELSE p.last_value - p.value_1w END AS change_1w,
    CASE t.change_type WHEN 'diff_bp' THEN (p.last_value - p.value_1m) * 100
                       WHEN 'log_pct' THEN 100 * ln(p.last_value / p.value_1m)
                       ELSE p.last_value - p.value_1m END AS change_1m,
    CASE t.change_type WHEN 'diff_bp' THEN (p.last_value - p.value_1y) * 100
                       WHEN 'log_pct' THEN 100 * ln(p.last_value / p.value_1y)
                       ELSE p.last_value - p.value_1y END AS change_1y,
    -- share of daily observations since 1999 below the latest value, in percent
    (SELECT 100 * avg(CASE WHEN o.value < p.last_value THEN 1 ELSE 0 END)
       FROM obs o WHERE o.series = p.series AND o.date >= DATE '1999-01-01') AS percentile_since_1999,
    t.change_type
FROM points p
JOIN types t USING (series);
