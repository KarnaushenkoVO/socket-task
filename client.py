""" Defines socket client class """

import json
import logging
import socket
import uuid
from time import sleep, time

DELAY = 1
CLIENT_MESSAGE_TEMPLATE = 'Client {}: received from server {}'


class SocketClient:
    """ TCP socket client, which send message with client's id and timestamp, print received """

    def __init__(self, ip, port, close_event):
        """ Initialize socket client

        ip (str): ip address of server
        port (int): port number of server
        close_event (threading.Event): event to inform about closing
        """

        self.socket = socket.socket()
        self.socket.connect((ip, port))
        self.close = close_event
        self._id = str(uuid.uuid4())

    def start(self):
        """ Starts client to form and send message to server with delay. Prints server's answers. """

        while not self.close.isSet():
            data = json.dumps({'id': self._id, 'timestamp': self.timestamp()})
            self.socket.send(data.encode())
            sleep(DELAY)
            try:
                data = json.loads(self.socket.recv(1024).decode())
            except Exception:
                data = None
            if data is not None:
                logging.info(CLIENT_MESSAGE_TEMPLATE.format(data.get('id'), data.get('timestamp')))

        self.shutdown()

    @staticmethod
    def timestamp():
        """ Generates integer timestamp """
        return int(time())

    def shutdown(self):
        """ Closes all sockets connections """
        self.socket.close()
