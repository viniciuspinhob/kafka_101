from confluent_kafka import Producer
from datetime import datetime
import json
import random
import time

TOPIC_NAME = "my-topic-1"

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err:
            print('ERROR: Message failed delivery: {}'.format(err))
    else:
        print("Produced event to topic {topic}".format(
            topic=msg.topic()))

def produce_to_topic(producer, data):
    
    # Trigger any available delivery report callbacks from previous produce() calls
    producer.poll(0)
    # Asynchronously produce a message. The delivery report callback will
    # be triggered from the call to poll() above, or flush() below, when the
    # message has been successfully delivered or failed permanently.
    data = json.dumps(data).encode('utf-8')
    producer.produce(TOPIC_NAME, data, callback=delivery_report) 

def producer_main(config):
    try:
        producer = Producer(config)
        while True:
            
            data = {
                'timestamp': str(datetime.now()), 
                'tagname' : random.choice(['tag1', 'tag2', 'tag3']),
                'value' : random.random(), 
                'quality' : random.choice(['Good', 'Neutral', 'Bad']) 
            }
            
            produce_to_topic(producer, data)
            # Wait for any outstanding messages to be delivered and delivery report
            # callbacks to be triggered.
            producer.flush()
            time.sleep(5)
    except KeyboardInterrupt:
        print('Canceled by user.')