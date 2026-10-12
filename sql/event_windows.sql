-- For every FOMC announcement and every series, the change in the series from
-- the last observation BEFORE the announcement day to the first one AFTER it.
--
-- Why not the announcement day itself: most announcements are at 2:00 or 2:15 pm
-- in New York, around 8 pm in Frankfurt. European markets are closed and the
-- ECB reference exchange rate was fixed at 2:15 pm CET, so the value recorded on
-- the announcement day was observed before the announcement.

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
    -- TRUE if an ECB Governing Council meeting falls inside the window: after
    -- the last observation before the announcement, up to the first one after.
    -- In that case the change also contains the reaction to the ECB decision.
    EXISTS (
        SELECT 1 FROM ecb_meetings m
        WHERE m.date > w.date_before AND m.date <= w.date_after
    ) AS ecb_meeting_in_window
FROM windows w
JOIN observations b ON b.series = w.series AND b.date = w.date_before
JOIN observations f ON f.series = w.series AND f.date = w.date_after;
