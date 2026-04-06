import json


def encode(message):
    json_message = json.dumps(message)
    json_message += "\n"
    encoded_message = json_message.encode()
    return encoded_message

def decode(data):
    decoded_data = data.decode()
    decoded_data = decoded_data.strip()
    decoded_message = json.loads(decoded_data)
    return decoded_message

if __name__ == "__main__":
    join_msg = {"type": "join", "username": "Person A", "color": "red"}
    chat_msg = {"type": "chat", "username": "Person A", "color": "red", "message": "FLower is blue."}
    leave_msg = {"type": "leave", "username": "Person A"}

    join_enc = encode(join_msg)
    join_dec = decode(join_enc)
    print(join_enc)
    print(join_dec)

    chat_enc = encode(chat_msg)
    chat_dec = decode(chat_enc)
    print(chat_enc)
    print(chat_dec)

    leave_enc = encode(leave_msg)
    leave_dec = decode(leave_enc)
    print(leave_enc)
    print(leave_dec)
