# Getting Started

This guide will help you set up and run the server, client, and node.

## Prerequisites

Ensure you have [Pipenv](https://pipenv.pypa.io/en/latest/) installed. If not, you can install it using:

```bash
pip install pipenv
```

# Running the Application

## Start the MQTT server:
To start the MQTT server, run:

```bash
pipenv run start-mqtt-server
```

## Start the REST server:
To start the REST server, run:

```bash
pipenv run start-rest-server
```

## Start the frontend:
To start the frontend, use:

```bash
pipenv run start-frontend
```

## Start the containerized node:
```bash
docker build -t python-rest-test .
```

```bash
docker run -tid -p 0.0.0.0:5000:5000 python-rest-test
```
