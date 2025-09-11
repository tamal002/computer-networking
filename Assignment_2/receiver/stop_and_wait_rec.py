import socket
import json
import math

receiver_socket = socket.socket()
print("Receiver socket is created")

receiver_socket.bind(('localhost', 9999))
receiver_socket.listen(1)

sender_socket, sender_address = receiver_socket.accept()
print(f"\033[32mSuccessfully connected with the sender {sender_address}.\033[0m\n")


frames = []
no_frames = int(sender_socket.recv(1204).decode())
count = 0
ack = 0
# the same frame_loss will be triggered for all three protocols to make fair comparriosons.
frame_loss = math.ceil(no_frames/2) 
loss = True
while count < no_frames:
    json_frame = sender_socket.recv(1204).decode()
    frame = json.loads(json_frame)
    header = frame[0]
    if loss and count + 1 == frame_loss:
        seq = -1
        loss = False
    else:
        seq = header["seq"]
    if seq == ack:
        ack = 1 - ack
        sender_socket.send(str(ack).encode("utf-8"))
        frames.append(frame)
        count += 1
    else:
        sender_socket.send(str(ack).encode("utf-8"))


# reassembling the frames and retrieving the data.
data = ""
for frame in frames:
    header, payload, trailer = frame
    padding = trailer["padding"]
    if padding > 0:
        payload = payload[:-padding]
    binary_data = payload
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) == 8:
            data += chr(int(byte, 2))
print(f"received data: {data}\n")


# connection termination
sender_socket.close()
receiver_socket.close()

