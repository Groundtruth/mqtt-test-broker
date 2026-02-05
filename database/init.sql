-- Create the sensor_data table to store test data
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    device_eui VARCHAR(16) NOT NULL,
    application_id INTEGER NOT NULL,
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
INSERT INTO sensor_data (device_eui, application_id, device_name, f_port, f_cnt, data, rssi, snr) VALUES
    ('0004a30b001e8a5c', 1, 'temperature-sensor-01', 10, 1, '{"temperature": 22.5, "humidity": 65.2, "battery": 3.6}'::jsonb, -85, 7.5),
    ('0004a30b001e8a5d', 1, 'temperature-sensor-02', 10, 1, '{"temperature": 23.1, "humidity": 62.8, "battery": 3.7}'::jsonb, -82, 8.2),
    ('0004a30b001e8a5e', 2, 'pressure-sensor-01', 11, 1, '{"pressure": 1013.25, "temperature": 21.8, "battery": 3.5}'::jsonb, -88, 6.9),
    ('0004a30b001e8a5f', 2, 'motion-sensor-01', 12, 1, '{"motion": true, "battery": 3.8}'::jsonb, -79, 9.1),
    ('0004a30b001e8a60', 3, 'water-level-sensor', 13, 1, '{"level": 145.6, "temperature": 18.3, "battery": 3.4}'::jsonb, -91, 5.8),
    ('0004a30b001e8a61', 1, 'temperature-sensor-03', 10, 2, '{"temperature": 24.3, "humidity": 58.5, "battery": 3.6}'::jsonb, -84, 7.8),
    ('0004a30b001e8a62', 3, 'air-quality-sensor', 14, 1, '{"pm25": 12.5, "pm10": 18.3, "co2": 450, "battery": 3.7}'::jsonb, -86, 7.2),
    ('0004a30b001e8a63', 2, 'door-sensor-01', 15, 1, '{"open": false, "battery": 3.9}'::jsonb, -80, 8.8),
    ('0004a30b001e8a64', 1, 'temperature-sensor-04', 10, 1, '{"temperature": 21.9, "humidity": 67.1, "battery": 3.5}'::jsonb, -87, 6.5),
    ('0004a30b001e8a65', 3, 'light-sensor-01', 16, 1, '{"lux": 350, "battery": 3.8}'::jsonb, -83, 8.0),
    ('0004a30b001e8a5c', 1, 'temperature-sensor-01', 10, 2, '{"temperature": 22.8, "humidity": 64.9, "battery": 3.6}'::jsonb, -86, 7.3),
    ('0004a30b001e8a5d', 1, 'temperature-sensor-02', 10, 2, '{"temperature": 23.4, "humidity": 62.1, "battery": 3.7}'::jsonb, -81, 8.5),
    ('0004a30b001e8a5e', 2, 'pressure-sensor-01', 11, 2, '{"pressure": 1013.50, "temperature": 22.0, "battery": 3.5}'::jsonb, -89, 6.7),
    ('0004a30b001e8a5f', 2, 'motion-sensor-01', 12, 2, '{"motion": false, "battery": 3.8}'::jsonb, -78, 9.3),
    ('0004a30b001e8a60', 3, 'water-level-sensor', 13, 2, '{"level": 146.2, "temperature": 18.5, "battery": 3.4}'::jsonb, -92, 5.6),
    ('0004a30b001e8a61', 1, 'temperature-sensor-03', 10, 3, '{"temperature": 24.6, "humidity": 57.8, "battery": 3.6}'::jsonb, -85, 7.6),
    ('0004a30b001e8a62', 3, 'air-quality-sensor', 14, 2, '{"pm25": 13.1, "pm10": 19.0, "co2": 465, "battery": 3.7}'::jsonb, -87, 7.0),
    ('0004a30b001e8a63', 2, 'door-sensor-01', 15, 2, '{"open": true, "battery": 3.9}'::jsonb, -79, 9.0),
    ('0004a30b001e8a64', 1, 'temperature-sensor-04', 10, 2, '{"temperature": 22.2, "humidity": 66.5, "battery": 3.5}'::jsonb, -88, 6.3),
    ('0004a30b001e8a65', 3, 'light-sensor-01', 16, 2, '{"lux": 420, "battery": 3.8}'::jsonb, -82, 8.2);

-- Function to reset published status (useful for testing)
CREATE OR REPLACE FUNCTION reset_published_status()
RETURNS void AS $$
BEGIN
    UPDATE sensor_data SET published = FALSE;
END;
$$ LANGUAGE plpgsql;
