from socket import *
import datetime
import json
from threading import Thread


class SockHandler:
    def __init__(self, sock):
        self.sock = sock
        self.is_alive = False

    def stop(self):
        self.is_alive = False


class ConsoleHandler(SockHandler):
    _name = ''

    def __init__(self, sock, name):
        super().__init__(sock)
        self._name = name

    def __call__(self):
        while True:
            text = input('Input your message: ')
            if text == 'exit':
                break
            message = {'time': datetime.datetime.now().strftime("%H:%M:%S"),
                       'name': self._name,
                       'message': text}
            self.sock.send(json.dumps(message).encode('utf-8'))


class Client():
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.name = ''

    def client_chat(self):
        self.name = input("Input your nick or name in chat: ")
        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.connect((self.address, self.port))
            sender = ConsoleHandler(sock=sock, name=self.name)
            th_sender = Thread(target=sender)
            th_sender.daemon = True
            th_sender.start()
            while True:
                data = sock.recv(1000000).decode('utf-8')
                print(data)

if __name__ == '__main__':
    client = Client('localhost', 8000)
    client.client_chat()