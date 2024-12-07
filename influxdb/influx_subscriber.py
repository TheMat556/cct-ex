# File: influxdb/influx_subscriber.py
import os
import threading
import time
from influxdb_client import InfluxDBClient


class InfluxDBSubscriber:
  def __init__(self, bucket, measurements, interval=1):
    self.bucket = bucket
    self.measurements = measurements
    self.interval = interval
    self._subscribers = {measurement: [] for measurement in measurements}
    self._stop_event = threading.Event()
    self._threads = []
    self._latest_data = {measurement: None for measurement in measurements}
    self.influx_client = InfluxDBClient(
      url=os.getenv('INFLUX_URL'),
      token=os.getenv('INFLUX_TOKEN'),
      org=os.getenv('INFLUX_ORG'),
    )
    self.query_api = self.influx_client.query_api()

  def start(self):
    for measurement in self.measurements:
      thread = threading.Thread(
        target=self._fetch_data_loop, args=(measurement,), daemon=True
      )
      self._threads.append(thread)
      thread.start()

  def stop(self):
    self._stop_event.set()
    for thread in self._threads:
      thread.join()

  def _fetch_data_loop(self, measurement):
    while not self._stop_event.is_set():
      try:
        query = f'from(bucket: "{self.bucket}") \
                          |> range(start: -5m) \
                          |> filter(fn: (r) => r["_measurement"] == "{measurement}") \
                          |> sort(columns: ["_time"], desc: true) \
                          |> limit(n: 1)'
        result = self.query_api.query(org=os.getenv('INFLUX_ORG'), query=query)
        points = []

        for table in result:
          for record in table.records:
            points.append(record)

        if points:
          self._latest_data[measurement] = points[0]
          self._notify_subscribers(measurement, self._latest_data[measurement])
        time.sleep(self.interval)
      except Exception:
        time.sleep(self.interval)

  def subscribe(self, measurement, callback):
    if measurement in self._subscribers:
      self._subscribers[measurement].append(callback)
      return lambda: self._subscribers[measurement].remove(callback)
    else:
      raise ValueError(f'Measurement {measurement} not supported.')

  def _notify_subscribers(self, measurement, data):
    for callback in self._subscribers[measurement]:
      callback(data)

  def get_latest_data(self, measurement):
    return self._latest_data.get(measurement)
