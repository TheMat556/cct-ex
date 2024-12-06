# app/main.py
from flask import Flask, jsonify
from util.generate_time_value import generate_time_value


class TimestampApp:
  def __init__(self):
    self.app = Flask(__name__)
    self.setup_routes()

  def setup_routes(self):
    self.app.route('/timestamps', methods=['GET'])(self.get_timestamps)

  def get_timestamps(self):
    return jsonify(generate_time_value())

  def run(self, debug=False, port=5000):
    self.app.run(host="0.0.0.0", debug=debug, port=port)
