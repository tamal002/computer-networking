import socket
import json
import time
import csv

# Parameters (assumptions)
LINK_RATE = 1_000_000   # 1 Mbps
FRAME_SIZE = 521        # bits (for efficiency formula)
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
print(f"Your data: {text_data[:60]}...\n")  # print only preview

# convert to binary
binary_data = ''.join(format(ord(c), '08b') for c in text_data)
print(f"Binary length = {len(binary_data)} bits\n")

# frame creation (payload slice size = 512 bits as before)
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
    seq_no = 1 - seq_no
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

# Transmission
no_of_frames = len(frames)
sender_socket.send(f"{no_of_frames}\n".encode())
print("\033[32mInitiating transmission using Stop-and-Wait...\033[0m\n")
time.sleep(1)

index = 0
ack_buffer = ""
while index < len(frames):
    header = frames[index][0]
    seq = header["seq"]
    frame_bytes = (json.dumps(frames[index]) + "\n").encode()
    try:
        sender_socket.send(frame_bytes)
    except (BrokenPipeError, ConnectionResetError):
        print("Connection closed by receiver.")
        break
    print(f"\033[32mFrame sent:\033[0m seq={seq}\n")

    # wait for ACK
    sender_socket.settimeout(5)
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
            if ack == 1 - seq:
                print(f"\033[32mACK received:\033[0m {ack}\n")
                index += 1
            else:
                print(f"\033[31mWrong ACK received:\033[0m {ack}\n")
    except socket.timeout:
        print(f"\033[31mTimeout! Retransmitting frame seq={seq}\033[0m\n")

print("\033[32mAll frames sent successfully!\033[0m\n")
sender_socket.close()

# Efficiency Calculation
T_f = FRAME_SIZE / LINK_RATE
efficiency = ((1 - P) * T_f) / (T_f + 2 * TP)
print(f"Stop-and-Wait Efficiency = {efficiency:.6f}\n")

with open("../analyse.csv", "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Stop-and-Wait", efficiency])
