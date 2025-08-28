
import socket
import json
from checksum import verify_checksum
from crc import verify_crc

receiver_socket = socket.socket()
print("Receiver socket is created")

receiver_socket.bind(('localhost', 9999))
receiver_socket.listen(1)

sender_socket, sender_address = receiver_socket.accept()
print(f"\033[32mSuccessfully connected with the sender {sender_address}.\033[0m\n")

final_data = {"checksum": "", "crc": ""}

# for checksum
stay_connected = True
while stay_connected:
    frames = []
    no_of_frames = sender_socket.recv(1024).decode("utf-8")
    no_of_frames = int(no_of_frames)

    # read one batch of frames 
    while no_of_frames != 0:
        frame = sender_socket.recv(1024).decode("utf-8")
        frame = json.loads(frame)
        print(f"\033[32mReceived frame:\033[0m {frame}\n")
        frames.append(frame)
        no_of_frames -= 1

    no_error = verify_checksum(frames)
    if not no_error:
        print("\033[31mThe received data is corrupted.\033[0m\n")
        choice = input("Do you want retransmission [y/n]: ")
        print("\n")
        sender_socket.send(choice.encode("utf-8"))
        if choice == 'n':
            stay_connected = False
    else:
        print("\033[32mAll frames are received correctly.\033[0m\n")
        sender_socket.send(b"n")  # tell sender no retransmission
        final_data["checksum"] = frames.copy()
        stay_connected = False


# for crc
stay_connected = True
while stay_connected:
    frames = []
    no_of_frames = sender_socket.recv(1024).decode("UTF-8").strip()
    no_of_frames = int(no_of_frames)

    # read one batch of frames 
    while no_of_frames != 0:
        frame = sender_socket.recv(1024).decode("UTF-8")
        frame = json.loads(frame)
        print(f"\033[32mReceived frame:\033[0m {frame}\n")
        frames.append(frame)
        no_of_frames -= 1

    no_error = verify_crc(frames)
    if not no_error:
        print("\033[31mThe received data is corrupted.\033[0m\n")
        choice = input("Do you want retransmission [y/n]: ")
        print("\n")
        sender_socket.send(choice.encode("utf-8"))
        if choice == 'n':
            stay_connected = False
    else:
        print("\033[32mAll frames are received correctly.\033[0m\n")
        sender_socket.send(b"n")  # telling sender for not to retransmit
        final_data["crc"] = frames.copy()
        stay_connected = False

print("\n")
print("----------Final received data--------------\n")

for key, value in final_data.items():
    scheme = key
    frames = value
    
    data = ""
    for frame in frames:
        header, payload, trailer = frame
        padding = trailer["padding"]
        if padding > 0:
            payload = payload[:-padding]
        binary_data = payload
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i+8]
            if len(byte) == 8:
                data += chr(int(byte, 2))
    print(f"scheme: {scheme}\nreceived data: {data}\n")


# connection termination
sender_socket.close()
receiver_socket.close()


