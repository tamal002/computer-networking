import socket
import json
import time

# Sender window size (configurable)
WINDOW_SIZE = 4

# creating the sender socket
sender_socket = socket.socket()
print("\033[32mSender socket is created\033[0m")

# connecting with the server / receiver
sender_socket.connect(('localhost', 9999))
print("\033[32msuccessfuly connected with receiver.\033[0m\n")

# reading data from dataword.txt file
with open("../dataword.txt", "r", encoding="utf-8") as f:
    text_data = f.read().strip()
print(f"your data: {text_data}\n")

# converting the string data into binary string
binary_data = ''.join(format(ord(char), '08b') for char in text_data)
print(f"your data in binary form: {binary_data}\n")

# frame size in bits
frame_size = 512  # 64 Byte = 64 x 8 = 512 bit

# Header template
header_template = {
    "sender_address": '127.0.0.1',
    "receiver_address": "127.0.0.1",
    "seq": -1
}

# Trailer template
trailer_template = {
    "padding": -1,
    "crc": -1,
    "generator": -1,
    "checksum": -1,
}

# framing the data
n = len(binary_data)
padding = 0
seq_no = 0
frames = []
for i in range(0, n, frame_size):
    frame = []
    header = header_template.copy()
    header["seq"] = seq_no
    seq_no += 1  # increasing seq number per frame (modulo later if needed)
    frame.append(header)
    payload = binary_data[i: i + frame_size]

    if len(payload) < frame_size:  # need to pad
        need = frame_size - len(payload)
        payload += '0' * need
        padding = need

    frame.append(payload)
    trailer = trailer_template.copy()
    trailer["padding"] = padding
    frame.append(trailer)
    frames.append(frame)

# ----- transmission start -----
no_of_frames = len(frames)
sender_socket.send(str(no_of_frames).encode("utf-8"))
print("\033[32minitiating the frames transmission using Go-Back-N...\033[0m\n")
time.sleep(2)

base = 0          # first unACKed frame
next_seq = 0      # next frame to send
timeout = 5       # timer value

while base < no_of_frames:
    # send frames in window
    while next_seq < base + WINDOW_SIZE and next_seq < no_of_frames:
        frame_bytes = json.dumps(frames[next_seq]).encode("utf-8")
        sender_socket.send(frame_bytes)
        print(f"\033[32mFrame sent:\033[0m seq={frames[next_seq][0]['seq']}\n")
        next_seq += 1

    # wait for ACK
    sender_socket.settimeout(timeout)
    try:
        ack = int(sender_socket.recv(1024).decode())
        print(f"Received ACK {ack}\n")

        # cumulative ACK → slide base
        base = ack + 1
    except socket.timeout:
        print(f"\033[31mTimeout! Resending from seq={frames[base][0]['seq']}...\033[0m\n")
        # retransmit all frames from base to next_seq-1
        for i in range(base, next_seq):
            frame_bytes = json.dumps(frames[i]).encode("utf-8")
            sender_socket.send(frame_bytes)
            print(f"\033[33mRetransmitted:\033[0m seq={frames[i][0]['seq']}\n")

print(f"\033[32mAll frames sent successfully\033[0m\n")
sender_socket.close()
