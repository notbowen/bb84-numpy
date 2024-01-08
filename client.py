import threading
import socket
import sys
import random

from protocol import SQPMessage
from quantum.qkd import QKD


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

        self.qkd_client = QKD()

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
        self.send_message("RES GET", msg.sender, self.qkd_client.send())

    def handle_basis(self, msg: SQPMessage) -> None:
        recv_basis = list(map(int, msg.data))
        same_indices = [str(idx) for idx, basis in enumerate(zip(self.qkd_client.basis, recv_basis)) if
                        basis[0] == basis[1]]
        self.shared_keys[msg.sender] = ""
        for idx in same_indices:
            self.shared_keys[msg.sender] += str(self.qkd_client.bits[int(idx)])
        self.send_message("RES BASIS", msg.sender, ",".join(same_indices))

    def handle_check(self, msg: SQPMessage) -> None:
        data = msg.data.splitlines()
        indices = data[0].split(",")
        bits = data[1].split(",")

        indices = list(map(int, indices))
        bits = list(map(int, bits))

        result = self.qkd_client.check_bits_at_indices(bits, indices, 1)
        self.send_message("RES CHECK", msg.sender, str(result))

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
        if response.method == "ERR GET":
            cprint("Error: " + response.data)
            return
        self.qkd_client.recv(response.data)
        cprint("Received qubits")
        cprint("Current state: " + "".join(map(str, self.qkd_client.bits)))

        self.send_message("BASIS", target, "".join(map(str, self.qkd_client.basis)))
        response = self.get_response_of_type("BASIS")
        if response.method == "ERR BASIS":
            cprint("Error: " + response.data)
            return
        cprint("Common base indices: " + response.data)

        basis = response.data.split(",")
        self.shared_keys[target] = ""
        for idx in basis:
            self.shared_keys[target] += str(self.qkd_client.bits[int(idx)])
        cprint("Final shared key: " + self.shared_keys[target])

        indices = [random.randint(0, self.qkd_client.length - 1) for _ in range(4)]
        bits = [int(self.qkd_client.bits[idx]) for idx in indices]
        self.send_message("CHECK", target, ",".join(map(str, indices)) + "\n" + ",".join(map(str, bits)))

        response = self.get_response_of_type("CHECK")
        if response.method == "ERR CHECK":
            cprint("Error: " + response.data)
            return
        cprint("Check result: " + response.data)

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
            if target == hostname:
                cprint("Target cannot be yourself!")
                continue
            client.begin_qkd(target)

        elif cmd == "EXIT":
            client.disconnect()
            sys.exit(0)
