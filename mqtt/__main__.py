import os
import time

from mqtt.service.mqtt_publish import MQTTPublisher
from util.generate_time_value import generate_time_value


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
