import yaml
from confluent_kafka.admin import AdminClient, NewTopic, ConfigResource

from producer import producer_main
from consumer import consumer_main

KAFKA_CONFIG = {
     'bootstrap.servers': 'localhost:9092',
     'group.id': 'kafka_101',
     # 'security.protocol': None,
     'sasl.mechanisms': 'PLAIN',
     # 'sasl.username': '<CLUSTER_API_KEY>', 
     # 'sasl.password': '<CLUSTER_API_SECRET>'
}

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
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data

def topic_exists(admin, topic):
    """
    Evaluate if topic already exist
    Args:
        admin (object): admin object
        topic (string): name of the topic
    Returns:
        bool (bool): True if topic exists and False if not
    """
    metadata = admin.list_topics()

    for t in iter(metadata.topics.values()):
        if t.topic == topic:
            return True
    return False

def create_topic(admin, topic):
    """"
    Create a new Kafka topic
    Args:
        admin (object): admin object
        topic (dict): info of the topic to be created
            example: {   
                'topic_name': "my-topic-0"
                'n_partitions': 2
                'replication_factor': 1
                'config': {
                    'compression.type': 'gzip'
                }
            }
    Returns:
        None
    """
    topic_name = str(topic['topic_name'])
    # create topic class object
    new_topic = NewTopic(
        topic = str(topic['topic_name']), 
        num_partitions = int(topic['n_partitions']), 
        replication_factor = int(topic['replication_factor']),
        config = topic['config']
    ) 
    result_dict = admin.create_topics([new_topic])
    # return result
    for topic, future in result_dict.items():
        try:
            future.result()  # The result itself is None
            print(f"Topic {topic_name} created")
        except Exception as e:
            print(f"Failed to create topic {topic_name}: {e}")

def list_existing_topics(admin):
    """
    List all kafka topics
    Args:
        admin (object): admin object
    Returns:
        topics (list): List of topics name
    """
    metadata = admin.list_topics()
    topics = []
    for t in iter(metadata.topics.values()):
        topics.append(t)
    return topics

if __name__ == '__main__':
    try:
        # Create Admin client
        admin = AdminClient(KAFKA_CONFIG)
        print("@ Existing topics :: ", list_existing_topics(admin))
        
        # get topics from topics.yaml
        topics = get_topics()

        # Create topic if it doesn't exist
        for topic in topics:
            topic = topics[topic]
            if not topic_exists(admin, topic['topic_name']):
                create_topic(admin, topic)

        # Start Producer
        print("@ Start kafka producer ...")
        producer_main(KAFKA_CONFIG)
        # Start Consumer
        print("@ Start kafka consumer ...")
        consumer_main()

    except KeyboardInterrupt:
        print('Canceled by user.')