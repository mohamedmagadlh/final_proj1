import socket
import select


HEADER_LENGTH = 10
IP = socket.gethostbyname(socket.gethostname())
PORT = 55000
u = 'utf-8'
d = 'data'
h = 'header'

LIST_UPDATE = "1"  # sent when any user joins or leaves the chat room
NORMAL_MSG = "2"  # normal message sent from user to server or another user

# format for the list update is : MESSAGE TYPE HEADER + MESSAGE TYPE + LIST HEADER + LIST
# format for the normal message is : MESSAGE TYPE HEADER + MESSAGE TYPE + USER HEADER + USER + MESSAGE HEADER + MESSAGE
# MESSAGE TYPES are differentiated on the client side. We can even do the implementation without sending the message
# type and sending the applying proper checks on the client side. but for now i have used the first approach.


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen(5)

sockets_list = [server_socket]
clients = {}
print(f'Listening at {IP}:{PORT}...')


def listing_online_users():
    clients_online = ""
    for value in clients.values():
        clients_online += value[d].decode(u)
        clients_online += " "
    print(clients_online)
    return clients_online


def sending_list_of_online_users():
    online_clients = listing_online_users()
    msg_type_header = f"{len(LIST_UPDATE):<{HEADER_LENGTH}}".encode(u)
    msg_type = LIST_UPDATE.encode(u)
    list_header = f"{len(online_clients):<{HEADER_LENGTH}}".encode(u)
    online_clients = online_clients.encode(u)
    for client_socket in clients:  # NEED TO MAKE CHANGES
        client_socket.send(msg_type_header + msg_type + list_header + online_clients)


def get_socket_pair(my_dict, dest):
    for item in my_dict.items():
        if item[1][d].decode(u) == dest:
            return item[0]


def receive_message(client_socket):
    try:
        dest_header = client_socket.recv(HEADER_LENGTH)
        if not len(dest_header):
            return False
        dest_user_len = int(dest_header.decode(u))
        dest_user = client_socket.recv(dest_user_len)
        message_header = client_socket.recv(HEADER_LENGTH)
        message_length = int(message_header.decode(u))
        return {'dest_header': dest_header, 'dest_user': dest_user, h: message_header,
                d: client_socket.recv(message_length)}
    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()  # should negotiate the clients online with the server
            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)
            clients[client_socket] = user
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address,
                                                                            user[d].decode(u)))
            sending_list_of_online_users()
        else:
            message = receive_message(notified_socket)
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket][d].decode(u)))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                sending_list_of_online_users()
                continue
            user = clients[notified_socket]
            print(
                f"Message from {user[d].decode(u)}: {message[d].decode(u)} to {message['dest_user'].decode(u)}")
            destination_client = message['dest_user'].decode(u)
            msg_type_header = f"{len(NORMAL_MSG):<{HEADER_LENGTH}}".encode(u)
            msg_type = NORMAL_MSG.encode(u)

            if destination_client.lower() == "all":
                for client_socket in clients:
                    if client_socket != notified_socket:
                        client_socket.send(
                            msg_type_header + msg_type + user[h] + user[d] + message[h] + message[
                                d])
            else:
                destination_socket = get_socket_pair(clients, destination_client.lower())
                destination_socket.send(
                    msg_type_header + msg_type + user[h] + user[d] + message[h] + message[d])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        sending_list_of_online_users()
        del clients[notified_socket]