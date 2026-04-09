import socket
from core import protocol


def connect(host, port, username, color, room_code):
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    join_request = {"type": "join", "username": username, "color": color, "room_code": room_code}
    encoded_request = protocol.encode(join_request)
    client_socket.send(encoded_request)

def receive_message():
    while True:
        try:
            message_receive = client_socket.recv(1024)
            decoded_receive = protocol.decode(message_receive)
            message_sender = decoded_receive.get("username")
            message_color = decoded_receive.get("color")
            if decoded_receive.get("type") == "join":
                print(f"({message_sender}, {message_color}) - Joined")
            elif decoded_receive.get("type") == "leave":
                print(f"({message_sender}, {message_color}) - Left")
            else:
                message_content = decoded_receive.get("message")
                print(f"({message_sender}, {message_color}) - {message_content}")
        except Exception:
            break

def send_message(username, color, message_text):
    message_send = {"type": "chat", "username": username, "color": color, "message": message_text}
    encoded_message = protocol.encode(message_send)
    client_socket.send(encoded_message)
