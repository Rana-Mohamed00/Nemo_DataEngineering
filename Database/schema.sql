
CREATE TABLE IF NOT EXISTS cleansed_telemetry (
    date TIMESTAMP,
    rpm DOUBLE PRECISION,
    speed DOUBLE PRECISION,
    ngear INTEGER,
    throttle DOUBLE PRECISION,
    brake BOOLEAN,
    drs INTEGER,
    source TEXT,
    time INTERVAL,
    session_time INTERVAL,
    driver INTEGER
);

CREATE TABLE IF NOT EXISTS dead_letter (
    raw_line TEXT,
    error_reason TEXT
);

