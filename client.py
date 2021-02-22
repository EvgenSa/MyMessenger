from socket import *
import datetime
import json


class Client():
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.nick_name = ''
        self.readMode = False

    def client_chat(self):
        self.nick_name = input("Input your nick or name in chat: ")
        if "r" == input('If you want read mode input r: '):
            self.readMode = True
        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.connect((self.address, self.port))
            while True:
                if self.readMode:
                    data_json = sock.recv(1000000)
                    data = json.loads(data_json)
                    print("{} - {} : {}". format(data['time'], data['name'], data['message']))

                else:
                    text = input('Input your message: ')
                    message = {'time': datetime.datetime.now().strftime("%H:%M:%S"),
                               'name': self.nick_name,
                               'message': text}
                    if text == 'exit':
                        break
                    sock.send(json.dumps(message).encode('utf-8'))

if __name__ == '__main__':
    client = Client('localhost', 1000)
    client.client_chat()