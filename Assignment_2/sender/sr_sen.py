import socket
import json
import time
import threading

# Config
WINDOW_SIZE = 4
TIMEOUT = 5  # seconds

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

frame_size = 512
header_template = {"sender_address": "127.0.0.1", "receiver_address": "127.0.0.1", "seq": -1}
trailer_template = {"padding": -1, "crc": -1, "generator": -1, "checksum": -1}

# frame creation
n = len(binary_data)
padding = 0
frames = []
seq_no = 0
for i in range(0, n, frame_size):
    frame = []
    header = header_template.copy()
    header["seq"] = seq_no
    seq_no += 1
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

no_of_frames = len(frames)
# send number of frames with newline delimiter
sender_socket.send(f"{no_of_frames}\n".encode())
print("\033[32mInitiating transmission using Selective Repeat...\033[0m\n")
time.sleep(2)

# Sender state
base = 0
next_seq = 0
acked = [False] * no_of_frames
timers = {}
ack_buffer = ""  # for partial ACKs

# start retransmission timer for each particular frame
def start_timer(i):
    def timer_expired():
        if not acked[i]:
            print(f"\033[31mTimeout! Retransmitting frame seq={i}\033[0m\n")
            frame_bytes = (json.dumps(frames[i]) + "\n").encode()
            try:
                sender_socket.send(frame_bytes)
            except (BrokenPipeError, ConnectionResetError):
                return
            start_timer(i)  # restart timer
    t = threading.Timer(TIMEOUT, timer_expired)
    t.start()
    timers[i] = t

while base < no_of_frames:
    # send frames within window
    while next_seq < base + WINDOW_SIZE and next_seq < no_of_frames:
        frame_bytes = (json.dumps(frames[next_seq]) + "\n").encode()
        sender_socket.send(frame_bytes)
        print(f"\033[32mFrame sent:\033[0m seq={next_seq}\n")
        start_timer(next_seq)
        next_seq += 1

    try:
        sender_socket.settimeout(TIMEOUT)
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
            if ack < no_of_frames:
                acked[ack] = True
                if ack in timers:
                    timers[ack].cancel()
                while base < no_of_frames and acked[base]:
                    base += 1
    except socket.timeout:
        # timers handle retransmissions
        pass

print("\033[32mAll frames sent successfully!\033[0m\n")
sender_socket.close()
