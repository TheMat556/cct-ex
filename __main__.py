import os

from dotenv import load_dotenv


def main():
  print('Hello World!')


if __name__ == '__main__':
  load_dotenv()
  print(
    os.getenv('PRIVATE_MQTT_BROKER'),
  )
  main()
