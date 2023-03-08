import yaml
from datetime import datetime
from confluent_kafka import Consumer
import ast
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

# Kafka configs
CONSUMER_TIME = 30
KAFKA_TOPICS = []
KAFKA_CONFIG = {
    'bootstrap.servers': 'broker:29092',
    'sasl.mechanisms': 'PLAIN',
    # 'security.protocol': 'SSL',
    #  'ssl.ca.location': 'keys/controlemalhas-CARoot.pem',
    #  'ssl.key.location': 'keys/controlemalhas-keystoreKey.pem',
    #  'ssl.certificate.location': 'keys/controlemalhas-truststore.pem',

    # 'session.timeout.ms': '45000',
    'group.id': 'sink-connector',
    # 'auto.offset.reset': 'latest',

    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    # 'max.poll.records' : 5000,
    'heartbeat.interval.ms': 30000,
    'max.poll.interval.ms': 30000,
    'session.timeout.ms': 30000,
}
# Database
# postgres://user:password@host/database
DB_POSTGRES = "postgresql://postgres:postgres@postgres:5432/postgres"
DB_TIMESCALE = "postgresql://postgres:postgres@timescaledb:5432/postgres"


def get_topics():
    """
    Read topics.yaml file and returns a dict containing all topics
    Args:
        None
    Returns:
        data (dict): dictionary of topics
            example:
                data = {   
                    'topic_name': "my-topic-0"
                    'n_partitions': 2
                    'replication_factor': 1
                    'config': {
                        'compression.type': 'gzip'
                    }
                }
    """
    with open("./topics.yaml", "r") as file:
        topics = yaml.load(file, Loader=yaml.FullLoader)

    topic_names = []
    for topic in topics:
        topic_names.append(topics[topic]['topic_name'])
    print("# topic names", topic_names)
    return topic_names


def consume_loop(consumer):
    """
    Consumes messages, during specified time, from kafka topics and add them to a 
    list of messages

    Args:
        consumer (): kafka consumer

    Returns:
        messages (list) : list of read kafka messages
    """
    time_zero = datetime.now()
    messages = []
    # Process messages
    total_count = 0
    empty_messages = 0
    running = True
    try:
        while running:
            msg = consumer.poll(1.0)
            timeout = (datetime.now() - time_zero).seconds
            if timeout >= CONSUMER_TIME:
                consumer.commit(asynchronous=False)
                # logger.info("Consumed {} records".format(total_count))
                # logger.warning("40s elapsed. Closing connection.")
                print("Consumed {} records".format(total_count))
                print(f"{CONSUMER_TIME}s elapsed. Closing connection.")
                running = False
                break
            if msg is None:
                empty_messages = empty_messages + 1
                pass
            elif msg.error():
                # logger.error('error: {}'.format(msg.error()))
                print('error: {}'.format(msg.error()))
            else:
                # Check for Kafka message
                message_data = ast.literal_eval(msg.value().decode('utf-8'))
                data = {
                    'tagname': message_data['tagname'],
                    'value': message_data['value'],
                    'timestamp': message_data['timestamp'],
                    'quality': message_data['quality']
                }
                messages.append(data)
                total_count += 1

    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
        print(f"Consumer Closed!")
    return messages


def save_data(df, database):
    """
    Save messages messages to a database

    Args:
        message (list):list of dicts (kafka messages)
    Returns:
        bool : true
    """
    try:
        # create db engine
        engine = create_engine(database)
        # insert data
        df.to_sql('process_data', con=engine, if_exists="append",
                  index=False, method='multi')
    except Exception as e:
        print(e)
        return False
    else:
        return True


def connect_main():
    try:
        # Create Consumer client
        consumer = Consumer(KAFKA_CONFIG)
        # get topics from topics.yaml
        topics = get_topics()
        # subscribe to topics
        consumer.subscribe(topics)
        # consume messages
        messages = consume_loop(consumer)
        # transform messages into dataframe
        df = pd.DataFrame.from_dict(messages)
        # save data to Database
        save_data(df, DB_POSTGRES)
        save_data(df, DB_TIMESCALE)

    except KeyboardInterrupt:
        print('Canceled by user.')
