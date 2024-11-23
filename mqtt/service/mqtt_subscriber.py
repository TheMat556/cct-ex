import time

import paho.mqtt.client as mqtt
import threading
import json


class MQTTClient:
  def __init__(self, broker, port, topic):
    self._thread = None
    self.broker = broker
    self.port = int(port)
    self.topic = topic

    self._subscribers = []
    self._latest_data = None
    self._stop_event = threading.Event()

    self.mqtt_client = mqtt.Client()
    self.mqtt_client.on_connect = self._on_connect
    self.mqtt_client.on_message = self._on_message

  def _on_connect(self, client, userdata, flags, rc):
    if rc == 0:
      print(f'Connected to MQTT broker, subscribing to {self.topic}')
      client.subscribe(self.topic)
    else:
      print(f'#LOG-ERROR: Failed to connect to MQTT broker with code {rc}')

  def _on_message(self, client, userdata, msg):
    try:
      data = json.loads(msg.payload.decode())
      self._latest_data = data
      self._notify_subscribers(data)
    except Exception as e:
      print(f'#LOG-ERROR: Error processing message: {e}')

  def start(self):
    try:
      self.mqtt_client.connect(self.broker, self.port, 60)
      self._thread = threading.Thread(target=self._mqtt_loop, daemon=True)
      self._thread.start()
    except Exception as e:
      print(f'#LOG-ERROR: Error starting MQTT client: {e}')

  def _mqtt_loop(self):
    self.mqtt_client.loop_forever()

  def stop(self):
    self._stop_event.set()
    self.mqtt_client.disconnect()
    if hasattr(self, '_thread'):
      self._thread.join()

  def subscribe(self, callback):
    self._subscribers.append(callback)
    return lambda: self._subscribers.remove(callback)

  def _notify_subscribers(self, data):
    for callback in self._subscribers:
      callback(data)

  def get_latest_data(self):
    return self._latest_data


if __name__ == '__main__':

  def on_data_received(data):
    print('Received MQTT data:', data)

  client = MQTTClient(broker='broker.hivemq.com', port=1883, topic='thagenberg')

  unsubscribe = client.subscribe(on_data_received)

  client.start()

  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    client.stop()
    unsubscribe()
