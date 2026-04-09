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
