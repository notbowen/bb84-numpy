class SQPMessage:
    def __init__(self, msg=None) -> None:
        self.method = ""
        self.target = ""
        self.sender = ""

        self.data = ""

        if msg:
            self.parse(msg)

    def create(self, method: str, target: str, sender: str, data: str) -> None:
        self.method = method
        self.target = target
        self.sender = sender
        self.data = data

    def parse(self, msg: bytes) -> None:
        msg_decoded = msg.decode()
        header, self.data = msg_decoded.split("\n\n")

        dest_info, self.sender = header.splitlines()
        self.method, self.target = dest_info.rsplit(" ", 1)

    def to_bytes(self) -> bytes:
        return f"{self.method} {self.target}\n{self.sender}\n\n{self.data}".encode()
