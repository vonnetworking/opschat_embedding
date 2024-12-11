import boto3
import json
import time
import os
import logging
from embeddings_util import EmbeddingsUtil

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Adjust log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  # StreamHandler ensures logs are printed to stdout
    ]
)

def read_messages_from_sqs(sqs, queue_url, max_messages=10, wait_time=10):
    try:
        # Receive messages from the queue
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_time,
            VisibilityTimeout=30
        )

        # Check if any messages were retrieved
        messages = response.get('Messages', [])
        if not messages:
            logging.info("No messages available in the queue.")
            return []

        # Process each message
        texts = []
        for message in messages:
            logging.info(f"Message ID: {message['MessageId']}")
            #logging.info(f"Body: {message['Body']}")
            array = json.loads(message['Body'])
            for text in array:
                texts.append(text)

            # Delete the message after processing
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
            logging.info(f"Message {message['MessageId']} deleted from the queue.")

        return texts

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    sqs = boto3.client('sqs')
    queue_url = os.getenv("AWS_QUEUE_URL")
    embedding_model = os.getenv("EMBEDDING_MODEL")
    embeddings_util = EmbeddingsUtil(embedding_model)
    
    logging.info("Starting to read messages from the SQS queue every second...")
    while True:
        messages = read_messages_from_sqs(sqs, queue_url, max_messages=10, wait_time=1)
        if len(messages) > 0:
            embeddings = embeddings_util.get(messages)

        time.sleep(1)