import json
from socket import *
import select


class User:
    def __init__(self, username: str, user_socket):
        self.username = username
        self.user_sockets = [user_socket]

    def __hash__(self):
        return hash(self.username)


class KnownUsers:
    def __init__(self):
        self.knows_users = {}

    def is_user_exist(self, username: str) -> bool:
        return username in self.knows_users

    def _get_user(self, username: str) -> User:
        if self.is_user_exist(username):
            return self.knows_users[username]

    def _save_user(self, username: str, user_socket):
        if self.is_user_exist(username):
            self.knows_users[username].user_sockets.append(user_socket)
        else:
            self.knows_users[username] = User(username, user_socket)

    def get_user(self, username: str, user_socket) -> User:
        self._save_user(username, user_socket)
        return self._get_user(username)

    def find_user(self, username: str) -> User or None:
        return self._get_user(username)


class Message:
    def __init__(
            self, author: User, content: str, message_sending_time: str, msg_type: str = 'broadcast',
            another_user: User = None
    ):
        self.author = author
        self.content = content
        self.message_sending_time = message_sending_time
        self.msg_type = msg_type
        self._validate_msg_type()
        self.another_user = another_user

    def _validate_msg_type(self):
        available_msg_types = ['broadcast', 'private']
        if self.msg_type not in available_msg_types:
            raise TypeError(f'This type of message are not available. Available {available_msg_types}')

    def __str__(self):
        return f"{self.message_sending_time} | {self.author.username} - {self.content}"


class Server:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.known_users = KnownUsers()

    def read_requests(self, r_client, all_clients):
        responses = []
        for sock in r_client:
            try:
                data = sock.recv(1000000).decode('utf-8')
                responses.append(data)
            except:
                print("Client has dropt")
                all_clients.remove(sock)
        return responses

    def write_respons(self, requests, w_client, all_clients):
        for sock in w_client:
            try:
                sock.send(requests.encode('utf-8'))
            except:
                print('Client has dropt')
                sock.close()
                all_clients.remove(sock)

    def mainloop_start(self):
        clients = []

        s = socket(AF_INET, SOCK_STREAM)
        s.bind((self.address, self.port))
        s.listen(5)
        s.settimeout(0.2)

        while True:
            try:
                conn, addr = s.accept()
            except OSError:
                pass
            else:
                print("Request to connection was received from %s" % str(addr))
                clients.append(conn)
            finally:
                wait = 10
                r = []
                w = []
                try:
                    r, w, e = select.select(clients, clients, [], wait)
                except Exception:
                    pass

                requests = self.read_requests(r, clients)
                if requests:
                    last_request = json.loads(requests[-1])
                    author_socket = clients[-1]
                    author_username = last_request.get('name')
                    author = self.known_users.get_user(author_username, author_socket)

                    author_msg_content = last_request.get('message')
                    author_msg_time = last_request.get('time')
                    # Надо как-то эти два метода скомбинировать в зависимости от типа отправки сообщения
                    # =============================================
                    # Example with broadcast msg. Remove after

                    msg = Message(author, author_msg_content, author_msg_time)

                    # =============================================
                    # Example with private msg. Remove after

                    receiver = self.known_users.find_user('Fish')
                    msg = Message(
                        author, author_msg_content, author_msg_time,
                        msg_type='private', another_user=receiver
                    )
                    # =============================================

                    if msg.msg_type == 'broadcast':
                        self.send_broad_cast_msg(msg, w, clients)
                    elif msg.msg_type == 'private':
                        self.send_private_msg(msg, w)

    def send_private_msg(self, msg, w):
        self.write_respons(str(msg), msg.another_user.user_sockets, w)

    def send_broad_cast_msg(self, msg, w, clients):
        self.write_respons(str(msg), w, clients)


if __name__ == '__main__':
    server = Server('localhost', 8000)
    server.mainloop_start()
