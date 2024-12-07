import os
import time

import paho.mqtt.client as mqtt

from util.generate_time_value import generate_time_value


class MQTTPublisher:
  def __init__(self, mqtt_broker, mqtt_port, mqtt_topic):
    self.mqtt_broker = mqtt_broker
    self.mqtt_port = int(mqtt_port)
    self.mqtt_topic = mqtt_topic

    self.mqtt_client = mqtt.Client()
    self.mqtt_client.on_connect = self.on_connect
    self.mqtt_client.on_publish = self.on_publish

    # self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)

  def on_connect(self, client, userdata, flags, rc):
    if rc == 0:
      print(f'Connected to MQTT broker, subscribing to {self.mqtt_topic}')
      client.subscribe(self.mqtt_topic)
    else:
      print(f'#LOG-ERROR: Failed to connect to MQTT broker with code {rc}')

  def start(self):
    try:
      self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
      self.mqtt_client.loop_start()
    except Exception as e:
      print(f'#LOG-ERROR: Error starting MQTT client: {e}')

  def on_publish(self, client, userdata, mid):
    print(f'#LOG-INFO: Message {mid} published successfully to {self.mqtt_topic}')

  def publish_price_updates(self, json_message):
    print(json_message)
    try:
      self.mqtt_client.publish(self.mqtt_topic, json_message)
    except Exception as e:
      print(f'#LOG-ERROR: Error publishing price update: {e}')
      time.sleep(1)


def main():
  print('Starting MQTT-Publisher')
  mqttPublisher = MQTTPublisher(
    os.getenv('PRIVATE_MQTT_BROKER'),
    os.getenv('PRIVATE_MQTT_PORT'),
    os.getenv('PRIVATE_MQTT_TOPIC'),
  )
  mqttPublisher.start()
  while True:
    time_value_json = generate_time_value()
    mqttPublisher.publish_price_updates(time_value_json)
    time.sleep(5)


if __name__ == '__main__':
  main()
