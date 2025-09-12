import socket
import json
import math

WINDOW_SIZE = 4

receiver_socket = socket.socket()
print("Receiver socket is created")

receiver_socket.bind(('localhost', 9999))
receiver_socket.listen(1)

sender_socket, sender_address = receiver_socket.accept()
print(f"\033[32mSuccessfully connected with sender {sender_address}.\033[0m\n")

frames = {}
no_frames = int(sender_socket.recv(1204).decode())
expected_base = 0

# Simulate loss for fair comparison
frame_loss = math.ceil(no_frames / 2)
loss = True

while len(frames) < no_frames:
    json_frame = sender_socket.recv(1204).decode()
    if not json_frame:
        break
    frame = json.loads(json_frame)
    header = frame[0]
    seq = header["seq"]

    if loss and seq == frame_loss:
        print(f"\033[31mSimulated loss at frame seq={seq}\033[0m\n")
        loss = False
        continue

    if expected_base <= seq < expected_base + WINDOW_SIZE:
        if seq not in frames:  # avoid duplicate store
            frames[seq] = frame
            print(f"\033[32mFrame stored in buffer:\033[0m seq={seq}\n")
        sender_socket.send(str(seq).encode())  # send individual ACK
        # slide window if base frame delivered
        while expected_base in frames:
            expected_base += 1
    else:
        print(f"\033[33mFrame {seq} out of window, discarded\033[0m\n")
        sender_socket.send(str(seq).encode())  # still ACK it (may be duplicate)

# Reassembly
data = ""
for i in range(no_frames):
    header, payload, trailer = frames[i]
    padding = trailer["padding"]
    if padding > 0:
        payload = payload[:-padding]
    for j in range(0, len(payload), 8):
        byte = payload[j:j+8]
        if len(byte) == 8:
            data += chr(int(byte, 2))

print(f"Received data: {data}\n")

sender_socket.close()
receiver_socket.close()