import threading
import socket
from core import protocol


HOST = "0.0.0.0"
PORT = 5000

clients = {}        # {key=client sockets, value=username}
lock = threading.Lock()

def broadcast(message, sender_socket):
    with lock:
        for client_socket in clients:
            if client_socket != sender_socket:
                client_socket.send(message)

def handle_client(client_socket, room_code):
    join_request = client_socket.recv(1024)
    decoded_request = protocol.decode(join_request)
    join_code = decoded_request.get("room_code")

    if join_code != room_code:
        client_socket.close()
        return

    new_client = {client_socket: decoded_request.get("username")}
    clients.update(new_client)

    message_type = decoded_request.get("type")
    username = decoded_request.get("username")
    color = decoded_request.get("color")
    message_dict = {"type": message_type, "username": username, "color": color}

    message = protocol.encode(message_dict)
    broadcast(message, client_socket)

    # for messages and disconnections
    while True:
        try:
            chat_message = client_socket.recv(1024)
            broadcast(chat_message, client_socket)
        except Exception:
            with lock:
                user = clients[client_socket]
                del clients[client_socket]

            leave_dict = {"type": "leave", "username": user}
            leave_message = protocol.encode(leave_dict)
            broadcast(leave_message, client_socket)

            client_socket.close()
            break

def start_server(room_code):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))

    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, _ = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, room_code)).start()
