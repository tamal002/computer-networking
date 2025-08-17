
import socket
import json
from crc import crc
from checksum import checksum


receiver_socket = socket.socket()
print("Receiver socket is created")

receiver_socket.bind(('localhost', 9999))

# The maximum number (here 3) of unaccepted connections the server will queue before refusing new ones.
receiver_socket.listen(1) 

sender_socket, sender_address = receiver_socket.accept()
print(f"successfuly connected with the sender {sender_address}.")

buffer = sender_socket.makefile("r", encoding="UTF-8")

sender_socket.send(bytes("successfuly receied the packets", "utf-8"))

receiver_socket.close()

frames = []
for line in buffer:  # each line = one frame
    frame = json.loads(line.strip())
    print(f"Received frame: {frame}")
    frames.append(frame)

sender_socket.close()


# check crc


# check checksum

# result of error detection 

