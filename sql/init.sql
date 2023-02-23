-- TimeScaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

--  Create Postgree table
CREATE TABLE IF NOT EXISTS process_data (
    timestamp TIMESTAMP NOT NULL,
    tagname TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    quality TEXT NOT NULL
);

--  Convert table to TimeScaleDB
SELECT create_hypertable('process_data', 'timestamp');

--  Set Index
CREATE INDEX ix_symbol_time ON process_data (tagname, timestamp DESC);

--  Time bucket
SELECT time_bucket('15 minutes', timestamp) AS fifteen_min,
    tagname,
    COUNT(*)
  FROM process_data
  WHERE timestamp > NOW() - INTERVAL '3 hours'
  GROUP BY fifteen_min, tagname
  ORDER BY fifteen_min DESC;

-- Continuous Aggregates (Materialized view & policy)
CREATE MATERIALIZED VIEW process_summary_hourly
WITH (timescaledb.continuous) AS
SELECT tagname,
   time_bucket(INTERVAL '1 hour', timestamp) AS bucket,
   AVG(value),
   MAX(value),
   MIN(value)
FROM process_data
GROUP BY tagname, bucket;

SELECT add_continuous_aggregate_policy('process_summary_hourly',
  start_offset => INTERVAL '3 hours',
  end_offset => INTERVAL '1 hour',
  schedule_interval => INTERVAL '1 hour');

-- Compression
ALTER TABLE process_data SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'tagname'
);

-- Compression policy
SELECT add_compression_policy('process_data', INTERVAL '6 hours');

-- --  Add retention policy
SELECT add_retention_policy('process_data', INTERVAL '1 hour');