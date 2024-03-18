FROM python:3

ENV DATABASE_TYPE=sqlite
ENV DATABASE_NAME=db.sqlite
ENV PERSISTENCE_PATH=/data


WORKDIR /app

COPY . .


RUN apt-get update && apt-get install -y git
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "main.py" ]