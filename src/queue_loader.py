import boto3
import uuid
import glob
import os
import re
import shutil
import json
import hashlib
import time
import asyncio
from activemq_util import ActiveMQ

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
    
    items = []
    for file in files:
        file_path = os.path.join(subdirectory, file)
        with open(file_path, 'r') as f:
            for line in f:
                if file_path.find("txt"):
                    items.append(process_program_logs(line))
                else:
                    items.append(process_change_tickets(line))
    return items

def chunk_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

async def send_message(activemq, queue, message_body):
    try:
        activemq.write(message_body, queue_name=queue, headers={'destination-type': 'ANYCAST'})
        # print(f"Message sent to queue: {queue}")
    except Exception as e:
        print(f"Failed to send message: {e}")


def grep_files(pattern, file_pattern):
    results = list()
    for filename in glob.glob(file_pattern):
        with open(filename) as f:
            for line in f:
                if re.search(pattern, line):
                    results.append(line)
    return results

async def main():

    
    embedding_queue = os.getenv("EMBEDDING_QUEUE")
    chunk_size = int(os.getenv("EMBEDDING_CHUNK_SIZE", 1024))
    log_dir = os.getenv("EMBEDDING_LOG_DIR", "/tmp/logs") 
    
    print("Starting Queue Load...")
    starting_ts = time.time()
    # Connect to ActiveMQ
    try:
        activemq = ActiveMQ(host='localhost', port=61616, username='artemis', password='artemis')
        activemq.connect()
    except Exception as e:
        print(f"Failed to connect to ActiveMQ: {e}")
        return
    
    items = load_files('./data')

    chunks = chunk_list(items, chunk_size)
    
    async with asyncio.TaskGroup() as tg:
        for chunk in chunks:
            queue_name = embedding_queue 
            tg.create_task(send_message(activemq, queue_name, json.dumps(chunk)))
        last_checksum = sha256_string(json.dumps(chunk))
    starting_ts = time.time()
    print(f"All expected log chunks sent to queue...starting timer")
    print(f"Waiting for message to process: {last_checksum}")
    message_processed = False
    while not message_processed:
        message_processed = grep_files(last_checksum, f"{log_dir}/*.log")
   
    ending_ts = time.time()
    total_runtime = ending_ts - starting_ts
    print(f"EXECUTION COMPLETE; RECORDS: {len(items)}; RUNTIME: {total_runtime}")
    activemq.disconnect()

# Run the asyncio main function
asyncio.run(main())
