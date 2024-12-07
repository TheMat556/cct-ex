import datetime

from influxdb.influx import InfluxDBClientWrapper

if __name__ == '__main__':
  url = 'http://localhost:8086'
  token = 'hNkuhmqdFRhgcSjs3y9TJaeDx8Lk_MsQM4wEt5j9TtcW3zu174SA3mO3Ay5W1ZudwikgGHEsW0YCOdWnW6GfWQ=='
  org = 'fhooe'
  bucket = 'readtst'

  influx_client = InfluxDBClientWrapper(url, token, org, bucket)

  # Write data
  for i in range(10):
    influx_client.write_data(
      measurement='example_measurement8',
      tags={'tag_key': 'Energy'},
      fields={'value': 123 + i},
      timestamp=datetime.datetime.utcnow().isoformat(),
    )

  # Read data
  result = influx_client.read_data('example_measurement8')
  for table in result:
    for record in table.records:
      print(f'Time: {record.get_time()}, Value: {record.get_value()}')

  influx_client.close()
