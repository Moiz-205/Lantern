from python import server, client
import threading

if __name__ == "__main__":
    threading.Thread(target=server.start_server, args=("test",), daemon=True).start()

    client.connect(host="127.0.0.1", port=5000,
        username="cat", color="red",
        room_code="test")
