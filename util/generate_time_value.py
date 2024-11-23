import json
import time
import numpy as np


def generate_time_value():
  price = np.random.uniform(50, 200)
  # TODO: Check this again
  future_timestamp = int(time.time()) + 7200
  message = json.dumps({'price': price, 'timestamp': future_timestamp})
  return message
