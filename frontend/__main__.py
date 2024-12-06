import threading

from frontend.app.fe import DashDataVisualizer

if __name__ == '__main__':
  visualizer = DashDataVisualizer()

  # Run Dash app
  visualizer.app.run_server(debug=True, use_reloader=False)
