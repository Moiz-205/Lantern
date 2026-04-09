from core import server, client
import threading


if __name__ == "__main__":
    is_host = input("Host or Join (h/j) > ").strip().lower() == "h"
    username = input("Enter your username > ")
    color = input("Enter your color > ")

    if is_host:
        threading.Thread(target=server.start_server, args=("test",), daemon=True).start()

    client.connect(host="127.0.0.1", port=5000,
        username=username, color=color,
        room_code="test")

    threading.Thread(target=client.receive_message, args=(), daemon=True).start()
    while True:
        message_text = input("> ")
        client.send_message(username, color, message_text)
