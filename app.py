import json
import os
import logging
from embeddings_util import EmbeddingsUtil
from activemq_util import ActiveMQ

host_name = os.getenv('HOSTNAME', 'unknown-host')

message_processed = 1

# Configure the embeddings utility
embeddings_util = EmbeddingsUtil(os.getenv("EMBEDDING_MODEL_LOCATION"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Adjust log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format=f"%(asctime)s [{host_name}] [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  # StreamHandler ensures logs are printed to stdout
    ]
)

def merge_embeddings(embeddings_util, items):
    texts = []

    # Get the texts from the messages
    for item in items:
        text = item['text']
        texts.append(text)

    # Get the embeddings and merge back in
    embeddings = embeddings_util.get(texts)
    for item, embedding in zip(items, embeddings):
        item["embeddings"] = embedding
    return items

def process_message(message):
    global message_processed  # Declare the global variable
    logging.info(f"Processing message: {message_processed}")
    modified_items = merge_embeddings(embeddings_util, message)

    # Write the items with merged embeddings to the vector store queue
    activemq.write(json.dumps(modified_items), queue_name=vector_store_queue)
    message_processed += 1  # Increment the global counter
 
if __name__ == "__main__":
    activemq_host = os.getenv("ACTIVEMQ_HOST")
    activemq_port = os.getenv("ACTIVEMQ_PORT") 
    embeddings_queue = os.getenv("EMBEDDING_QUEUE") + "/" + host_name
    vector_store_queue = os.getenv("VECTOR_STORE_QUEUE")

    # Connect to ActiveMQ
    activemq = ActiveMQ(host=activemq_host, port=int(activemq_port), username='artemis', password='artemis')
    logging.info(f"Listening for messages from the queue: {embeddings_queue}...")
    while True:
        activemq.connect()

        # Listen for messages
        try:
            activemq.read(queue_name=embeddings_queue, on_message_callback=process_message)
            activemq.disconnect()
        except Exception as e:
            logging.error(f"Error reading from queue: {e}")
            activemq.disconnect()