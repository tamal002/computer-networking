
import socket
import json
from crc import set_crc
from checksum import set_checksum
from error_injection import inject_error, detected_by_both, detected_by_crc_only, detected_by_checksum_only
import time


sender_socket = socket.socket()
print("\033[32mSender socket is created\033[0m")

sender_socket.connect(('localhost', 9999))
print("\033[32msuccessfuly connected with receiver.\033[0m\n")

# reading data from dataword.txt file
with open("dataword.txt", "r", encoding="utf-8") as f:
    text_data = f.read().strip()

print(f"your data: {text_data}\n")

# converting the string data into binary string
binary_data = ''.join(format(ord(char), '08b') for char in text_data)
print(f"your data in binary form: {binary_data}\n")

# size of each frame will be 64 bit -> 8 characters per frame
frame_size = 64

# Header structure
header = {
    "sender_address": '127.0.0.1',
    "receiver_address": "127.0.0.1",
    "number_of_errors": "",
    "error_positions": []
}

# Trailor structure
trailer_template = {
    "padding" : -1,
    "crc" : -1, 
    "generator": -1,
    "checksum" : -1,
}


# framing the data
n = len(binary_data)
padding = 0
frames = []
for i in range(0, n, frame_size):
    frame = []
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



# for checksum
print("--------- Scheme: checksum ---------\n")
transmit = True
error = True
while transmit:
    no_of_frames = len(frames)
    sender_socket.send(str(no_of_frames).encode("utf-8"))
    print("\033[32minitiating the frames transmission using checksum error detection...\033[0m\n")
    time.sleep(3)
    for frame in frames:
        temp = frame.copy()
        temp = set_checksum(temp) # checksum calculation
        if(error): # injecting error
            temp = inject_error(temp) 
            print("\033[31mError injected successfuly...\033[0m")
        frame_bytes = json.dumps(temp).encode("utf-8")
        sender_socket.send(frame_bytes)
        print(f"\033[32mframe sent:\033[0m {temp}\n")
        time.sleep(3)
    # getting know if the receiver wants the retransmition or not .
    respose_from_server = sender_socket.recv(1024).decode("UTF-8")
    if(respose_from_server == 'y' or respose_from_server == 'Y'):
        error = False
    else:
        transmit = False
        
time.sleep(3)

# for crc
print("--------- Scheme: crc ---------\n")
transmit = True
error = True
while transmit:
    no_of_frames = len(frames)
    sender_socket.send(str(no_of_frames).encode("utf-8"))
    print("\033[32minitiating the frames transmission using CRC error detection...\033[0m\n")
    time.sleep(3)
    for frame in frames:
        temp = frame.copy()
        temp = set_crc(temp) # checksum calculation
        if(error): # injecting error
            temp = inject_error(temp) 
            print("\033[31mError injected successfuly...\033[0m")
        frame_bytes = json.dumps(temp).encode("utf-8")
        sender_socket.send(frame_bytes)
        print(f"\033[32mframe sent:\033[0m {temp}\n")
        time.sleep(3)
    # getting know if the receiver wants the retransmition or not .
    respose_from_server = sender_socket.recv(1024).decode("UTF-8")
    if(respose_from_server == 'y' or respose_from_server == 'Y'):
        error = False
    else:
        transmit = False

'''
                                            | working note | 

=>  json.dumps() converts a Python object (list/dict/string/number) into a JSON string.

    Example:
    json.dumps(frame)
    gives something like: '[{"HOST": "127.0.0.1", "PORT": 5000}, "0101010101...", {"padding": 2, "crc": "101"}]'

    Now it’s just a normal string in JSON format.

=>  .encode("utf-8")
    Converts that JSON string into bytes (because sockets only send bytes).

    Example: b'[{"HOST": "127.0.0.1", "PORT": 5000}, "0101010101...", {"padding": 2, "crc": "101"}]'

'''


# closing the connection.
sender_socket.close()


    


