import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from embeddings_util import EmbeddingsUtil
from activemq_util import ActiveMQ

# Configure the embeddings utility
embeddings_util = EmbeddingsUtil(os.getenv("EMBEDDING_MODEL"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# ThreadPoolExecutor with a maximum of 10 threads
executor = ThreadPoolExecutor(max_workers=50)

def merge_embeddings(embeddings_util, items):
    """Gets embeddings for items and merges them back into the list."""
    texts = [item['text'] for item in items]
    embeddings = embeddings_util.get(texts)
    for item, embedding in zip(items, embeddings):
        item["embeddings"] = embedding
    return items

def process_message_threaded(message):
    """Processes a single message and returns the result."""
    try:
        logging.info(f"Processing message")
        result = merge_embeddings(embeddings_util, message)
        logging.info(f"Successfully processed embeddings")
        return result
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        return None  # Return None or an appropriate error indicator

def process_message(message):
    """Callback for messages, submits processing to the thread pool and collects results."""
    #logging.info(f"Received message: {message}")
    future = executor.submit(process_message_threaded, message)
    return future 

if __name__ == "__main__":
    embeddings_queue = os.getenv("EMBEDDING_QUEUE")
    vector_store_queue = os.getenv("VECTOR_STORE_QUEUE")

    # Connect to ActiveMQ
    activemq = ActiveMQ(host='localhost', port=61616, username='artemis', password='artemis')
    activemq.connect()

    # Listen for messages
    futures = []
    logging.info("Starting to read messages from the queue...")
    
    def handle_message(message):
        # Submit to the thread pool and track the future
        future = process_message(message)
        futures.append(future)

    activemq.read(queue_name=embeddings_queue, on_message_callback=handle_message)

    # Optionally, handle results as they complete
    for future in as_completed(futures):
        result = future.result()  # Get the result of the computation
        if result is not None:
            logging.info(f"Processed result: {result}")
        else:
            logging.warning("A message failed to process.")