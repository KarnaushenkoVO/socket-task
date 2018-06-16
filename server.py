""" Defines socket server class """

import json
import logging
import socket
import threading
from time import time

SERVER_MESSAGE_TEMPLATE = 'Server: Received from user: {}: {}'


class SocketServer:
    """ TCP socket server, which receives message with user's id and timestamp, print received, and answers """

    def __init__(self, ip, port, close_event, max_clients=5):
        """ Initialize socket client

        ip (str): ip address of server
        port (int): port number of server
        close_event (threading.Event): event to inform about closing
        max_client (int): number of expected clients
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip, port))
        self.close = close_event
        self.max_clients = max_clients
        self.connections = []

    def run_server(self):
        """ Method to start server accept client connections and delegates client processing """

        logging.info('Server: Starting connections')
        self.socket.listen(self.max_clients)

        # This is required to release server after all connections established
        for _ in range(self.max_clients):
            client_socket, address = self.socket.accept()
            if client_socket not in self.connections:
                self.connections.append(client_socket)
            self.serve_client(client_socket)

        # Waiting until appropriate will be set
        while not self.close.isSet():
            pass
        self.shutdown()

    def serve_client(self, client_socket):
        """ Runs thread which process client's messages

        client_socket (socket.socket): client's socket
        """

        def client_callback(connection, close):
            """ Process client messages

            connection (socket.socket): client's socket
            close (threading.Event): event to inform about closing
            """

            # Wait until there is no event about server terminating
            while not close.isSet():
                try:
                    data = json.loads(connection.recv(1024).decode())
                except Exception:
                    data = None
                if data is not None:
                    logging.info(SERVER_MESSAGE_TEMPLATE.format(data.get('id'), data.get('timestamp')))

                    # Updates timestamp and send back message
                    data['timestamp'] = self.timestamp()
                    data = json.dumps(data)
                    connection.send(data.encode())

        # Creates and starts thread with function which will process client's messages as a target
        client_thread = threading.Thread(target=client_callback, daemon=True, args=(client_socket, self.close))
        client_thread.start()

    @staticmethod
    def timestamp():
        """ Generates integer timestamp """
        return int(time())

    def shutdown(self):
        """ Closes all connections """
        logging.info('Server: Closing connections')
        for connection in self.connections:
            connection.close()
