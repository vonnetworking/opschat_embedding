import boto3
import uuid
import os
import json
import asyncio
from activemq_util import ActiveMQ

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

async def send_message(activemq, queue, message_body):
    try:
        activemq.write(message_body, queue_name=queue)
        print(f"Message sent to queue: {queue}")
    except Exception as e:
        print(f"Failed to send message: {e}")


async def main():
    local = False
    embedding_queue = os.getenv("EMBEDDING_QUEUE")

    # Connect to ActiveMQ
    try:
        activemq = ActiveMQ(host='localhost', port=61616, username='artemis', password='artemis')
        activemq.connect()
    except Exception as e:
        print(f"Failed to connect to ActiveMQ: {e}")
        return
    
    items = load_files('./data')

    chunks = chunk_list(items, 1000)
    async with asyncio.TaskGroup() as tg:
        if local:
            for chunk in chunks:
                queue_name = embedding_queue + "/unknown-host"
                tg.create_task(send_message(activemq, queue_name, json.dumps(chunk)))
        else:
            i = 0
            for chunk in chunks:
                queue_name = embedding_queue + "/opschat-ingestion-" + str(i) 
                tg.create_task(send_message(activemq, queue_name, json.dumps(chunk)))
                i += 1
                if i > 9:
                    i = 0

    input("Press Enter to end this program...")
    activemq.disconnect()

# Run the asyncio main function
asyncio.run(main())