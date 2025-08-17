
import socket
import json
from crc import crc
from checksum import checksum
from error_injection import inject_error


sender_socket = socket.socket()
print("Sender socket is created")
sender_socket.connect(('localhost', 9999))
print(f"successfuly connected with receiver.")

# reading data from dataword.txt file
with open("dataword.txt", "r", encoding="utf-8") as f:
    text_data = f.read().strip()

print(f"your data: {text_data}")

# converting the string data into binary string
binary_data = ''.join(format(ord(char), '08b') for char in text_data)
print(f"your data in binary form: {binary_data}")

# size of each frame will be 64 bit -> 8 characters per frame
frame_size = 64

# the payload which will be actually send as the real data
header = {
    "HOST" : "localhost",
    "PORT" : 9999,
}

trailer_template = {
    "padding" : -1,
    "crc" : -1, 
    "checksum" : -1,
}

n = len(binary_data)
start = 0
padding = 0

frames = []
for i in range(start, n, frame_size):
    frame = []
    frame.append(header)
    payload = binary_data[start : start + frame_size]
    start += frame_size
    
    if len(payload) < frame_size: # need to pad
        need = frame_size - len(frame)
        frame += '0' * need
        padding = need

    frame.append(payload)
    crc_value = crc(payload) # crc / check sum method call
    trailer = trailer_template.copy()
    trailer["padding"] = padding
    trailer["crc"] = crc_value
    frame.append(trailer)
    frames.append(frame)


# injecting error
frames = inject_error(frames)


# Sending frames one by one to the reciever.
for frame in frames:
    frame_bytes = json.dumps(frame).encode("utf-8") + b"\n"
    sender_socket.send(frame_bytes)

'''

                                            | working note | 

=>  json.dumps() converts a Python object (list/dict/string/number) into a JSON string.

    Example:
    json.dumps(frame)
    gives something like: '[{"HOST": "127.0.0.1", "PORT": 5000}, "0101010101...", {"padding": 2, "crc": "101"}]'

    Now it’s just a normal string in JSON format.

=>  .encode("utf-8")
    Converts that JSON string into bytes (because sockets only send bytes).

    Example: b'[{"HOST": "127.0.0.1", "PORT": 5000}, "0101010101...", {"padding": 2, "crc": "101"}]'

=> + b"\n" Appends a newline character (in bytes form) at the end.
    So the final thing looks like: b'[{"HOST": "127.0.0.1", "PORT": 5000}, "0101010101...", {"padding": 2, "crc": "101"}]\n'
    This newline delimiter helps the receiver know where one frame ends and the next begins.



'''


# receiving the response from the receiver.
respose_from_server = sender_socket.recv(1024).decode("UTF-8") 
print(respose_from_server)

# closing the connection.
sender_socket.close()


    


