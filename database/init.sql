-- Create the sensor_data table to store test data
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    device_eui VARCHAR(16) NOT NULL,
    application_id UUID DEFAULT gen_random_uuid(),
    device_name VARCHAR(100),
    f_port INTEGER,
    f_cnt INTEGER,
    data JSONB NOT NULL,
    rssi INTEGER,
    snr FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published BOOLEAN DEFAULT FALSE
);

-- Create index for efficient querying
CREATE INDEX idx_published ON sensor_data(published);
CREATE INDEX idx_device_eui ON sensor_data(device_eui);
CREATE INDEX idx_timestamp ON sensor_data(timestamp);

-- Insert sample test data simulating Chirpstack device messages
INSERT INTO sensor_data (device_eui, device_name, f_port, f_cnt, data, rssi, snr) VALUES
    ('0004a30b001e8a5c', 'temperature-sensor-01', 1, 1, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -85, 7.5),
    ('0004a30b001e8a5d', 'temperature-sensor-02', 1, 1, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -82, 8.2),
    ('0004a30b001e8a5e', 'pressure-sensor-01', 1, 1, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -88, 6.9),
    ('0004a30b001e8a5f', 'motion-sensor-01', 1, 1, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -79, 9.1),
    ('0004a30b001e8a60', 'water-level-sensor', 1, 1, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -91, 5.8),
    ('0004a30b001e8a61', 'temperature-sensor-03', 1, 2, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -84, 7.8),
    ('0004a30b001e8a62', 'air-quality-sensor', 1, 1, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -86, 7.2),
    ('0004a30b001e8a63', 'door-sensor-01', 1, 1, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -80, 8.8),
    ('0004a30b001e8a64', 'temperature-sensor-04', 1, 1, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -87, 6.5),
    ('0004a30b001e8a65', 'light-sensor-01', 1, 1, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -83, 8.0),
    ('0004a30b001e8a5c', 'temperature-sensor-01', 1, 2, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -86, 7.3),
    ('0004a30b001e8a5d', 'temperature-sensor-02', 1, 2, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -81, 8.5),
    ('0004a30b001e8a5e', 'pressure-sensor-01', 1, 2, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -89, 6.7),
    ('0004a30b001e8a5f', 'motion-sensor-01', 1, 2, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -78, 9.3),
    ('0004a30b001e8a60', 'water-level-sensor', 1, 2, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -92, 5.6),
    ('0004a30b001e8a61', 'temperature-sensor-03', 1, 3, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -85, 7.6),
    ('0004a30b001e8a62', 'air-quality-sensor', 1, 2, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -87, 7.0),
    ('0004a30b001e8a63', 'door-sensor-01', 1, 2, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -79, 9.0),
    ('0004a30b001e8a64', 'temperature-sensor-04', 1, 2, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -88, 6.3),
    ('0004a30b001e8a65', 'light-sensor-01', 1, 2, '{"event": "Heartbeat", "status": "Sprung", "battery": 42 }'::jsonb, -82, 8.2);

-- Function to reset published status (useful for testing)
CREATE OR REPLACE FUNCTION reset_published_status()
RETURNS void AS $$
BEGIN
    UPDATE sensor_data SET published = FALSE;
END;
$$ LANGUAGE plpgsql;
