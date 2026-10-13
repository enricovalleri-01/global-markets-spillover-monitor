-- For every FOMC announcement and every series, the change in the series from
-- the last observation BEFORE the announcement day to the first one AFTER it.
--
-- Why the announcement day itself is skipped: most announcements are at 2:00
-- or 2:15 pm in New York, in the European evening, after that day's European
-- values were recorded. A few are in the New York morning, before them. A
-- window from the day before to the day after contains the reaction in both
-- cases. The price is a wider window: the change is a cumulative daily
-- response, not an intraday reaction, and it also contains other news.

CREATE OR REPLACE VIEW event_windows AS
WITH windows AS (
    SELECT
        a.date    AS announcement_date,
        a.time_et,
        s.series,
        s.change_type,
        (SELECT max(o.date) FROM observations o
          WHERE o.series = s.series AND o.date < a.date) AS date_before,
        (SELECT min(o.date) FROM observations o
          WHERE o.series = s.series AND o.date > a.date) AS date_after
    FROM fomc_announcements a
    CROSS JOIN series s
)
SELECT
    w.announcement_date,
    w.time_et,
    w.series,
    w.date_before,
    w.date_after,
    w.date_after - w.date_before AS window_days,
    b.value AS value_before,
    f.value AS value_after,
    CASE w.change_type
        WHEN 'diff_bp' THEN (f.value - b.value) * 100
        WHEN 'log_pct' THEN 100 * ln(f.value / b.value)
        ELSE f.value - b.value
    END AS change,
    -- TRUE if an ECB Governing Council meeting falls, by date, after the last
    -- observation before the announcement and up to the first one after it.
    -- It is a calendar match for this one-observation window only, and the
    -- meeting dates start in March 1999. Longer horizons are flagged in
    -- src/models/local_projections.py.
    EXISTS (
        SELECT 1 FROM ecb_meetings m
        WHERE m.date > w.date_before AND m.date <= w.date_after
    ) AS ecb_meeting_in_h1_window
FROM windows w
JOIN observations b ON b.series = w.series AND b.date = w.date_before
JOIN observations f ON f.series = w.series AND f.date = w.date_after;
