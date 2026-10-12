-- Three tables. Everything else in the project is computed from these.

-- One row per series: what it is and where it comes from.
CREATE TABLE series (
    series       VARCHAR PRIMARY KEY,
    description  VARCHAR NOT NULL,
    unit         VARCHAR NOT NULL,
    source       VARCHAR NOT NULL,
    source_code  VARCHAR NOT NULL,
    -- how a change over a window is measured:
    --   diff_bp  = difference of a rate in percent, times 100 (basis points)
    --   log_pct  = 100 * log(after / before) (percent)
    --   diff     = plain difference (index points)
    change_type  VARCHAR NOT NULL
);

-- One row per series and day ("long" format). Days without a value are absent.
CREATE TABLE observations (
    series  VARCHAR NOT NULL REFERENCES series (series),
    date    DATE    NOT NULL,
    value   DOUBLE  NOT NULL,
    PRIMARY KEY (series, date)
);

-- One row per FOMC announcement, with the Bauer-Swanson surprises in basis points.
CREATE TABLE fomc_announcements (
    date           DATE    NOT NULL,
    time_et        VARCHAR NOT NULL,   -- announcement time, US Eastern time
    unscheduled    BOOLEAN NOT NULL,
    mps_bp         DOUBLE,             -- raw surprise
    mps_orth_bp    DOUBLE,             -- orthogonalised surprise (missing in 2020)
    us10y_30min_bp DOUBLE,             -- 10-year Treasury yield response in the 30-minute window
    PRIMARY KEY (date, time_et)
);

-- One row per ECB Governing Council monetary policy meeting (from March 1999).
CREATE TABLE ecb_meetings (
    date           DATE PRIMARY KEY,
    dfr_change_bp  DOUBLE NOT NULL     -- change in the deposit facility rate decided that day
);
