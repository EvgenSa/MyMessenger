import socket
import threading
import sys
import json

def buildActionMessage(text):
    return {'command': text, 'type': "COMMAND"}

def buildUserLoginMessage(username, password, msg_type):
    return {'username': username, 'password': password, 'type': msg_type}

def loginOrRegister(status, uname, password, sock):
    send(buildUserLoginMessage(uname, password, "REGISTER" if status == "n" else "LOGIN"), sock)

def send(message, sock):
    sock.send(json.dumps(message).encode('utf-8'))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 1234


ip = input('Enter the IP Address::')
s.connect((ip, port))

status = input("Are you a registered user?")
uname = input("Enter user name::")
password = input("Enter password::")

loginOrRegister(status, uname, password, s)

clientRunning = True

def receiveMsg(sock):
    serverDown = False
    while clientRunning and (not serverDown):
        try:
            msg = sock.recv(1024).decode('utf-8')
            print(msg)
        except:
            print('Server is Down. You are now Disconnected. Press enter to exit...')
            serverDown = True
        
             

threading.Thread(target = receiveMsg, args = (s,)).start()
while clientRunning:
    tempMsg = input()
    msg = uname + '>>' + tempMsg
    if '@quit' in msg:
        clientRunning = False
        send(buildActionMessage('@quit'), s)
    else:
        send(buildActionMessage(msg), s)
