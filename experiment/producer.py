import stomp
import json
import time

# Producer sends messages to a queue
def send_messages():
    conn = stomp.Connection([("localhost", 61616)])
    conn.connect("artemis", "artemis", wait=True)
    
    #messages = [{"id": 1, "content": "Hello, World!"}, {"id": 2, "content": "Goodbye, World!"}]
    messages = [{"text": "2024-07-13T15:21:52.644950, info, db_service, 192.168.1.1, database connection closed", "metadata": {"timestamp": "2024-07-13T15:21:52.644950", "log_level": "info", "application": "db_service", "ip": "192.168.1.1", "message": "database connection closed"}}, {"text": "2024-07-13T15:21:52.644950, info, db_service, 192.168.1.1, database connection closed", "metadata": {"timestamp": "2024-07-13T15:21:52.644950", "log_level": "info", "application": "db_service", "ip": "192.168.1.1", "message": "database connection closed"}}]
    conn.send(body=json.dumps(messages), destination="queue/embedding")
    
    print("Messages sent to queue/embedding")
    time.sleep(2)
    conn.disconnect()


send_messages()