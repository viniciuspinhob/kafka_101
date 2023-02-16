
--  Create Postgree table
CREATE TABLE IF NOT EXISTS process_data (
    timestamp TEXT NOT NULL,
    tagname TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    quality TEXT NOT NULL
);

--  Convert table to TimeScaleDB
-- SELECT create_hypertable('process_data', 'timestamp');

-- Set index to ID
-- CREATE INDEX ON process_data (tmstp DESC, id)
--     WHERE id IS NOT NULL;




-- Criar um atable apor TAG pver vom breno