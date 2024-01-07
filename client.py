import threading
import socket
import sys

from protocol import SQPMessage


def cprint(msg: str) -> None:
    print(f"\r{msg}\n> ", end="")


class SQPClient:
    def __init__(self, hostname: str) -> None:
        assert len(hostname) <= 64
        self.hostname = hostname
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.shared_keys = {}
        self.listening_thread = None
        self.response_queue = []

    def connect(self, host: str, port: int):
        self.socket.connect((host, port))

        padded_hostname = self.hostname + " " * (64 - len(self.hostname))
        self.socket.send(padded_hostname.encode())
        msg = self.socket.recv(1024)

        protocol = SQPMessage(msg)

        if protocol.method == "ERR":
            print(protocol.data)
            sys.exit(1)

        print(f"Connected to {host}:{port}")

    def send_message(self, method: str, target: str, data: str) -> None:
        message = SQPMessage()
        message.create(method, target, self.hostname, data)

        try:
            self.socket.send(message.to_bytes())
        except ConnectionResetError:
            print("Server has been shut down.")
            sys.exit(0)

    def receive_message(self) -> bytes:
        try:
            msg = self.socket.recv(1024)
            return msg
        except ConnectionResetError:
            print("Server has been shut down.")
            sys.exit(0)
        except OSError:
            pass

    def handle_message(self, msg: SQPMessage) -> None:
        if msg.method == "GET":
            self.handle_get(msg)
        elif msg.method == "BASIS":
            self.handle_basis(msg)
        elif msg.method == "CHECK":
            self.handle_check(msg)
        elif msg.method[0:3] == "RES" or msg.method[0:3] == "ERR":
            self.handle_res(msg)

        # Invalid methods are dropped

    def handle_get(self, msg: SQPMessage) -> None:
        self.send_message("RES GET", msg.sender, "response message")

    def handle_basis(self, msg: SQPMessage) -> None:
        pass

    def handle_check(self, msg: SQPMessage) -> None:
        pass

    def handle_res(self, msg: SQPMessage) -> None:
        self.response_queue.append(msg)

    def get_response_of_type(self, method: str) -> SQPMessage:
        while True:
            for msg in self.response_queue:
                if msg.method == "RES " + method:
                    self.response_queue.remove(msg)
                    return msg
                elif msg.method == "ERR " + method:
                    self.response_queue.remove(msg)
                    return msg

    def listen_loop(self) -> None:
        while True:
            msg = self.receive_message()
            if not msg:
                continue

            message = SQPMessage(msg)
            self.handle_message(message)

    def start_listening(self) -> None:
        self.listening_thread = threading.Thread(target=self.listen_loop)
        self.listening_thread.daemon = True
        self.listening_thread.start()

    def begin_qkd(self, target: str) -> None:
        self.send_message("GET", target, "")
        response = self.get_response_of_type("GET")
        if response.method == "ERR":
            cprint("Error: " + response.data)
            return
        cprint(response.data)

    def disconnect(self) -> None:
        self.send_message("DC", "server", "")
        self.socket.close()


if __name__ == "__main__":
    hostname = input("Enter hostname: ")

    client = SQPClient(hostname)
    client.connect("127.0.0.1", 8484)
    client.start_listening()

    print("> ", end="")
    while True:
        cmd = input("")

        if cmd.startswith("CONNECT"):
            target = cmd.split(" ")[1]
            client.begin_qkd(target)

        elif cmd == "EXIT":
            client.disconnect()
            sys.exit(0)
