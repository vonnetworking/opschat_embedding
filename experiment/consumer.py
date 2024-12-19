import stomp
import json

# Consumer listens for messages from the same queue
class MyListener(stomp.ConnectionListener):
    def on_message(self, frame):
        messages = json.loads(frame.body)
        for message in messages:
            print(f"Received message: {message}")

def consume_messages():
    conn = stomp.Connection([("localhost", 61616)])
    conn.set_listener("", MyListener())
    conn.connect("artemis", "artemis", wait=True)
    
    conn.subscribe(destination="queue/embedding", id=1, ack="auto")
    print("Subscribed to queue/embedding. Waiting for messages...")
    
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        conn.disconnect()

consume_messages()