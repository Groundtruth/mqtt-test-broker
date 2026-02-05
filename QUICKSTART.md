# Quick Start Guide

Get your MQTT test broker running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Ports 1883 (MQTT) and 5432 (PostgreSQL) available

## Installation

### 1. Extract the Project

```bash
tar -xzf mqtt-test-broker.tar.gz
cd mqtt-test-broker
```

### 2. Start the System

```bash
docker-compose up -d
```

This starts:
- **Mosquitto MQTT Broker** on port 1883
- **PostgreSQL Database** with 20 test records
- **Publisher Application** that publishes messages every 5 seconds

### 3. Verify It's Running

```bash
docker-compose ps
```

You should see all three containers running.

### 4. View Messages

**Option A: Using Docker**
```bash
docker run -it --rm --network mqtt-test-broker_mqtt-network eclipse-mosquitto mosquitto_sub -h mosquitto -t "application/#" -v
```

**Option B: Using Local Mosquitto Client**
```bash
mosquitto_sub -h localhost -p 1883 -t "application/#" -v
```

**Option C: Using Python Test Subscriber**
```bash
# Install paho-mqtt if not already installed
pip3 install paho-mqtt

# Run the test subscriber
python3 test_subscriber.py
```

## What You'll See

Messages published every 5 seconds in Chirpstack format:

```
application/1/device/0004a30b001e8a5c/event/up
{
  "applicationID": "1",
  "deviceName": "temperature-sensor-01",
  "devEUI": "0004a30b001e8a5c",
  "data": {
    "temperature": 22.5,
    "humidity": 65.2,
    "battery": 3.6
  },
  ...
}
```

## Test Your Application

Point your application to:
- **MQTT Broker**: `localhost:1883`
- **Topic Pattern**: `application/+/device/+/event/up`

## Configuration

To change the publishing interval, edit `docker-compose.yml`:

```yaml
environment:
  PUBLISH_INTERVAL: 2  # Change to 2 seconds
```

Then restart:
```bash
docker-compose restart publisher
```

## Stop the System

```bash
docker-compose down
```

## Troubleshooting

**No messages appearing?**
```bash
# Check publisher logs
docker-compose logs -f publisher

# Restart publisher
docker-compose restart publisher
```

**Port already in use?**
```bash
# Check what's using the port
sudo lsof -i :1883
sudo lsof -i :5432

# Stop conflicting services or change ports in docker-compose.yml
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Add more test data to the database
- Customize message format in `publisher/publisher.py`
- Integrate with your application

## Support

For detailed information, see the main README.md file.
