import datetime

from influxdb.influx import InfluxDBClientWrapper

url = "http://localhost:8086"
token = "hNkuhmqdFRhgcSjs3y9TJaeDx8Lk_MsQM4wEt5j9TtcW3zu174SA3mO3Ay5W1ZudwikgGHEsW0YCOdWnW6GfWQ=="
org = "fhooe"
bucket = "newbucket"

influx_client = InfluxDBClientWrapper(url, token, org, bucket)

__all__ = [influx_client]
