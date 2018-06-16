""" Starts server and clients in different threads and shutdown all after 10 seconds """

import logging
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from time import sleep

from client import SocketClient
from server import SocketServer

logging.basicConfig(level=logging.DEBUG, format='%(message)s')

HOST = '127.0.0.1'
PORT = 53
WORK_TIME = 10
CLIENT_NUMBERS = 5

if __name__ == '__main__':
    # Defines event which will inform about main process terminating
    close_event = threading.Event()

    # Creates instance of SocketServer and starts it in daemon thread
    server = SocketServer(HOST, PORT, close_event, CLIENT_NUMBERS)
    server_thread = threading.Thread(target=server.run_server, daemon=True)
    server_thread.start()

    # Creating thread pool with socket clients
    with ThreadPoolExecutor(max_workers=CLIENT_NUMBERS) as executor:
        for _ in range(CLIENT_NUMBERS):
            client = SocketClient(HOST, PORT, close_event)
            executor.submit(client.start)

        # Waits required time of work
        sleep(WORK_TIME)
        # Informs all threads about terminating
        close_event.set()
        # Waits until server close all connections and exits
        server_thread.join()
        # Close program with status code zero
        sys.exit(0)
