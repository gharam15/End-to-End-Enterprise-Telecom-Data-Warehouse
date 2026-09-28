-- CREATE SCHEMA staging FOR STAGINH LAYER
CREATE SCHEMA IF NOT EXISTS staging;


-- CREATE TABLE staging.network_cells
CREATE TABLE IF NOT EXISTS staging.network_cells (

    id BIGSERIAL PRIMARY KEY,

    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,

    mcc INTEGER,
    mnc INTEGER,
    lac INTEGER,
    cellid BIGINT,

    average_signal_strength DOUBLE PRECISION,

    range INTEGER,
    samples INTEGER,
    changeable INTEGER,

    radio VARCHAR(20),

    rnc INTEGER,
    cid BIGINT,
    tac INTEGER,
    sid INTEGER,
    nid INTEGER,
    bid INTEGER,

    ingestion_timestamp TIMESTAMPTZ
);
 DROP TABLE staging.network_cells
 
-- CHECK TABLE LOAD
SELECT *
FROM staging.network_cells;


SELECT COUNT(*)
FROM staging.network_cells;







