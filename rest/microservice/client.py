import requests
import threading
import time


class TimestampClient:
  def __init__(self, url='http://127.0.0.1:5000/timestamps', interval=5):
    self.url = url
    self.interval = interval
    self._subscribers = []
    self._stop_event = threading.Event()
    self._thread = None
    self._latest_data = None

  def start(self):
    self._thread = threading.Thread(target=self._fetch_data_loop, daemon=True)
    self._thread.start()

  def stop(self):
    self._stop_event.set()
    if self._thread:
      self._thread.join()

  def _fetch_data_loop(self):
    while not self._stop_event.is_set():
      try:
        response = requests.get(self.url)
        if response.status_code == 200:
          self._latest_data = response.json()
          self._notify_subscribers(self._latest_data)
        time.sleep(self.interval)
      except Exception as e:
        print(f'Error fetching timestamps: {e}')
        time.sleep(self.interval)

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
    print('Received data:', data)

  client = TimestampClient()

  unsubscribe = client.subscribe(on_data_received)
  client.start()

  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    client.stop()
    unsubscribe()
