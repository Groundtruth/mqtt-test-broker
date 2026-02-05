# MQTT Test Broker for Chirpstack Simulation

This project provides a complete test environment for simulating Chirpstack MQTT messages. It includes a PostgreSQL database with test data, an MQTT broker (Mosquitto), and a Python publisher application that reads data from the database and publishes it in Chirpstack format.

## Architecture

The system consists of three Docker containers:

1. **Mosquitto MQTT Broker** - Eclipse Mosquitto MQTT broker on port 1883
2. **PostgreSQL Database** - Stores sensor data with test records
3. **Publisher Application** - Python app that reads from the database and publishes to MQTT

## Features

- **Chirpstack-compatible message format** - Messages follow the Chirpstack application server format
- **Continuous publishing** - Automatically cycles through test data and republishes
- **Configurable interval** - Adjust publishing frequency via environment variables
- **20 pre-loaded test records** - Various sensor types (temperature, pressure, motion, etc.)
- **Easy to extend** - Add more test data by inserting into the PostgreSQL table

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 1.29 or higher)

## Project Structure

```
mqtt-test-broker/
├── docker-compose.yml          # Main orchestration file
├── config/
│   └── mosquitto.conf          # MQTT broker configuration
├── database/
│   └── init.sql                # Database schema and test data
├── publisher/
│   ├── Dockerfile              # Publisher container image
│   ├── publisher.py            # Main publisher application
│   └── requirements.txt        # Python dependencies
└── README.md                   # This file
```

## Quick Start

### 1. Start the System

Navigate to the project directory and start all services:

```bash
cd mqtt-test-broker
docker-compose up -d
```

This will:
- Start the Mosquitto MQTT broker on port 1883
- Start PostgreSQL database on port 5432
- Initialize the database with test data
- Start the publisher application

### 2. View Logs

Check that everything is running correctly:

```bash
# View all logs
docker-compose logs -f

# View publisher logs only
docker-compose logs -f publisher

# View MQTT broker logs
docker-compose logs -f mosquitto
```

### 3. Subscribe to MQTT Messages

To see the published messages, subscribe to the MQTT broker:

```bash
# Subscribe to all application messages
docker run -it --rm --network mqtt-test-broker_mqtt-network eclipse-mosquitto mosquitto_sub -h mosquitto -t "application/#" -v

# Or if you have mosquitto_sub installed locally
mosquitto_sub -h localhost -p 1883 -t "application/#" -v
```

### 4. Test with Your Application

Your application can connect to the MQTT broker at:
- **Host**: `localhost`
- **Port**: `1883`
- **Topic pattern**: `application/+/device/+/event/up`

Example topics:
- `application/1/device/0004a30b001e8a5c/event/up`
- `application/2/device/0004a30b001e8a5e/event/up`
- `application/3/device/0004a30b001e8a60/event/up`

## Configuration

### Environment Variables

You can customize the publisher behavior by editing the `docker-compose.yml` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_BROKER` | `mosquitto` | MQTT broker hostname |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `MQTT_TOPIC` | `application/{app_id}/device/{dev_eui}/event/up` | Topic template |
| `DB_HOST` | `postgres` | PostgreSQL hostname |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `mqttdata` | Database name |
| `DB_USER` | `mqttuser` | Database username |
| `DB_PASSWORD` | `mqttpass` | Database password |
| `MESSAGES_PER_SECOND` | `1` | Publishing rate (messages per second) |
| `BATCH_SIZE` | `10` | Number of records to fetch per batch |
| `AUTO_RESET` | `true` | Auto-reset published status when complete |

### Adjust Publishing Rate

To change the publishing rate, modify the `MESSAGES_PER_SECOND` in `docker-compose.yml`:

```yaml
environment:
  MESSAGES_PER_SECOND: 10   # 10 messages per second
  BATCH_SIZE: 50            # Fetch 50 records at a time
  AUTO_RESET: true          # Continuously cycle through data
```

**Examples**:

```yaml
# Low rate - 1 message every 5 seconds
MESSAGES_PER_SECOND: 0.2

# Medium rate - 10 messages per second
MESSAGES_PER_SECOND: 10

# High rate - 100 messages per second
MESSAGES_PER_SECOND: 100
BATCH_SIZE: 200
```

Then restart the publisher:

```bash
docker-compose restart publisher
```

For detailed configuration options, see [CONFIGURATION.md](CONFIGURATION.md).

## Message Format

Messages are published in Chirpstack format. Example:

```json
{
  "applicationID": "1",
  "applicationName": "app-1",
  "deviceName": "temperature-sensor-01",
  "devEUI": "0004a30b001e8a5c",
  "rxInfo": [
    {
      "gatewayID": "0000000000000001",
      "uplinkID": "uplink-1",
      "name": "test-gateway",
      "rssi": -85,
      "loRaSNR": 7.5,
      "location": {
        "latitude": 0,
        "longitude": 0,
        "altitude": 0
      }
    }
  ],
  "txInfo": {
    "frequency": 868100000,
    "dr": 5
  },
  "adr": true,
  "fCnt": 1,
  "fPort": 10,
  "data": {
    "temperature": 22.5,
    "humidity": 65.2,
    "battery": 3.6
  },
  "object": {
    "temperature": 22.5,
    "humidity": 65.2,
    "battery": 3.6
  },
  "tags": {},
  "confirmedUplink": false,
  "devAddr": "00000000",
  "publishedAt": "2026-02-05T12:00:00"
}
```

## Database Management

### Connect to PostgreSQL

```bash
docker exec -it mqtt-postgres psql -U mqttuser -d mqttdata
```

### View Test Data

```sql
-- View all sensor data
SELECT * FROM sensor_data;

-- View unpublished data
SELECT * FROM sensor_data WHERE published = FALSE;

-- View data by device
SELECT * FROM sensor_data WHERE device_eui = '0004a30b001e8a5c';
```

### Add More Test Data

```sql
INSERT INTO sensor_data (device_eui, application_id, device_name, f_port, f_cnt, data, rssi, snr) 
VALUES (
    '0004a30b001e9999',
    1,
    'new-sensor',
    10,
    1,
    '{"temperature": 25.0, "humidity": 60.0, "battery": 3.7}'::jsonb,
    -80,
    8.0
);
```

### Reset Published Status

To manually reset all records to unpublished (the publisher does this automatically):

```sql
SELECT reset_published_status();
```

## Troubleshooting

### Publisher Not Connecting to MQTT

Check if the MQTT broker is running:

```bash
docker-compose ps mosquitto
```

View MQTT broker logs:

```bash
docker-compose logs mosquitto
```

### Publisher Not Connecting to Database

Check if PostgreSQL is running:

```bash
docker-compose ps postgres
```

View database logs:

```bash
docker-compose logs postgres
```

### No Messages Being Published

1. Check publisher logs:
   ```bash
   docker-compose logs -f publisher
   ```

2. Verify there's unpublished data:
   ```bash
   docker exec -it mqtt-postgres psql -U mqttuser -d mqttdata -c "SELECT COUNT(*) FROM sensor_data WHERE published = FALSE;"
   ```

3. Restart the publisher:
   ```bash
   docker-compose restart publisher
   ```

## Stopping the System

### Stop all services

```bash
docker-compose down
```

### Stop and remove all data

```bash
docker-compose down -v
```

This will remove the PostgreSQL data volume, and you'll start fresh next time.

## Testing Your Application

### Example: Python MQTT Subscriber

Create a simple test subscriber to verify messages:

```python
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("application/+/device/+/event/up")

def on_message(client, userdata, msg):
    print(f"\nTopic: {msg.topic}")
    payload = json.loads(msg.payload.decode())
    print(f"Device: {payload['deviceName']}")
    print(f"Data: {json.dumps(payload['data'], indent=2)}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()
```

### Example: Node.js MQTT Subscriber

```javascript
const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://localhost:1883');

client.on('connect', () => {
    console.log('Connected to MQTT broker');
    client.subscribe('application/+/device/+/event/up', (err) => {
        if (!err) {
            console.log('Subscribed to topic');
        }
    });
});

client.on('message', (topic, message) => {
    const payload = JSON.parse(message.toString());
    console.log(`\nTopic: ${topic}`);
    console.log(`Device: ${payload.deviceName}`);
    console.log(`Data:`, payload.data);
});
```

## Advanced Usage

### Custom MQTT Topics

To change the topic structure, modify the `MQTT_TOPIC` environment variable in `docker-compose.yml`:

```yaml
environment:
  MQTT_TOPIC: "custom/topic/{dev_eui}/data"
```

### WebSocket Support

The MQTT broker also supports WebSocket connections on port 9001:

```javascript
const client = mqtt.connect('ws://localhost:9001');
```

### External Access

To access the MQTT broker from outside your local machine, you may need to:

1. Update the `mosquitto.conf` to bind to all interfaces
2. Configure your firewall to allow port 1883
3. Use your machine's IP address instead of `localhost`

## License

This is a test/development tool. Use it freely for testing and development purposes.

## Support

For issues or questions about this test broker setup, please refer to the documentation or create an issue in your project repository.
