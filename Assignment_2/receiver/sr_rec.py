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

# --- Read the number of frames first (terminated with newline) ---
buffer = ""
no_frames = None
while no_frames is None:
    data = sender_socket.recv(1024).decode()
    buffer += data
    if "\n" in buffer:
        first, buffer = buffer.split("\n", 1)
        no_frames = int(first.strip())

frames = {}
expected_base = 0

# Simulate one loss for fair comparison
frame_loss = math.ceil(no_frames / 2)
loss = True

# --- Main loop ---
while len(frames) < no_frames:
    data = sender_socket.recv(2048).decode()
    if not data:
        break
    buffer += data

    # extract complete JSON frames delimited by newline
    while "\n" in buffer:
        json_frame, buffer = buffer.split("\n", 1)
        if not json_frame.strip():
            continue
        try:
            frame = json.loads(json_frame)
        except json.JSONDecodeError:
            print(f"⚠️ Incomplete/corrupted frame skipped: {json_frame[:60]}...")
            continue

        seq = frame[0]["seq"]

        # simulate frame loss once
        if loss and seq == frame_loss:
            print(f"\033[31mSimulated loss at frame seq={seq}\033[0m\n")
            loss = False
            continue

        if expected_base <= seq < expected_base + WINDOW_SIZE:
            if seq not in frames:  # avoid duplicate store
                frames[seq] = frame
                print(f"\033[32mFrame stored in buffer:\033[0m seq={seq}\n")

            sender_socket.send(f"{seq}\n".encode())  # ACK this seq

            # slide window if base frame is now delivered
            while expected_base in frames:
                expected_base += 1
        else:
            print(f"\033[33mFrame {seq} out of window, discarded\033[0m\n")
            sender_socket.send(f"{expected_base-1}\n".encode())  # send dup-ACK

# --- Reassembly ---
data = ""
for i in range(no_frames):
    if i not in frames:
        continue  # skip lost/unrecovered frames
    header, payload, trailer = frames[i]
    padding = trailer["padding"]
    if padding > 0:
        payload = payload[:-padding]
    for j in range(0, len(payload), 8):
        byte = payload[j:j+8]
        if len(byte) == 8:
            data += chr(int(byte, 2))

print(f"Received data:\n{data}\n")

sender_socket.close()
receiver_socket.close()
