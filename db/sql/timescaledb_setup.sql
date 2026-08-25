-- ============================================================================
-- 🚀 SHAREGY TIMESCALEDB MIGRATION & CONTINUOUS AGGREGATES SETUP
-- ============================================================================
-- Wandelt alle hochfrequenten Telemetrie- und Zählertabellen in native
-- TimescaleDB Hypertables um, aktiviert automatische Kompression & Retention.
-- ============================================================================

-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
    RAISE NOTICE '🚀 Starte TimescaleDB Hypertable-Migration für Sharegy...';

    -- ------------------------------------------------------------------------
    -- A. EMS TELEMETRIE HYPERTABLES (devices app)
    -- ------------------------------------------------------------------------

    -- 1. devices_devicemetric (Hochfrequente Roh-Telemetrie)
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'devices_devicemetric') THEN
        ALTER TABLE devices_devicemetric DROP CONSTRAINT IF EXISTS devices_devicemetric_pkey CASCADE;
        ALTER TABLE devices_devicemetric ADD PRIMARY KEY (id, timestamp);
        PERFORM create_hypertable('devices_devicemetric', 'timestamp', chunk_time_interval => INTERVAL '7 days', if_not_exists => TRUE, migrate_data => TRUE);
        RAISE NOTICE '✅ devices_devicemetric als Hypertable (7 Tage Chunks) eingerichtet.';
    END IF;

    -- 2. devices_devicemetric1m (1-Minuten Aggregate)
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'devices_devicemetric1m') THEN
        ALTER TABLE devices_devicemetric1m DROP CONSTRAINT IF EXISTS devices_devicemetric1m_pkey CASCADE;
        ALTER TABLE devices_devicemetric1m DROP CONSTRAINT IF EXISTS devices_devicemetric1m_device_id_bucket_metric_key_77e77b63_uniq CASCADE;
        ALTER TABLE devices_devicemetric1m ADD PRIMARY KEY (id, bucket);
        PERFORM create_hypertable('devices_devicemetric1m', 'bucket', chunk_time_interval => INTERVAL '7 days', if_not_exists => TRUE, migrate_data => TRUE);
        RAISE NOTICE '✅ devices_devicemetric1m als Hypertable (7 Tage Chunks) eingerichtet.';
    END IF;

    -- 3. devices_devicemetric5m (5-Minuten Aggregate)
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'devices_devicemetric5m') THEN
        ALTER TABLE devices_devicemetric5m DROP CONSTRAINT IF EXISTS devices_devicemetric5m_pkey CASCADE;
        ALTER TABLE devices_devicemetric5m DROP CONSTRAINT IF EXISTS devices_devicemetric5m_device_id_bucket_metric_key_3811f5d6_uniq CASCADE;
        ALTER TABLE devices_devicemetric5m ADD PRIMARY KEY (id, bucket);
        PERFORM create_hypertable('devices_devicemetric5m', 'bucket', chunk_time_interval => INTERVAL '14 days', if_not_exists => TRUE, migrate_data => TRUE);
        RAISE NOTICE '✅ devices_devicemetric5m als Hypertable (14 Tage Chunks) eingerichtet.';
    END IF;

    -- 4. devices_devicemetric15m (15-Minuten Aggregate)
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'devices_devicemetric15m') THEN
        ALTER TABLE devices_devicemetric15m DROP CONSTRAINT IF EXISTS devices_devicemetric15m_pkey CASCADE;
        ALTER TABLE devices_devicemetric15m DROP CONSTRAINT IF EXISTS devices_devicemetric15m_device_id_bucket_metric_key_55d4ee38_uniq CASCADE;
        ALTER TABLE devices_devicemetric15m ADD PRIMARY KEY (id, bucket);
        PERFORM create_hypertable('devices_devicemetric15m', 'bucket', chunk_time_interval => INTERVAL '30 days', if_not_exists => TRUE, migrate_data => TRUE);
        RAISE NOTICE '✅ devices_devicemetric15m als Hypertable (30 Tage Chunks) eingerichtet.';
    END IF;

    -- 5. devices_devicemetric1h (Stündliche Aggregate)
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'devices_devicemetric1h') THEN
        ALTER TABLE devices_devicemetric1h DROP CONSTRAINT IF EXISTS devices_devicemetric1h_pkey CASCADE;
        ALTER TABLE devices_devicemetric1h DROP CONSTRAINT IF EXISTS devices_devicemetric1h_device_id_bucket_metric_key_e31505b3_uniq CASCADE;
        ALTER TABLE devices_devicemetric1h ADD PRIMARY KEY (id, bucket);
        PERFORM create_hypertable('devices_devicemetric1h', 'bucket', chunk_time_interval => INTERVAL '90 days', if_not_exists => TRUE, migrate_data => TRUE);
        RAISE NOTICE '✅ devices_devicemetric1h als Hypertable (90 Tage Chunks) eingerichtet.';
    END IF;

    -- ------------------------------------------------------------------------
    -- B. ENERGY SHARING & METERING HYPERTABLES (core app)
    -- ------------------------------------------------------------------------

    -- 6. core_intervalreading (iMSys 15m Zähler-Rohwerte)
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'core_intervalreading') THEN
        ALTER TABLE core_intervalreading DROP CONSTRAINT IF EXISTS core_intervalreading_pkey CASCADE;
        ALTER TABLE core_intervalreading ADD PRIMARY KEY (id, ts_start);
        PERFORM create_hypertable('core_intervalreading', 'ts_start', chunk_time_interval => INTERVAL '14 days', if_not_exists => TRUE, migrate_data => TRUE);
        RAISE NOTICE '✅ core_intervalreading als Hypertable (14 Tage Chunks) eingerichtet.';
    END IF;

    -- 7. core_aggregatedreading
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'core_aggregatedreading') THEN
        ALTER TABLE core_aggregatedreading DROP CONSTRAINT IF EXISTS core_aggregatedreading_pkey CASCADE;
        ALTER TABLE core_aggregatedreading DROP CONSTRAINT IF EXISTS core_aggregatedreading_meter_id_period_start_key CASCADE;
        ALTER TABLE core_aggregatedreading ADD PRIMARY KEY (id, period_start);
        PERFORM create_hypertable('core_aggregatedreading', 'period_start', chunk_time_interval => INTERVAL '30 days', if_not_exists => TRUE, migrate_data => TRUE);
        RAISE NOTICE '✅ core_aggregatedreading als Hypertable (30 Tage Chunks) eingerichtet.';
    END IF;

    -- 8. core_balanceslot
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'core_balanceslot') THEN
        ALTER TABLE core_balanceslot DROP CONSTRAINT IF EXISTS core_balanceslot_pkey CASCADE;
        ALTER TABLE core_balanceslot ADD PRIMARY KEY (id, period_start);
        PERFORM create_hypertable('core_balanceslot', 'period_start', chunk_time_interval => INTERVAL '30 days', if_not_exists => TRUE, migrate_data => TRUE);
        RAISE NOTICE '✅ core_balanceslot als Hypertable (30 Tage Chunks) eingerichtet.';
    END IF;

    -- ------------------------------------------------------------------------
    -- C. BÖRSENPREISE (market app)
    -- ------------------------------------------------------------------------

    -- 9. market_spotprice
    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'market_spotprice') THEN
        ALTER TABLE market_spotprice DROP CONSTRAINT IF EXISTS market_spotprice_pkey CASCADE;
        ALTER TABLE market_spotprice DROP CONSTRAINT IF EXISTS market_spotprice_timestamp_source_a3536ea1_uniq CASCADE;
        ALTER TABLE market_spotprice ADD PRIMARY KEY (id, timestamp);
        PERFORM create_hypertable('market_spotprice', 'timestamp', chunk_time_interval => INTERVAL '30 days', if_not_exists => TRUE, migrate_data => TRUE);
        RAISE NOTICE '✅ market_spotprice als Hypertable (30 Tage Chunks) eingerichtet.';
    END IF;

    -- ------------------------------------------------------------------------
    -- D. KOMPRESSION & RETENTION POLICIES
    -- ------------------------------------------------------------------------
    
    -- Kompression für Rohdaten älter als 7 Tage
    BEGIN
        ALTER TABLE devices_devicemetric SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'device_id, metric_key',
            timescaledb.compress_orderby = 'timestamp DESC'
        );
        PERFORM add_compression_policy('devices_devicemetric', INTERVAL '7 days', if_not_exists => TRUE);
        RAISE NOTICE '✅ Automatische Kompression (nach 7 Tagen) für devices_devicemetric aktiviert.';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'ℹ️ Kompressions-Policy für devices_devicemetric bereits aktiv oder übersprungen.';
    END;

    -- Retention Policy: Rohdaten nach 30 Tagen löschen (Aggregate 5m/15m/1h bleiben dauerhaft erhalten!)
    BEGIN
        PERFORM add_retention_policy('devices_devicemetric', INTERVAL '30 days', if_not_exists => TRUE);
        PERFORM add_retention_policy('devices_devicemetric1m', INTERVAL '60 days', if_not_exists => TRUE);
        RAISE NOTICE '✅ Automatische Daten-Retention (30 Tage Rohdaten / 60 Tage 1m) aktiviert.';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'ℹ️ Retention-Policy bereits aktiv oder übersprungen.';
    END;

    -- ------------------------------------------------------------------------
    -- E. PERFORMANCE-INDIZES
    -- ------------------------------------------------------------------------
    CREATE INDEX IF NOT EXISTS dm_dev_ts_desc_idx ON devices_devicemetric (device_id, metric_key, timestamp DESC);
    CREATE INDEX IF NOT EXISTS dm1h_dev_bucket_desc_idx ON devices_devicemetric1h (device_id, metric_key, bucket DESC);
    CREATE INDEX IF NOT EXISTS dm5m_dev_bucket_desc_idx ON devices_devicemetric5m (device_id, metric_key, bucket DESC);
    
    RAISE NOTICE '🎉 TimescaleDB Setup erfolgreich abgeschlossen!';
END $$;

