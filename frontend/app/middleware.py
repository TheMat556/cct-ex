import datetime
import json

from influxdb import influx_client
from mqtt.service.mqtt_subscriber import MQTTSubscriber
from rest.microservice.client import RESTSubscriber


class FrontEndMiddleware:
  def __init__(self, rest_url, mqtt_broker, mqtt_port, mqtt_topic):
    # Initialize clients
    self.rest_client = RESTSubscriber(url=rest_url, interval=5)
    self.mqtt_client = MQTTSubscriber(
      broker=mqtt_broker, port=mqtt_port, topic=mqtt_topic
    )
    self._start_clients()
    self.start()

  def _start_clients(self):
    self.rest_client.start()
    self.mqtt_client.start()

  def start(self):
    # Subscribe clients
    self.rest_client.subscribe(self._rest_data_callback)
    self.mqtt_client.subscribe(self._mqtt_data_callback)

  def _rest_data_callback(self, data):
    try:
      message = json.loads(data)
      timestamp = int(message['timestamp'])
      datetime_obj = datetime.datetime.fromtimestamp(timestamp)
      influx_client.write_data(
        measurement='REST',
        tags={'tag_key': 'energyprice'},
        fields={'value': message['price']},
        timestamp=datetime_obj.astimezone(datetime.timezone.utc).isoformat(
          timespec='milliseconds'
        ),
      )
    except Exception as e:
      print(f'Error processing REST data: {e}')

  def _mqtt_data_callback(self, data):
    timestamp = int(data['timestamp'])
    datetime_obj = datetime.datetime.fromtimestamp(timestamp)
    try:
      influx_client.write_data(
        measurement='MQTT',
        tags={'tag_key': 'energyprice'},
        fields={'value': data['price']},
        timestamp=datetime_obj.astimezone(datetime.timezone.utc).isoformat(
          timespec='milliseconds'
        ),
      )
    except Exception as e:
      print(f'Error processing MQTT data: {e}')
