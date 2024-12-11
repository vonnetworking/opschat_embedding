import boto3
import uuid
import os
import json
import asyncio

def process_program_logs(line):
    tokens = line.strip().split(',')
    timestamp = tokens[0].strip()
    log_level = tokens[1].strip().lower()
    application = tokens[2].strip().lower()
    ip = tokens[3].strip().lower()
    message = tokens[4].strip().lower()
    text_to_embed = timestamp + ", " + log_level + ", " + application + ", " + ip + ", " + message
    my_dict = {'text': text_to_embed, 'metadata': {'timestamp': timestamp, 'log_level': log_level, 'application': application, 'ip': ip, 'message': message}}
    return my_dict

def process_change_tickets(line):
    tokens = line.strip().split(',')
    timestamp = tokens[0].strip()
    change_id = tokens[1].strip().lower()
    application = tokens[2].strip().lower()
    ip = tokens[3].strip().lower()
    change_type = tokens[4].strip().lower()
    message = tokens[5].strip().lower()
    status = tokens[6].strip().lower()
    text_to_embed = timestamp + ", change ID or ticket:" + change_id + ", " + application + ", " + ip + ", " + change_type + ", " + message + ", " + status
    my_dict = {'text': text_to_embed, 'metadata': {'timestamp': timestamp, 'change_id': change_id, 'application': application, 'ip': ip, 
                                                   'change_type': change_type, 'message': message, 'status': status}}
    return my_dict

def load_files(subdirectory):
    # Get the list of all files in the subdirectory
    files = [f for f in os.listdir(subdirectory) if os.path.isfile(os.path.join(subdirectory, f))]
    
    for file in files:
        file_path = os.path.join(subdirectory, file)
        with open(file_path, 'r') as f:
            items = []
            for line in f:
                if file_path.endswith("program_logs.txt"):
                    items.append(process_program_logs(line))
                else:
                    items.append(process_change_tickets(line))
        return items

def chunk_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

async def send_message_to_fifo_queue(sqs, queue_url, message_body):
    # Generate deduplication_id
    deduplication_id = str(uuid.uuid4())
    
    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body,
            #MessageGroupId="group1",
            #MessageDeduplicationId=deduplication_id
        )
        print("Message sent! MessageId:", response['MessageId'])
        return response
    except Exception as e:
        print("Error sending message to SQS:", str(e))
        raise

async def main():
    sqs = boto3.client('sqs')
    queue_url = os.getenv("AWS_QUEUE_URL")

    items = load_files('./data')

    texts = []
    for item in items:
        text = item["text"]
        texts.append(text)

    chunks = chunk_list(texts, 100)
    async with asyncio.TaskGroup() as tg:
        for chunk in chunks:
            tg.create_task(send_message_to_fifo_queue(sqs, queue_url, json.dumps(chunk)))

# Run the asyncio main function
asyncio.run(main())

'''
if __name__ == "__main__":
    sqs = boto3.client('sqs')
    queue_url = os.getenv("AWS_QUEUE_URL")

    items = load_files('./data')

    texts = []
    for item in items:
        text = item["text"]
        texts.append(text)

    chunks = chunk_list(texts, 100)
    for chunk in chunks:
        send_message_to_fifo_queue(sqs, queue_url, json.dumps(chunk))
'''