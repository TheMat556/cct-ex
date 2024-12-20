import json
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import threading
from datetime import datetime

from frontend.app.middleware import FrontEndMiddleware
from influxdb.influx_subscriber import InfluxDBSubscriber


class DashDataVisualizer:
  def __init__(
    self,
    rest_url='http://127.0.0.1:5000/timestamps',
    mqtt_broker='broker.hivemq.com',
    mqtt_port=1883,
    mqtt_topic='thagenberg',
    influx_bucket='readtst',
    influx_measurements=['MQTT', 'REST'],
  ):
    # Initialize Dash app
    self.app = dash.Dash(__name__)

    self._frontend_middleware = FrontEndMiddleware(
      rest_url, mqtt_broker, mqtt_port, mqtt_topic
    )
    self._frontend_middleware.start()

    # Initialize InfluxDBSubscriber
    self.influx_subscriber = InfluxDBSubscriber(influx_bucket, influx_measurements)
    self.influx_subscriber.start()

    # Subscribe to InfluxDB measurements
    for measurement in influx_measurements:
      self.influx_subscriber.subscribe(measurement, self._influx_data_callback)

    # Initialize empty DataFrames with correct columns
    self.rest_df = pd.DataFrame(columns=['timestamp', 'price'])
    self.mqtt_df = pd.DataFrame(columns=['timestamp', 'price'])

    # Set up app layout
    self._setup_layout()

    # Set up callbacks
    self._setup_callbacks()

  def _influx_data_callback(self, data):
    try:
      measurement = data['_measurement']
      timestamp = self._convert_timestamp(data['_time'])
      price = data['_value']

      new_data = pd.DataFrame([{'timestamp': timestamp, 'price': price}])
      if measurement == 'MQTT':
        self.mqtt_df = pd.concat([self.mqtt_df, new_data], ignore_index=True).tail(50)
      elif measurement == 'REST':
        self.rest_df = pd.concat([self.rest_df, new_data], ignore_index=True).tail(50)

    except Exception as e:
      print(f'Error processing InfluxDB data: {e}')

  def _setup_layout(self):
    self.app.layout = html.Div(
      [
        html.H1(
          'Real-time Data Visualization',
          style={'textAlign': 'center', 'marginBottom': 30},
        ),
        html.Div(
          [
            dcc.Graph(id='rest-graph'),
            dcc.Graph(id='mqtt-graph'),
            dcc.Graph(id='difference-graph'),
          ]
        ),
        dcc.Interval(
          id='interval-component',
          interval=5 * 1000,  # update every 5 seconds
          n_intervals=0,
        ),
      ]
    )

  def _convert_timestamp(self, timestamp):
    """Convert timestamp to datetime object."""
    try:
      # Try parsing as unix timestamp first
      return datetime.fromtimestamp(float(timestamp))
    except (ValueError, TypeError):
      try:
        # Try parsing as ISO format
        tst = datetime.fromisoformat(str(timestamp))
        return tst
      except (ValueError, AttributeError):
        return datetime.strptime(
          timestamp, '%Y-%m-%dT%H:%M:%S.%f%z'
        )  # Return parsed datetime if possible

  def _get_time_range(self):
    """Get the common time range for all graphs."""
    all_timestamps = []

    if not self.rest_df.empty:
      all_timestamps.extend(self.rest_df['timestamp'])
    if not self.mqtt_df.empty:
      all_timestamps.extend(self.mqtt_df['timestamp'])

    if all_timestamps:
      min_time = min(all_timestamps)
      max_time = max(all_timestamps)
      return min_time, max_time
    return None, None

  def _setup_callbacks(self):
    @self.app.callback(
      [
        Output('rest-graph', 'figure'),
        Output('mqtt-graph', 'figure'),
        Output('difference-graph', 'figure'),
      ],
      [Input('interval-component', 'n_intervals')],
    )
    def update_graphs(n):
      # Get common time range
      min_time, max_time = self._get_time_range()

      # Common layout settings
      common_layout = dict(
        template='plotly_white',
        xaxis=dict(
          title='Time',
          range=[min_time, max_time] if min_time and max_time else None,
          tickformat='%Y-%m-%d %H:%M:%S',
        ),
      )

      # REST Graph
      rest_fig = px.line(
        self.rest_df, x='timestamp', y='price', title='REST Timestamp Data'
      )
      rest_fig.update_layout(yaxis_title='Price', **common_layout)

      # MQTT Graph
      mqtt_fig = px.line(self.mqtt_df, x='timestamp', y='price', title='MQTT Data')
      mqtt_fig.update_layout(yaxis_title='Price', **common_layout)

      # Difference Graph
      diff_fig = px.line(
        pd.DataFrame(columns=['timestamp', 'difference']),
        x='timestamp',
        y='difference',
        title='Difference between REST and MQTT Data',
      )

      if not self.rest_df.empty and not self.mqtt_df.empty:
        # Merge DataFrames on timestamp
        merged_df = pd.merge(
          self.rest_df,
          self.mqtt_df,
          on='timestamp',
          how='inner',
          suffixes=('_rest', '_mqtt'),
        )

        # Calculate differences for matching timestamps
        diff_df = pd.DataFrame(
          {
            'timestamp': merged_df['timestamp'],
            'difference': merged_df['price_rest'] - merged_df['price_mqtt'],
          }
        )

        # Sort by timestamp to maintain chronological order
        diff_df = diff_df.sort_values('timestamp')

        diff_fig = px.line(
          diff_df,
          x='timestamp',
          y='difference',
          title='Difference between REST and MQTT Data',
        )

      diff_fig.update_layout(yaxis_title='Price Difference', **common_layout)

      return rest_fig, mqtt_fig, diff_fig

  def _rest_data_callback(self, data):
    try:
      message = json.loads(data)
      # Convert timestamp to datetime
      timestamp = self._convert_timestamp(message['timestamp'])

      # Create DataFrame from the received data
      new_df = pd.DataFrame([{'timestamp': timestamp, 'price': message['price']}])

      # Concatenate with existing data and keep last 50 records
      self.rest_df = pd.concat([self.rest_df, new_df], ignore_index=True).tail(50)

    except Exception as e:
      print(f'Error processing REST data: {e}')

  def _mqtt_data_callback(self, data):
    try:
      # Convert timestamp to datetime
      timestamp = self._convert_timestamp(data['timestamp'])

      # Create DataFrame from single MQTT message
      new_data = pd.DataFrame([{'timestamp': timestamp, 'price': data['price']}])

      # Concatenate with existing data and keep last 50 records
      self.mqtt_df = pd.concat([self.mqtt_df, new_data], ignore_index=True).tail(50)

    except Exception as e:
      print(f'Error processing MQTT data: {e}')

    # Start clients in background
    client_thread = threading.Thread(target=self._start_clients, daemon=True)
    client_thread.start()

    # Run Dash app
    self.app.run_server(debug=True, use_reloader=False)


if __name__ == '__main__':
  visualizer = DashDataVisualizer()

  # Run Dash app
  visualizer.app.run_server(debug=True, use_reloader=False)
