import json
import logging
import boto3

class SQS:
    def __init__(self):
        self.sqs = boto3.client('sqs')

    def read(self, queue_url, max_messages=10, wait_time=10):
        try:
            # Receive messages from the queue
            response = self.sqs.receive_message(
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
            items = []
            for message in messages:
                logging.info(f"Message ID: {message['MessageId']}")
                array = json.loads(message['Body'])
                for item in array:
                    items.append(item)

                # Delete the message after processing
                self.sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )

            return items

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return []
        
    def write(self, queue_url, message_body):
        try:
            response = self.sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=message_body
            )
            return response
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise