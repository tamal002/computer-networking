import socket
import json
import time
import csv

# Parameters
WINDOW_SIZE = 4
LINK_RATE = 1_000_000   # 1 Mbps
FRAME_SIZE = 521        # bits
TP = 2                  # seconds (one-way)
P = 0.2                 # error probability
TIMEOUT = 5             # seconds

# create socket
sender_socket = socket.socket()
print("\033[32mSender socket is created\033[0m")

sender_socket.connect(('localhost', 9999))
print("\033[32mSuccessfully connected with receiver.\033[0m\n")

# read data
with open("../dataword.txt", "r", encoding="utf-8") as f:
    text_data = f.read().strip()
print(f"your data: {text_data}\n")

# convert to binary
binary_data = ''.join(format(ord(c), '08b') for c in text_data)
print(f"your data in binary form: {binary_data}\n")

# frame creation
slice_size = 512
header_template = {"sender_address": "127.0.0.1", "receiver_address": "127.0.0.1", "seq": -1}
trailer_template = {"padding": -1, "crc": -1, "generator": -1, "checksum": -1}

n = len(binary_data)
padding = 0
frames = []
seq_no = 0
for i in range(0, n, slice_size):
    frame = []
    header = header_template.copy()
    header["seq"] = seq_no
    seq_no += 1
    frame.append(header)
    payload = binary_data[i:i + slice_size]

    if len(payload) < slice_size:
        need = slice_size - len(payload)
        payload += '0' * need
        padding = need

    frame.append(payload)
    trailer = trailer_template.copy()
    trailer["padding"] = padding
    frame.append(trailer)
    frames.append(frame)

# transmission
no_of_frames = len(frames)
sender_socket.send(f"{no_of_frames}\n".encode())
print("\033[32mInitiating transmission using Go-Back-N...\033[0m\n")
time.sleep(2)

base = 0
next_seq = 0
ack_buffer = ""

while base < no_of_frames:
    # send frames within window
    while next_seq < base + WINDOW_SIZE and next_seq < no_of_frames:
        frame_bytes = (json.dumps(frames[next_seq]) + "\n").encode()
        sender_socket.send(frame_bytes)
        print(f"\033[32mFrame sent:\033[0m seq={frames[next_seq][0]['seq']}\n")
        next_seq += 1

    sender_socket.settimeout(TIMEOUT)
    try:
        data = sender_socket.recv(1024).decode()
        if not data:
            continue
        ack_buffer += data
        while "\n" in ack_buffer:
            ack_str, ack_buffer = ack_buffer.split("\n", 1)
            if not ack_str.strip():
                continue
            ack = int(ack_str)
            print(f"Received ACK {ack}\n")
            base = ack + 1
    except socket.timeout:
        print(f"\033[31mTimeout! Resending from seq={frames[base][0]['seq']}...\033[0m\n")
        for i in range(base, next_seq):
            frame_bytes = (json.dumps(frames[i]) + "\n").encode()
            sender_socket.send(frame_bytes)
            print(f"\033[33mRetransmitted:\033[0m seq={frames[i][0]['seq']}\n")

print("\033[32mAll frames sent successfully!\033[0m\n")
sender_socket.close()

# Efficiency calculation (theoretical)
N = WINDOW_SIZE
T_f = FRAME_SIZE / LINK_RATE
efficiency = ((1 - P) * N * T_f) / (T_f + 2 * TP)

with open("../analyse.csv", "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Go-Back-N", efficiency])
