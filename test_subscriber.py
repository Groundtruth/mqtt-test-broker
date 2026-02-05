#!/usr/bin/env python3
"""
Example MQTT Subscriber for Testing
Subscribe to Chirpstack messages and display them
"""

import paho.mqtt.client as mqtt
import json
import sys

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "application/+/device/+/event/up"


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"✓ Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"✓ Subscribed to topic: {MQTT_TOPIC}")
        print("\nWaiting for messages...\n")
        print("-" * 80)
    else:
        print(f"✗ Connection failed with code {rc}")
        sys.exit(1)


def on_message(client, userdata, msg):
    """Callback when message is received"""
    try:
        payload = json.loads(msg.payload.decode())
        
        print(f"\n📨 Message Received")
        print(f"Topic: {msg.topic}")
        print(f"Device: {payload.get('deviceName', 'Unknown')}")
        print(f"Device EUI: {payload.get('devEUI', 'Unknown')}")
        print(f"Application ID: {payload.get('applicationID', 'Unknown')}")
        print(f"Frame Counter: {payload.get('fCnt', 'Unknown')}")
        print(f"Port: {payload.get('fPort', 'Unknown')}")
        
        # Display sensor data
        data = payload.get('data', {})
        print(f"\n📊 Sensor Data:")
        for key, value in data.items():
            print(f"  • {key}: {value}")
        
        # Display signal info
        rx_info = payload.get('rxInfo', [])
        if rx_info:
            print(f"\n📡 Signal Info:")
            print(f"  • RSSI: {rx_info[0].get('rssi', 'N/A')} dBm")
            print(f"  • SNR: {rx_info[0].get('loRaSNR', 'N/A')} dB")
        
        print("-" * 80)
        
    except json.JSONDecodeError:
        print(f"✗ Failed to decode JSON message")
    except Exception as e:
        print(f"✗ Error processing message: {e}")


def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    if rc != 0:
        print(f"\n✗ Unexpected disconnection (code: {rc})")


def main():
    """Main function"""
    print("=" * 80)
    print("MQTT Test Subscriber - Chirpstack Message Monitor")
    print("=" * 80)
    
    # Create MQTT client
    client = mqtt.Client(client_id="test-subscriber")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        # Connect to broker
        print(f"\nConnecting to {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Start loop
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n\n✓ Subscriber stopped by user")
        client.disconnect()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
