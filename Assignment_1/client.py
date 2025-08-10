# client is the sender here

import socket

sender_socket = socket.socket()

sender_socket.connect(('localhost', 9999))

# reading data from dataword.txt file
with open("dataword.txt", "r", encoding="utf-8") as f:
    text_data = f.read().strip()

print(f"your data: {text_data}")

# converting the string data into binary string
binary_data = ''.join(format(ord(char), '08b') for char in text_data)
print(f"your data in binary form: {binary_data}")

# size of each frame will be 64 bit -> 8 characters per frame
frame_size = 64

# the payload which will be actually send as the real data
payload = []
n = len(binary_data)
start = 0
padding = 0

for i in range(start, n, frame_size):
    frame = binary_data[start : start + frame_size]
    start += frame_size
    print(len(frame))

    if len(frame) < frame_size: # need to pad
        need = frame_size - len(frame)
        frame += '0' * need
        padding = need

    payload.append(frame)


# crc / check sum method call


# error_injection method call



# Sending something like data/other to the reciever...
for frame in payload:
    frame_bytes = int(frame, 2).to_bytes(len(frame) // 8, byteorder="big")
    sender_socket.send(frame_bytes)

'''

working note:

=>  int(frame, 2)
    frame is something like:
    "0100100001100101011011000110110001101111"

=>  int(frame, 2) tells Python:
    "Interpret this string as a base-2 (binary) number".

Example:
"01000001" → 65 (because 0b01000001 = decimal 65, which is 'A' in ASCII).

So now we have the binary number in integer form.

=>  .to_bytes(len(frame) // 8, byteorder="big")
    Converts that integer into actual bytes (raw binary representation).

=>  len(frame) // 8 = number of bytes in this frame (because 8 bits = 1 byte).
    Example: if frame length = 64 bits → 64 // 8 = 8 bytes.

=>  "big" means big-endian (most significant byte first, like normal network order).

'''


# receiving the response from the receiver
respose_from_server = sender_socket.recv(1024).decode() 
print(respose_from_server)

sender_socket.close()


    


