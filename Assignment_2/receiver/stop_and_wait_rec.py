import socket
import json
import math

receiver_socket = socket.socket()
print("Receiver socket is created")

receiver_socket.bind(('localhost', 9999))
receiver_socket.listen(1)

sender_socket, sender_address = receiver_socket.accept()
print(f"\033[32mSuccessfully connected with the sender {sender_address}.\033[0m\n")

# read number of frames first
buffer = ""
no_frames = None
while no_frames is None:
    data = sender_socket.recv(1024).decode()
    if not data:
        continue
    buffer += data
    if "\n" in buffer:
        first, buffer = buffer.split("\n", 1)
        no_frames = int(first.strip())

frames = []
count = 0
ack = 0
frame_loss = math.ceil(no_frames / 2)  # simulate one loss
loss = True

while count < no_frames:
    data = sender_socket.recv(2048).decode()
    if not data:
        break
    buffer += data
    while "\n" in buffer:
        json_frame, buffer = buffer.split("\n", 1)
        if not json_frame.strip():
            continue
        try:
            frame = json.loads(json_frame)
        except json.JSONDecodeError:
            continue

        header = frame[0]
        seq = header["seq"]

        if loss and count + 1 == frame_loss:
            print(f"\033[31mSimulated loss at frame seq={seq}\033[0m\n")
            seq = -1
            loss = False

        if seq == ack:
            print(f"\033[32mFrame received:\033[0m seq={seq}\n")
            ack = 1 - ack
            sender_socket.send(f"{ack}\n".encode())
            frames.append(frame)
            count += 1
        else:
            print(f"\033[33mOut-of-order frame discarded:\033[0m seq={seq}, sent duplicate ACK {ack}\n")
            sender_socket.send(f"{ack}\n".encode())

# reassembling
data_text = ""
for frame in frames:
    header, payload, trailer = frame
    padding = trailer["padding"]
    if padding > 0:
        payload = payload[:-padding]
    for i in range(0, len(payload), 8):
        byte = payload[i:i+8]
        if len(byte) == 8:
            data_text += chr(int(byte, 2))

print(f"Received data---\n {data_text}\n")  # preview

sender_socket.close()
receiver_socket.close()
