import json
import base64
users = {}
status = ""

def write_in_file(data):
    with open("passwords.json", "a") as f:
        j = json.dumps(users)
        f.write(j+'\n')

def displayMenu():
    status = input("Are you a registered user? y/n? Press q to quit: ")
    if status == "y":
        oldUser()
    elif status == "n":
        newUser()
    return (status)

def newUser():
    createLogin = input("Create login name: ")
    if createLogin in users:
        print("\nLogin name already exist!\n")
    else:
        createPassw = input("Create password: ")
        enc_password = base64.b64encode(bytes(createPassw.encode('utf-8')))
        users[createLogin] = enc_password.decode('utf-8')
        print("\nUser created!\n")
        write_in_file(users)


def oldUser():
    login = input("Enter login name: ")
    passw = input("Enter password: ")
    with open('passwords.json', 'r') as p:
        new_d = [json.loads(line) for line in p]
        # print(new_d)
        for index, dict_ in enumerate(new_d):
            if login in dict_ and base64.b64decode(dict_[login]).decode('utf-8') == passw:
                print("\nLogin successful!\n")
                break
            elif login in dict_ and dict_[login] != passw:
                print("\nUser doesn't exist or wrong password!\n")
                break

while status != "q":
    status = displayMenu()



