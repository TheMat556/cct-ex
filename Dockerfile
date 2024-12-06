FROM python:3.12-slim

RUN apt-get update && apt-get install -y wget

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv

RUN pipenv install --deploy --ignore-pipfile

COPY . .

EXPOSE 5000

CMD ["pipenv", "run", "python", "-m", "rest"]
