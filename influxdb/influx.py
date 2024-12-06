from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxDBClientWrapper:
    def __init__(self, url, token, org, bucket):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

    def write_data(self, measurement, tags, fields, timestamp=None):
        point = Point(measurement)
        for tag_key, tag_value in tags.items():
            point = point.tag(tag_key, tag_value)
        for field_key, field_value in fields.items():
            point = point.field(field_key, field_value)
        if timestamp:
            point = point.time(timestamp, WritePrecision.NS)
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def read_data(self, measurement, start="-1h"):
        query = f'from(bucket: "{self.bucket}") |> range(start: {start}) |> filter(fn: (r) => r._measurement == "{measurement}")'
        result = self.query_api.query(org=self.org, query=query)
        return result

    def close(self):
        self.client.close()
