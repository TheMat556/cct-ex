import json
import math
import time
import numpy as np


def generate_time_value():
  price = np.random.uniform(50, 200)
  # TODO: Check this again
  timestamp = int(time.time())
  rounded_timestamp = math.floor(timestamp / 5) * 5
  message = json.dumps({'price': price, 'timestamp': rounded_timestamp})
  return message
