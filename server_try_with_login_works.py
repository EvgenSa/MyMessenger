import socket
import threading
import json
import base64
import os.path

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverRunning = True
ip = str(socket.gethostbyname(socket.gethostname()))
port = 1234
users_store = "passwords.json"

clients = {}

s.bind((ip, port))
s.listen()
print('Server Ready...')
print('Ip Address of the Server::%s' % ip)

def write_json(data, filename=users_store): 
    with open(filename,'w') as f: 
        json.dump(data, f) 

def createUsers():
   with open(users_store, "w") as f:
        json.dump({'users': []}, f)

def addNewUser(username, password):
    with open(users_store) as json_file: 
        data = json.load(json_file) 
        temp = data['users']
        temp.append({'username': username, 'password': password})
    write_json(data)  

def doesUsernameExists(username):
    with open(users_store) as json_file:
        data = json.load(json_file)
        for user in data['users']:
            if user['username'] == username:
                return True
    return False

def validateAndLogin(username, password):
    with open(users_store) as json_file:
        data = json.load(json_file)
        for user in data['users']:
           if user['username'] == username and base64.b64decode(user['password']).decode('utf-8') == password:
               return True
    return False

def handleCommands(uname, client, clients, keys, help, msg):
    response = 'Number of People Online\n'
    found = False
    if '@chatlist' in msg:
        clientNo = 0
        for name in keys:
            clientNo += 1
            response = response + str(clientNo) + '::' + name + '\n'
        client.send(response.encode('utf-8'))
    elif '@help' in msg:
        client.send(help.encode('utf-8'))
    elif '@broadcast' in msg:
        msg = msg.replace('@broadcast', '')
        for k, v in clients.items():
            v.send(msg.encode('utf-8'))
    elif '@quit' in msg:
        response = 'Stopping Session and exiting...'
        client.send(response.encode('utf-8'))
        if uname != "":
            clients.pop(uname)
            print(uname + ' has been logged out')
        clientConnected = False
    else:
        for name in keys:
            if ('@' + name) in msg:
                msg = msg.replace('@' + name, '')
                clients.get(name).send(msg.encode('utf-8'))
                found = True
        if (not found):
            client.send('Trying to send message to invalid person.'.encode('utf-8'))

def handleRegister(client, username, password):
    if doesUsernameExists(username):
        client.send("\nLogin name already exist!\n".encode('utf-8'))
        return ""
    else:
        enc_password = base64.b64encode(bytes(password.encode('utf-8'))).decode('utf-8')
        addNewUser(username, enc_password)
        client.send('Welcome to Messenger. Type @help to know all the commands'.encode('utf-8'))
        if client not in clients:
            clients[username] = client
        return username
    
def handleLogin(client, username, password):
    isValid = validateAndLogin(username, password)
    response = "\nWelcome to Messenger. Type @help to know all the command\n" if isValid else "\nUser doesn't exist or wrong password!\n"
    client.send(response.encode('utf-8'))
    if isValid:
       if client not in clients:
           clients[username] = client
       return username
    else: return ""

def handleClient(client):
    clientConnected = True
    keys = clients.keys()
    help = 'There are four commands in Messenger\n1::@chatlist=>gives you the list of the people currently online\n2::@quit=>To end your session\n3::@broadcast=>To broadcast your message to each and every person currently present online\n4::Add the name of the person at the end of your message preceded by @ to send it to particular person'
    uname = ""
    while clientConnected:
        try:
            data = client.recv(1024)
            msg = json.loads(data)
            if msg['type'] == "COMMAND":
                handleCommands(uname, client, clients, keys, help, msg['command'])
            elif msg['type'] == "REGISTER":
                uname = handleRegister(client, msg['username'], msg['password'])
            elif msg['type'] == "LOGIN":
                uname = handleLogin(client, msg['username'], msg['password'])
            
        except Exception as e:
            print(str(e))
            if uname != "":
                clients.pop(uname)
                print(uname + ' has been logged out')
            clientConnected = False


while serverRunning:
    client, address = s.accept()
    
    if os.path.isfile(users_store) == False:
        createUsers()
    threading.Thread(target=handleClient, args=(client,)).start()
