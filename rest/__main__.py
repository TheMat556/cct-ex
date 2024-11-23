from rest.microservice.server import TimestampApp


def create_app():
  return TimestampApp()


if __name__ == '__main__':
  timestamp_app = create_app()
  timestamp_app.run()
