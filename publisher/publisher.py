#!/usr/bin/env python3
"""
MQTT Publisher Application
Reads sensor data from PostgreSQL and publishes to MQTT broker in Chirpstack format
Supports high-throughput publishing with configurable messages per second
"""

import os
import json
import time
import logging
import base64
from datetime import datetime
from threading import Thread, Event
import psycopg2
from psycopg2.extras import RealDictCursor
import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_TOPIC_TEMPLATE = os.getenv('MQTT_TOPIC', 'application/{app_id}/device/{dev_eui}/event/up')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_NAME = os.getenv('DB_NAME', 'mqttdata')
DB_USER = os.getenv('DB_USER', 'mqttuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'mqttpass')

# Publishing rate configuration
MESSAGES_PER_SECOND = float(os.getenv('MESSAGES_PER_SECOND', 1))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 10))  # Number of messages to fetch at once
AUTO_RESET = os.getenv('AUTO_RESET', 'true').lower() == 'true'  # Auto-reset when no unpublished data


class MQTTPublisher:
    def __init__(self):
        self.mqtt_client = None
        self.db_conn = None
        self.connected = False
        self.stop_event = Event()
        self.publish_count = 0
        self.error_count = 0
        self.start_time = None
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback when MQTT client connects"""
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
            self.connected = True
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
            self.connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback when MQTT client disconnects"""
        logger.warning(f"Disconnected from MQTT broker, return code: {rc}")
        self.connected = False
    
    def on_publish(self, client, userdata, mid):
        """Callback when message is published"""
        logger.debug(f"Message {mid} published successfully")
    
    def connect_mqtt(self):
        """Initialize and connect MQTT client"""
        try:
            self.mqtt_client = mqtt.Client(client_id="chirpstack-simulator")
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_disconnect = self.on_disconnect
            self.mqtt_client.on_publish = self.on_publish
            
            logger.info(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.5)
            
            if not self.connected:
                raise Exception("MQTT connection timeout")
                
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            logger.info(f"Connecting to database at {DB_HOST}:{DB_PORT}/{DB_NAME}...")
            self.db_conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            logger.info("Database connection established")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def get_unpublished_data_batch(self, limit=10):
        """Fetch batch of unpublished sensor data from database"""
        try:
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, device_eui, application_id, device_name, 
                       f_port, f_cnt, data, rssi, snr, timestamp
                FROM sensor_data
                WHERE published = FALSE
                ORDER BY timestamp ASC
                LIMIT %s
            """, (limit,))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Failed to fetch data from database: {e}")
            return []
    
    def mark_as_published(self, record_ids):
        """Mark multiple records as published in the database"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                UPDATE sensor_data 
                SET published = TRUE 
                WHERE id = ANY(%s)
            """, (record_ids,))
            self.db_conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Failed to mark records as published: {e}")
            self.db_conn.rollback()
            return False
    
    def reset_published_status(self):
        """Reset all records to unpublished for continuous testing"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT reset_published_status()")
            self.db_conn.commit()
            cursor.close()
            logger.info("All records reset to unpublished")
            return True
        except Exception as e:
            logger.error(f"Failed to reset published status: {e}")
            self.db_conn.rollback()
            return False
    
    def create_chirpstack_message(self, record):
        """Create a Chirpstack-formatted MQTT message from database record"""
        message = {
            "deviceInfo": {
                "applicationId": str(record['application_id']),
                "applicationName": f"app-{record['application_id']}",
                "deviceName": record['device_name'],
                "devEui": record['device_eui'],
            },
            "rxInfo": [
                {
                    "gatewayId": "0000000000000001",
                    "uplinkId": record['id'],
                    "name": "test-gateway",
                    "rssi": record['rssi'],
                    "snr": record['snr'],
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
            "adr": True,
            "fCnt": record['f_cnt'],
            "fPort": record['f_port'],
            "data": base64.b64encode(json.dumps(record['data']).encode()).decode(),
            "object": record['data'],
            "tags": {},
            "confirmedUplink": False,
            "devAddr": "00000000",
            "publishedAt": record['timestamp'].isoformat() if record['timestamp'] else datetime.utcnow().isoformat()
        }
        return message
    
    def publish_message(self, record):
        """Publish a single message to MQTT broker"""
        try:
            # Create topic
            topic = MQTT_TOPIC_TEMPLATE.format(
                app_id=record['application_id'],
                dev_eui=record['device_eui']
            )
            
            # Create message payload
            message = self.create_chirpstack_message(record)
            payload = json.dumps(message)
            
            # Publish to MQTT
            result = self.mqtt_client.publish(topic, payload, qos=0)  # QoS 0 for high throughput
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.publish_count += 1
                if self.publish_count % 100 == 0:  # Log every 100 messages
                    logger.info(f"Published {self.publish_count} messages (Device: {record['device_name']})")
                return True
            else:
                logger.error(f"Failed to publish message, return code: {result.rc}")
                self.error_count += 1
                return False
                
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            self.error_count += 1
            return False
    
    def print_stats(self):
        """Print publishing statistics"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            rate = self.publish_count / elapsed if elapsed > 0 else 0
            logger.info(f"Stats: {self.publish_count} messages published, {self.error_count} errors, {rate:.2f} msg/sec")
    
    def stats_thread(self):
        """Background thread to print statistics periodically"""
        while not self.stop_event.is_set():
            time.sleep(30)  # Print stats every 30 seconds
            if not self.stop_event.is_set():
                self.print_stats()
    
    def run(self):
        """Main loop to fetch and publish data at specified rate"""
        logger.info("Starting MQTT Publisher...")
        
        # Connect to services
        if not self.connect_mqtt():
            logger.error("Cannot start without MQTT connection")
            return
        
        if not self.connect_db():
            logger.error("Cannot start without database connection")
            return
        
        logger.info(f"Publisher started. Target rate: {MESSAGES_PER_SECOND} messages/second")
        logger.info(f"Batch size: {BATCH_SIZE}, Auto-reset: {AUTO_RESET}")
        
        # Start statistics thread
        self.start_time = time.time()
        stats_thread = Thread(target=self.stats_thread, daemon=True)
        stats_thread.start()
        
        try:
            # Calculate delay between messages
            if MESSAGES_PER_SECOND > 0:
                delay_between_messages = 1.0 / MESSAGES_PER_SECOND
            else:
                delay_between_messages = 1.0  # Default to 1 second if rate is 0
            
            logger.info(f"Delay between messages: {delay_between_messages:.4f} seconds")
            
            while not self.stop_event.is_set():
                # Fetch batch of unpublished data
                records = self.get_unpublished_data_batch(BATCH_SIZE)
                
                if records:
                    published_ids = []
                    
                    for record in records:
                        if self.stop_event.is_set():
                            break
                        
                        # Record time before publishing
                        publish_start = time.time()
                        
                        # Publish message
                        if self.publish_message(record):
                            published_ids.append(record['id'])
                        
                        # Calculate how long to sleep to maintain rate
                        elapsed = time.time() - publish_start
                        sleep_time = delay_between_messages - elapsed
                        
                        if sleep_time > 0:
                            time.sleep(sleep_time)
                    
                    # Mark batch as published
                    if published_ids:
                        self.mark_as_published(published_ids)
                        
                else:
                    # No unpublished data available
                    if AUTO_RESET:
                        logger.info("No unpublished data available. Resetting published status...")
                        self.reset_published_status()
                        time.sleep(0.1)  # Small delay before continuing
                    else:
                        logger.info("No unpublished data available. Waiting...")
                        time.sleep(5)  # Wait before checking again
                
        except KeyboardInterrupt:
            logger.info("Shutting down publisher...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.stop_event.set()
            self.print_stats()
            self.cleanup()
    
    def cleanup(self):
        """Clean up connections"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logger.info("MQTT client disconnected")
        
        if self.db_conn:
            self.db_conn.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    publisher = MQTTPublisher()
    publisher.run()
