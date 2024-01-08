import socket
import threading
import argparse
from loguru import logger

from protocol import SQPMessage
from quantum.qkd import QKD


class SQPServer:
    def __init__(self, host="0.0.0.0", port=8484, eavesdrop=False):
        self.host = host
        self.port = port

        self.eavesdrop = eavesdrop
        self.qkd_client = QKD()

        self.connections = {}

    def disconnect(self, target: str) -> None:
        if target not in self.connections:
            return

        self.connections.pop(target)
        logger.info(f"{target} disconnected")

    def handle_connection(self, hostname: str, c: socket.socket):
        while True:
            try:
                msg = c.recv(1024)
            except:
                c.close()
                self.disconnect(hostname)
                return

            if not msg:
                continue

            message = SQPMessage(msg)

            if message.method == "DC":
                self.disconnect(hostname)
                return

            if message.method == "RES GET" and self.eavesdrop:
                logger.info(f"Eavesdropping on GET RES request from {hostname}")
                self.qkd_client.recv(message.data)
                message.data = self.qkd_client.send()

            try:
                self.connections[message.target].send(message.to_bytes())
                logger.debug(f"{message.method} request sent to {message.target}")
            except KeyError:
                error = SQPMessage()
                error.create("ERR " + message.method, hostname, "server", "Host not found!")
                logger.debug(f"ERR {message.method} request sent to {hostname}")
                c.send(error.to_bytes())

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)

        logger.info(f"Server started at {self.host}:{self.port}")

        while True:
            c, addr = s.accept()

            hostname = c.recv(64).decode().strip()
            if hostname in self.connections:
                message = f"Hostname {hostname} is already in use!"

                error = SQPMessage()
                error.create("ERR", hostname, "server", message)
                c.send(error.to_bytes())

                logger.error(message)
                continue

            self.connections[hostname] = c
            logger.info(f"Connection from: {addr[0]}:{addr[1]} ({hostname})")

            message = f"RES {hostname}\nserver\n\nOK"
            c.send(message.encode())

            thread = threading.Thread(
                target=self.handle_connection, args=(hostname, c))
            thread.daemon = True
            thread.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--eavesdrop", action="store_true", help="Eavesdrop on the qubits")
    args = parser.parse_args()

    server = SQPServer(eavesdrop=args.eavesdrop)
    server.start()
