import socket
import threading
import json
import base64
import os.path


class Users:
    PASSWORDS_FILENAME = "passwords.json"

    def initialise_users(self):
        if os.path.isfile(self.PASSWORDS_FILENAME) == False:
            self.create_users()

    def create_users(self):
       with open(self.PASSWORDS_FILENAME, "w") as f:
            json.dump({'users': []}, f)
    
    def add_new_user(self, username, password):
        with open(self.PASSWORDS_FILENAME) as json_file:
            data = json.load(json_file)
            temp = data['users']
            temp.append({'username': username, 'password': password})
        self.write_json(data)

    def is_user_exist(self, username):
        with open(self.PASSWORDS_FILENAME) as json_file:
            data = json.load(json_file)
            for user in data['users']:
                if user['username'] == username:
                    return True
        return False

    def validate_and_login(self, username, password):
        with open(self.PASSWORDS_FILENAME) as json_file:
            data = json.load(json_file)
            for user in data['users']:
               if user['username'] == username and base64.b64decode(user['password']).decode('utf-8') == password:
                   return True
        return False
    
    def write_json(self, data, filename=PASSWORDS_FILENAME):
        with open(filename, 'w') as f:
            json.dump(data, f)


class ServerHandlers:
    def __init__(self, clients, users, client):
        self.clients = clients
        self.users = users
        self.client = client

    def client_handler(self):
        clientConnected = True
        keys = self.clients.keys()
        help = 'There are four commands in Messenger\n1::@chatlist=>gives you the list of the people currently online\n2::@quit=>To end your session\n3::@broadcast=>To broadcast your message to each and every person currently present online\n4::Add the name of the person at the end of your message preceded by @ to send it to particular person'
        uname = ""
        while clientConnected:
            try:
                data = self.client.recv(1024)
                msg = json.loads(data)
                if msg['type'] == "COMMAND":
                    self.command_handler(uname, keys, help, msg['command'])
                elif msg['type'] == "REGISTER":
                    uname = self.register_handler(msg['username'], msg['password'])
                elif msg['type'] == "LOGIN":
                    uname = self.login_handler(msg['username'], msg['password'])

            except Exception as e:
                print(str(e))
                if uname != "":
                    self.clients.pop(uname)
                    print(uname + ' has been logged out')
                clientConnected = False

    def command_handler(self, uname, keys, help, msg):
        response = 'Number of People Online\n'
        found = False
        if '@chatlist' in msg:
            clientNo = 0
            for name in keys:
                clientNo += 1
                response = response + str(clientNo) + '::' + name + '\n'
            self.client.send(response.encode('utf-8'))
        elif '@help' in msg:
            self.client.send(help.encode('utf-8'))
        elif '@broadcast' in msg:
            msg = msg.replace('@broadcast', '')
            for k, v in self.clients.items():
                v.send(msg.encode('utf-8'))
        elif '@quit' in msg:
            response = 'Stopping Session and exiting...'
            self.client.send(response.encode('utf-8'))
            if uname != "":
                self.clients.pop(uname)
                print(uname + ' has been logged out')
        else:
            for name in keys:
                if ('@' + name) in msg:
                    msg = msg.replace('@' + name, '')
                    self.clients.get(name).send(msg.encode('utf-8'))
                    found = True
            if (not found):
                self.client.send('Trying to send message to invalid person.'.encode('utf-8'))

    def register_handler(self, username, password):
        if self.users.is_user_exist(username):
            self.client.send("\nLogin name already exist!\n".encode('utf-8'))
            return ""
        else:
            enc_password = base64.b64encode(bytes(password.encode('utf-8'))).decode('utf-8')
            self.users.add_new_user(username, enc_password)
            self.client.send('Welcome to Messenger. Type @help to know all the commands'.encode('utf-8'))
            if self.client not in self.clients:
                self.clients[username] = self.client
            return username

    def login_handler(self, username, password):
        isValid = self.users.validate_and_login(username, password)
        response = "\nWelcome to Messenger. Type @help to know all the command\n" if isValid else "\nUser doesn't exist or wrong password!\n"
        self.client.send(response.encode('utf-8'))
        if isValid:
           if self.client not in self.clients:
               self.clients[username] = self.client
           return username
        else:
            return ""


class Server:
    def __init__(self, server_port: int):
        self.is_server_work = None
        self.server_port = server_port
        self.clients = {}
        self.users = Users()

    def server_socket(self) -> socket.socket:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @property
    def server_ip(self) -> str:
        return str(socket.gethostbyname(socket.gethostname()))

    def run(self):
        server_socket = self.server_socket()
        server_socket.bind((self.server_ip, self.server_port))
        server_socket.listen()
        print('Server ready and wait for users')
        print('Ip Address of the Server::%s' % self.server_ip)

        self.accept_socket(server_socket)

    def accept_socket(self, server_socket):
        while True:
            client, address = server_socket.accept()

            self.users.initialise_users()

            server_handler = ServerHandlers(self.clients, self.users, client)
            threading.Thread(target=server_handler.client_handler).start()


if __name__ == '__main__':
    server = Server(1234)
    server.run()
