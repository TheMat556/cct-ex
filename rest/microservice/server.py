from flask import Flask, jsonify

from util.generate_time_value import generate_time_value

app = Flask(__name__)


@app.route('/timestamps', methods=['GET'])
def get_timestamps():
  return jsonify(generate_time_value())


if __name__ == '__main__':
  app.run(debug=True, port=5000)
