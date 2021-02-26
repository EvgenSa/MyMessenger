import socket
import threading
import sys
import json

class Registartion:

    def buildActionMessage(self, text):
        return {'command': text, 'type': "COMMAND"}

    def buildUserLoginMessage(self, username, password, msg_type):
        return {'username': username, 'password': password, 'type': msg_type}

    def loginOrRegister(self, status, uname, password, sock):
        self.send(self.buildUserLoginMessage(uname, password, "REGISTER" if status == "n" else "LOGIN"), sock)

    def send(self, message, sock):
        sock.send(json.dumps(message).encode('utf-8'))


class Client:


    def receiveMsg(self, sock):
        serverDown = False
        while True and (not serverDown):
            try:
                msg = sock.recv(1024).decode('utf-8')
                print(msg)
            except:
                print('Server is Down. You are now Disconnected. Press enter to exit...')
                serverDown = True

    def chat(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 1234

        ip = input('Enter the IP Address::')
        s.connect((ip, port))

        status = input("Are you a registered user?")
        uname = input("Enter user name::")
        password = input("Enter password::")

        Registartion().loginOrRegister(status, uname, password, s)

        clientRunning = True
        threading.Thread(target=self.receiveMsg, args = (s,)).start()

        while clientRunning:
            tempMsg = input()
            msg = uname + '>>' + tempMsg
            registratiuon_manager = Registartion()
            if '@quit' in msg:
                clientRunning = False
                registratiuon_manager.send(registratiuon_manager.buildActionMessage('@quit'), s)
            else:
                registratiuon_manager.send(registratiuon_manager.buildActionMessage(msg), s)


if __name__ == '__main__':

    client = Client()
    client.chat()

