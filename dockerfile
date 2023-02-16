FROM python:3.10-slim

WORKDIR /app

# get requirements file
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

# copy kafka_client files
COPY topics.yaml topics.yaml
COPY dags.yaml dags.yaml
COPY kafka_client kafka_client

EXPOSE 9092
# Run aplication to create topics
CMD ["python3", "kafka_client/admin.py"]