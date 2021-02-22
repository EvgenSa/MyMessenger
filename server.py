from socket import *
import select

class Server():
    def __init__(self, address, port):
        self.address = address
        self.port = port

    def read_requests(self, r_client, all_clients):
        responses = []
        for sock in r_client:
            try:
                data = sock.recv(1000000).decode('utf-8')
                responses.append(data)
            except:
                print("Client has dropt")
                all_clients.remove(sock)
        return (responses)


    def write_respons(self, requests, w_client, all_clients):
        for sock in w_client:
            try:
                for resp in requests:
                    sock.send(resp.encode('utf-8'))
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
            except OSError: pass
            else:
                print("Request to connection was received from %s" % str(addr))
                clients.append(conn)
            finally:
                wait = 10
                r = []
                w = []
                try:
                    r, w, e = select.select(clients, clients, [], wait)
                except Exception: pass

                requests = self.read_requests(r, clients)
                if requests:
                    self.write_respons(requests, w, clients)


if __name__ == '__main__':
    server = Server('localhost', 1000)
    server.mainloop_start()


