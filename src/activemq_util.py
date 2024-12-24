import stomp
import json
import time
import logging
import uuid

class ActiveMQ:
    def __init__(self, host='localhost', port=61613, username='admin', password='admin'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.conn = None
        self.listener_id = uuid.uuid4()

    def connect(self):
        self.conn = stomp.Connection([(self.host, self.port)])
        self.conn.connect(self.username, self.password, wait=True)

    def disconnect(self):
        if self.conn:
            self.conn.disconnect()

    def write(self, messages, queue_name, headers={}):
        if not self.conn:
            raise Exception("Not connected to the broker. Call connect() first.")
        
        expiration_time = int((time.time() + 60) * 1000)  # Expire in 60 seconds
        headers['expiration'] = expiration_time

        self.conn.send(body=messages, destination=queue_name, headers=headers, persistent='true')
        logging.info(f"Messages sent successfully to {queue_name}.")

    def ack(self, frame):
        try:
            self.conn.ack(frame.headers['message-id'], frame.headers['subscription'])
        except:
            pass

    def read(self, queue_name, on_message_callback):
        if not self.conn:
            raise Exception("Not connected to the broker. Call connect() first.")
        
        listener = self.MessageListener(on_message_callback)
        self.conn.set_listener('', listener)
        self.conn.subscribe(destination=queue_name, id=self.listener_id, ack='auto')
        logging.info(f"Subscribed to {queue_name}. Waiting for messages...")
        while True:
            try:
                if not self.conn.is_connected():
                    raise Exception("Lost connection to the broker.")
                time.sleep(60)  # Keep the script running to listen for messages
            except Exception as e:
                logging.error(f"Error in listener: {e}")
                break

    class MessageListener(stomp.ConnectionListener):
        def __init__(self, on_message_callback):
            self.on_message_callback = on_message_callback

        def on_error(self, frame):
            logging.info(f"Received error: {frame}")

        def on_message(self, frame):
            try:
                # Parse the batched JSON message
                self.on_message_callback(frame)
            except json.JSONDecodeError as e:
                logging.info(f"Error decoding JSON: {e}")
