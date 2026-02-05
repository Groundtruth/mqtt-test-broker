# Configuration Guide

This guide explains all configuration options for the MQTT test broker system.

## Publisher Configuration

### MESSAGES_PER_SECOND

**Description**: Controls the publishing rate (messages per second)

**Type**: Float

**Default**: `1`

**Range**: `0.01` to `100` (or higher, depending on your system)

**Examples**:

```yaml
# Slow rate - 1 message every 5 seconds
MESSAGES_PER_SECOND: 0.2

# Default - 1 message per second
MESSAGES_PER_SECOND: 1

# Medium rate - 10 messages per second
MESSAGES_PER_SECOND: 10

# High rate - 50 messages per second
MESSAGES_PER_SECOND: 50

# Maximum rate - 100 messages per second
MESSAGES_PER_SECOND: 100
```

**Performance Notes**:
- For rates above 50 msg/sec, ensure your MQTT broker can handle the load
- QoS is set to 0 for maximum throughput
- Monitor system resources (CPU, memory, network) at high rates

---

### BATCH_SIZE

**Description**: Number of records to fetch from database in each batch

**Type**: Integer

**Default**: `10`

**Range**: `1` to `1000`

**Recommendations**:
- Low rates (< 5 msg/sec): Use `BATCH_SIZE: 5-10`
- Medium rates (5-50 msg/sec): Use `BATCH_SIZE: 50-100`
- High rates (> 50 msg/sec): Use `BATCH_SIZE: 100-500`

**Examples**:

```yaml
# Small batches for low-rate publishing
BATCH_SIZE: 5

# Medium batches (default)
BATCH_SIZE: 10

# Large batches for high-throughput
BATCH_SIZE: 100
```

**Impact**:
- Larger batches reduce database queries but use more memory
- Smaller batches provide more granular control but increase DB load

---

### AUTO_RESET

**Description**: Automatically reset all records to unpublished when no unpublished data is available

**Type**: Boolean

**Default**: `true`

**Values**: `true` or `false`

**Examples**:

```yaml
# Continuous publishing (recommended for testing)
AUTO_RESET: true

# Publish once and stop
AUTO_RESET: false
```

**Behavior**:
- `true`: Publisher continuously cycles through all test data
- `false`: Publisher stops when all records are published

---

## MQTT Configuration

### MQTT_BROKER

**Description**: Hostname or IP address of the MQTT broker

**Type**: String

**Default**: `mosquitto` (container name)

**Examples**:

```yaml
# Using Docker container name
MQTT_BROKER: mosquitto

# Using localhost (if running outside Docker)
MQTT_BROKER: localhost

# Using external broker
MQTT_BROKER: mqtt.example.com
```

---

### MQTT_PORT

**Description**: Port number for MQTT broker

**Type**: Integer

**Default**: `1883`

**Common Values**:
- `1883`: Standard MQTT port
- `8883`: MQTT over TLS/SSL

---

### MQTT_TOPIC

**Description**: Topic template for publishing messages

**Type**: String (with placeholders)

**Default**: `application/{app_id}/device/{dev_eui}/event/up`

**Placeholders**:
- `{app_id}`: Replaced with `application_id` from database
- `{dev_eui}`: Replaced with `device_eui` from database

**Examples**:

```yaml
# Chirpstack format (default)
MQTT_TOPIC: application/{app_id}/device/{dev_eui}/event/up

# Custom format
MQTT_TOPIC: devices/{dev_eui}/data

# Simplified format
MQTT_TOPIC: sensor/{dev_eui}
```

---

## Database Configuration

### DB_HOST

**Description**: PostgreSQL hostname or IP address

**Type**: String

**Default**: `postgres` (container name)

---

### DB_PORT

**Description**: PostgreSQL port number

**Type**: Integer

**Default**: `5432`

---

### DB_NAME

**Description**: PostgreSQL database name

**Type**: String

**Default**: `mqttdata`

---

### DB_USER

**Description**: PostgreSQL username

**Type**: String

**Default**: `mqttuser`

---

### DB_PASSWORD

**Description**: PostgreSQL password

**Type**: String

**Default**: `mqttpass`

**Security Note**: Change this in production environments!

---

## Configuration Examples

### Example 1: Low Rate Testing (1 message every 5 seconds)

```yaml
environment:
  MESSAGES_PER_SECOND: 0.2
  BATCH_SIZE: 5
  AUTO_RESET: true
```

### Example 2: Medium Rate Testing (10 messages per second)

```yaml
environment:
  MESSAGES_PER_SECOND: 10
  BATCH_SIZE: 50
  AUTO_RESET: true
```

### Example 3: High Throughput Testing (100 messages per second)

```yaml
environment:
  MESSAGES_PER_SECOND: 100
  BATCH_SIZE: 200
  AUTO_RESET: true
```

### Example 4: Burst Testing (50 msg/sec, publish once)

```yaml
environment:
  MESSAGES_PER_SECOND: 50
  BATCH_SIZE: 100
  AUTO_RESET: false
```

---

## How to Apply Configuration Changes

### Method 1: Edit docker-compose.yml

1. Open `docker-compose.yml`
2. Modify the `environment` section under `publisher` service
3. Restart the publisher:

```bash
docker-compose restart publisher
```

### Method 2: Use Environment Variables

1. Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

2. Edit `.env` with your values

3. Update `docker-compose.yml` to use env_file:

```yaml
publisher:
  build: ./publisher
  env_file:
    - .env
```

4. Restart:

```bash
docker-compose down
docker-compose up -d
```

### Method 3: Command Line Override

```bash
docker-compose up -d \
  -e MESSAGES_PER_SECOND=100 \
  -e BATCH_SIZE=200
```

---

## Monitoring Performance

### View Real-Time Logs

```bash
docker-compose logs -f publisher
```

### Check Publishing Statistics

The publisher logs statistics every 30 seconds:

```
INFO - Stats: 3000 messages published, 0 errors, 100.05 msg/sec
```

### Monitor System Resources

```bash
# CPU and memory usage
docker stats mqtt-publisher

# Network traffic
docker stats --no-stream mqtt-publisher
```

---

## Troubleshooting

### Publisher Can't Keep Up with Target Rate

**Symptoms**: Actual rate is lower than configured rate

**Solutions**:
1. Increase `BATCH_SIZE` to reduce database queries
2. Check database performance
3. Check MQTT broker capacity
4. Reduce `MESSAGES_PER_SECOND` to a sustainable rate

### High CPU Usage

**Causes**:
- Very high publishing rate
- Small batch size causing frequent DB queries

**Solutions**:
1. Increase `BATCH_SIZE`
2. Reduce `MESSAGES_PER_SECOND`
3. Use QoS 0 (already default for high throughput)

### Messages Not Publishing

**Check**:
1. Verify MQTT broker is running: `docker-compose ps mosquitto`
2. Check publisher logs: `docker-compose logs publisher`
3. Verify database has unpublished data
4. Check network connectivity between containers

---

## Performance Benchmarks

Based on testing with default configuration:

| Rate (msg/sec) | CPU Usage | Memory Usage | Recommended Batch Size |
|----------------|-----------|--------------|------------------------|
| 1              | < 5%      | 50 MB        | 5-10                   |
| 10             | 10-15%    | 60 MB        | 20-50                  |
| 50             | 30-40%    | 80 MB        | 50-100                 |
| 100            | 50-70%    | 100 MB       | 100-200                |

**Note**: Performance varies based on hardware, network, and system load.

---

## Best Practices

1. **Start Low**: Begin with low rates and gradually increase
2. **Monitor**: Watch logs and system resources
3. **Batch Size**: Set batch size to 2-5x your target rate
4. **Auto Reset**: Use `AUTO_RESET: true` for continuous testing
5. **QoS**: Keep QoS 0 for high throughput (already default)
6. **Database**: Ensure PostgreSQL has adequate resources
7. **Network**: Use Docker networks for container communication

---

## Advanced Configuration

### Custom Message Format

To customize the Chirpstack message format, edit `publisher/publisher.py`:

```python
def create_chirpstack_message(self, record):
    # Modify this method to change message structure
    message = {
        # Your custom format here
    }
    return message
```

### Multiple Publishers

To run multiple publishers for even higher throughput:

```yaml
# In docker-compose.yml
publisher1:
  build: ./publisher
  container_name: mqtt-publisher-1
  environment:
    MESSAGES_PER_SECOND: 50

publisher2:
  build: ./publisher
  container_name: mqtt-publisher-2
  environment:
    MESSAGES_PER_SECOND: 50
```

This gives you 100 msg/sec total across two publishers.
