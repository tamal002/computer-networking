import socket
import json
import math

WINDOW_SIZE = 4

receiver_socket = socket.socket()
print("Receiver socket is created")

receiver_socket.bind(('localhost', 9999))
receiver_socket.listen(1)

sender_socket, sender_address = receiver_socket.accept()
print(f"\033[32mSuccessfully connected with the sender {sender_address}.\033[0m\n")

frames = []
buffer = ""

# --- read number of frames first (newline terminated) ---
no_frames = None
while no_frames is None:
    data = sender_socket.recv(1024).decode()
    buffer += data
    if "\n" in buffer:
        first, buffer = buffer.split("\n", 1)
        no_frames = int(first.strip())

count = 0
expected_seq = 0

# simulate loss
frame_loss = math.ceil(no_frames / 2)
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
            print(f"Skipping corrupted frame chunk")
            continue

        seq = frame[0]["seq"]

        if loss and seq == frame_loss:
            print(f"\033[31mSimulated loss at frame seq={seq}\033[0m\n")
            loss = False
            # do not ACK → sender will timeout
            continue

        if seq == expected_seq:
            frames.append(frame)
            print(f"\033[32mFrame received correctly:\033[0m seq={seq}\n")
            sender_socket.send(f"{seq}\n".encode())  # cumulative ACK
            expected_seq += 1
            count += 1
        else:
            # duplicate ACK
            sender_socket.send(f"{expected_seq-1}\n".encode())
            print(f"\033[33mOut-of-order frame {seq} discarded, sent dup-ACK {expected_seq-1}\033[0m\n")

# reassemble frames
data = ""
for frame in frames:
    header, payload, trailer = frame
    padding = trailer["padding"]
    if padding > 0:
        payload = payload[:-padding]
    for i in range(0, len(payload), 8):
        byte = payload[i:i+8]
        if len(byte) == 8:
            data += chr(int(byte, 2))

print(f"Received data: {data}\n")

sender_socket.close()
receiver_socket.close()
