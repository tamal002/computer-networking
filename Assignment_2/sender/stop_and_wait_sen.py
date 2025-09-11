import socket
import json
import time 



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


# ftame size in bits
frame_size = 512 # 64 Byte ---> 64 x 8 = 512 bit

# Header structure (template)
header_template = {
    "sender_address": '127.0.0.1',
    "receiver_address": "127.0.0.1",
    "seq": -1
}


# Trailor structure (template)
trailer_template = {
    "padding" : -1,
    "crc" : -1, 
    "generator": -1,
    "checksum" : -1,
}


# framing the data
# sequence will in toggle mode [0->1->0->1->0->... so on]
n = len(binary_data)
padding = 0
seq_no = 0
frames = []
for i in range(0, n, frame_size):
    frame = []
    header = header_template.copy()
    header["seq"] = seq_no
    seq_no = 1 - seq_no
    frame.append(header)
    payload = binary_data[i : i + frame_size]
    
    if len(payload) < frame_size: # need to pad
        need = frame_size - len(payload)
        payload += '0' * need
        padding = need

    frame.append(payload)
    trailer = trailer_template.copy()
    trailer["padding"] = padding
    frame.append(trailer)
    frames.append(frame)


# ----- starting the transmission -------
no_of_frames = len(frames)
sender_socket.send(str(no_of_frames).encode("utf-8"))
print("\033[32minitiating the frames transmission using checksum error detection...\033[0m\n")
time.sleep(3)

index = 0
while index < len(frames):
    header = frames[index][0]
    seq = header["seq"]
    temp_frame = frames[index].copy()
    frame_bytes = json.dumps(temp_frame).encode("utf-8")
    sender_socket.send(frame_bytes)
    print(f"\033[32mframe sent:\033[0m {temp_frame}\n")
    sender_socket.settimeout(5)
    try:
        ack = int(sender_socket.recv(1024).decode())
        if ack == 1 - seq:
            print(f"\033[32mcurrent frame is received by the receiver sucessfully...\033[0m\n")
            index += 1
        else:
            print(f"\033[31mWrong ack from receiver...\033[0m\n")
    except socket.timeout:
        print(f"\033[31mFrame has lost, retransmiting...\033[0m\n")


print(f"\033[32mAll frames sent successfully\033[0m\n"
)
sender_socket.close()