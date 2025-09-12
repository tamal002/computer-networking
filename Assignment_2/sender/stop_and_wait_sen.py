import socket
import json
import time
import csv

# Parameters (assumptions)
LINK_RATE = 1_000_000   # 1 Mbps
FRAME_SIZE = 521        # bits
TP = 2                  # seconds (one-way propagation)
P = 0.2                 # error probability

# creating the sender socket
sender_socket = socket.socket()
print("\033[32mSender socket is created\033[0m")

sender_socket.connect(('localhost', 9999))
print("\033[32mSuccessfully connected with receiver.\033[0m\n")

# reading data
with open("../dataword.txt", "r", encoding="utf-8") as f:
    text_data = f.read().strip()
print(f"your data: {text_data}\n")

# convert to binary
binary_data = ''.join(format(ord(c), '08b') for c in text_data)
print(f"your data in binary form: {binary_data}\n")

# frame creation
frame_size = 512  # still used for slicing payload
header_template = {"sender_address": "127.0.0.1", "receiver_address": "127.0.0.1", "seq": -1}
trailer_template = {"padding": -1, "crc": -1, "generator": -1, "checksum": -1}

n = len(binary_data)
padding = 0
frames = []
seq_no = 0
for i in range(0, n, frame_size):
    frame = []
    header = header_template.copy()
    header["seq"] = seq_no
    seq_no = 1 - seq_no
    frame.append(header)
    payload = binary_data[i:i + frame_size]

    if len(payload) < frame_size:
        need = frame_size - len(payload)
        payload += '0' * need
        padding = need

    frame.append(payload)
    trailer = trailer_template.copy()
    trailer["padding"] = padding
    frame.append(trailer)
    frames.append(frame)

# Transmission
no_of_frames = len(frames)
sender_socket.send(str(no_of_frames).encode())
print("\033[32mInitiating transmission using Stop-and-Wait...\033[0m\n")
time.sleep(2)

index = 0
while index < len(frames):
    header = frames[index][0]
    seq = header["seq"]
    frame_bytes = json.dumps(frames[index]).encode()
    sender_socket.send(frame_bytes)
    print(f"\033[32mFrame sent:\033[0m {frames[index]}\n")
    sender_socket.settimeout(5)
    try:
        ack = int(sender_socket.recv(1024).decode())
        if ack == 1 - seq:
            print("\033[32mACK received, moving to next frame...\033[0m\n")
            index += 1
        else:
            print("\033[31mWrong ACK received.\033[0m\n")
    except socket.timeout:
        print("\033[31mTimeout! Resending frame...\033[0m\n")

print("\033[32mAll frames sent successfully!\033[0m\n")
sender_socket.close()

# Efficiency Calculation
T_f = FRAME_SIZE / LINK_RATE
efficiency = ((1 - P) * T_f) / (T_f + 2 * TP)


with open("../analyse.csv", "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Stop-and-Wait", efficiency])
