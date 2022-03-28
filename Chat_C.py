import socket
import errno
import sys
import time
import threading

HEADER_LENGTH = 10

IP = socket.gethostbyname(socket.gethostname())
PORT = 55000
my_username = input("Username: ")
u = 'utf-8'

online_users=[]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = my_username.encode(u)
username_header = f"{len(username):<{HEADER_LENGTH}}".encode(u)
dest_user = "server".encode(u)
dest_user_len = f"{len(dest_user):<{HEADER_LENGTH}}".encode(u)

client_socket.send(dest_user_len + dest_user + username_header + username)

def read_msg_type_header():
    msg_type_header = client_socket.recv(HEADER_LENGTH)
    if not len(msg_type_header):
        print('Connection closed by the server')
        sys.exit()
    msg_type_length = int(msg_type_header.decode(u))
    msg_type = client_socket.recv(msg_type_length).decode(u)
    return int(msg_type)

def selection_menu(user_list):
    if len(user_list) != 1:
        print("\n\nThe currently available users are :", end="\n")
        count = 1
        for name in user_list:
            if name != my_username:
                print(f"{count}. {name}", end="\n")
                count+=1
    else:
        print("\n\n No user is currently online")

def recv_online_users():
    list_header = client_socket.recv(HEADER_LENGTH)
    list_length = int(list_header.decode(u).strip())
    users_string = client_socket.recv(list_length).decode(u)
    users_list = users_string.split()
    return users_list

def read_message():
    username_header = client_socket.recv(HEADER_LENGTH)
    username_length = int(username_header.decode(u).strip())
    username = client_socket.recv(username_length).decode(u)
    message_header = client_socket.recv(HEADER_LENGTH)
    message_length = int(message_header.decode(u).strip())
    message = client_socket.recv(message_length).decode(u)
    return username, message

def send_message():
    print(f"\n{my_username} > ",end = "")
    while True:
        global online_users
        message=input()
        user_list = online_users
        if "@" in message:
            recp = (message.split()[0]).split("@")[1]
            if (recp.lower() != my_username.lower()) and (recp.lower() in map(str.lower, user_list) or recp.lower() == "all"):
                dest_user = f"{recp}"
                dest_user = dest_user.encode(u)
                dest_user_len = f"{len(dest_user):<{HEADER_LENGTH}}".encode(u)
                try :
                    actual_message = message.split(' ', 1)[1]
                    actual_message = actual_message.encode(u)
                    message_header = f"{len(actual_message):<{HEADER_LENGTH}}".encode(u)
                    client_socket.send(dest_user_len + dest_user + message_header + actual_message)
                except:
                    print("\nError : Cannot send empty message")
                    print(f"\n{my_username} > ", end="")
            else:
                print("\nError : Please enter the correct username")
                print(f"\n{my_username} > ", end="")
                continue
        else:
            print("\n Please specify the @username before entering the message")
            print(f"\n{my_username} > ", end="")
            continue
        print(f"\n{my_username} > ", end="")

def receive_msg():
    while True:
        try:
            while True:
                msg_type = read_msg_type_header()
                if msg_type == 1:
                    global online_users
                    online_users = recv_online_users()
                    selection_menu(online_users)
                elif msg_type == 2:
                    username , message = read_message()
                    print(f'\n\n{username} > {message}')
                else:
                    print('Connection closed by the server')
                    sys.exit()
                print(f"\n{my_username} > ", end="")

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()
            pass

        except Exception as e:
            print('Reading error: '.format(str(e)))
            sys.exit()

try:
    time.sleep(1.0)
    msg_type = read_msg_type_header()
    online_users = recv_online_users()
    print("\nUSE @all TO SEND MESSAGE TO EVERYONE IN THE CHAT ROOM OR @username TO SEND MESSAGE TO A PARTICULAR USER.",end="\n")

    if len(online_users) and online_users[0] != my_username:
        selection_menu(online_users)
    x = threading.Thread(target=receive_msg, args=())
    x.start()
    y = threading.Thread(target=send_message, args=())
    y.start()

except KeyboardInterrupt:
    client_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()
    pass