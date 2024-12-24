import hashlib
import json
import os
import logging
import uuid
from embeddings_util import EmbeddingsUtil
from activemq_util import ActiveMQ

host_name = os.getenv('EMBEDDING_HOSTNAME', 'unknown-host')
log_dir = os.getenv('EMBEDDING_LOG_DIR', '/tmp/logs')
uid = uuid.uuid4()
container_name = os.getenv('EMBEDDING_WORKER_NAME', f'embedding-app-{uid}')

message_processed = 1

# Configure the embeddings utility
embeddings_util = EmbeddingsUtil(os.getenv("EMBEDDING_MODEL_LOCATION"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Adjust log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format=f"%(asctime)s [{host_name}] [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # StreamHandler ensures logs are printed to stdout
        logging.FileHandler(f"{log_dir}/{container_name}.log")
        ]
)

def sha256_string(string):
  """Calculates the SHA-256 hash of a string."""
  # Create a SHA-256 hash object
  hash_object = hashlib.sha256()

  # Encode the string to bytes
  string_bytes = string.encode('utf-8')

  # Update the hash object with the bytes
  hash_object.update(string_bytes)

  # Return the hexadecimal representation of the hash
  return hash_object.hexdigest()

def merge_embeddings(embeddings_util, items, message_hash=""):
    texts = []
    logging.info(f"Procesing items SHA: {message_hash}")

    # Get the texts from the messages
    for item in items:
        text = item['text']
        texts.append(text)

    # Get the embeddings and merge back in
    embeddings = embeddings_util.get(texts)
    for item, embedding in zip(items, embeddings):
        item["embeddings"] = embedding
    return items

def process_message(frame):
    global message_processed  # Declare the global variable
    logging.info(f"Processing message: {message_processed}")
    message_hash = sha256_string(frame.body)
    modified_items = merge_embeddings(embeddings_util, json.loads(frame.body), message_hash=message_hash)
    
    # Write the items with merged embeddings to the vector store queue
    activemq.write(json.dumps(modified_items), queue_name=vector_store_queue, headers={'destination-type': 'ANYCAST'})
    message_processed += 1  # Increment the global counter
 
if __name__ == "__main__":
    activemq_host = os.getenv("ACTIVEMQ_HOST")
    activemq_port = os.getenv("ACTIVEMQ_PORT") 
    embeddings_queue = os.getenv("EMBEDDING_QUEUE") # + "/" + host_name
    vector_store_queue = os.getenv("VECTOR_STORE_QUEUE")

    # Connect to ActiveMQ
    activemq = ActiveMQ(host=activemq_host, port=int(activemq_port), username='artemis', password='artemis')
    logging.info(f"Listening for messages from the queue: {embeddings_queue}...")
    while True:
        activemq.connect()
        # Listen for messages
        try:
            activemq.read(queue_name=embeddings_queue, on_message_callback=process_message)
        except Exception as e:
            logging.error(f"Error reading from queue: {e}")
            activemq.disconnect()
