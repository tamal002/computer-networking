
import socket
import json
from checksum import verify_checksum

receiver_socket = socket.socket()
print("Receiver socket is created")

receiver_socket.bind(('localhost', 9999))
receiver_socket.listen(1)

sender_socket, sender_address = receiver_socket.accept()
print(f"Successfully connected with the sender {sender_address}.")



stay_connected = True
while stay_connected:

    frames = []

    no_of_frames = sender_socket.recv(1024).decode("UTF-8").strip()
    no_of_frames = int(no_of_frames)

    # read one batch of frames 
    while no_of_frames != 0:
        frame = sender_socket.recv(1024).decode("UTF-8")
        frame = json.loads(frame)
        print(f"Received frame: {frame}")
        frames.append(frame)
        no_of_frames -= 1

    no_error = verify_checksum(frames)
    if not no_error:
        print("The received data is corrupted.")
        choice = input("Do you want retransmission [y/n]: ")
        sender_socket.send(choice.encode("utf-8"))
    else:
        print("All frames received correctly.")
        sender_socket.send(b"n")  # tell sender no retransmission
        stay_connected = False


final_data = ""
for frame in frames:
    header, payload, trailer = frame
    if frame == frames[len(frames)-1]:
        padding = trailer["padding"]
        if padding > 0:
            payload = payload[:-padding]
    binary_data = payload
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) == 8:
            final_data += chr(int(byte, 2))

print(f"Received final data: [ {final_data} ]")

sender_socket.close()
receiver_socket.close()



################################### older code ############################################


# import socket
# import json
# #from crc import crc
# from checksum import verify_checksum


# receiver_socket = socket.socket()
# print("Receiver socket is created")

# receiver_socket.bind(('localhost', 9999))

# # The maximum number (here 3) of unaccepted connections the server will queue before refusing new ones.
# receiver_socket.listen(1) 

# sender_socket, sender_address = receiver_socket.accept()
# print(f"successfuly connected with the sender {sender_address}.")

# buffer = sender_socket.makefile("r", encoding="UTF-8")

# stay_connected = True
# while stay_connected:
#     no_error = True
#     frames = []

#     for line in buffer:  # read until sender finishes this batch
#         line = line.strip()
#         if not line:
#             continue
#         frame = json.loads(line)
#         print(f"Received frame: {frame}")
#         no_error = no_error and verify_checksum(frame)
#         frames.append(frame)

#     if no_error == False:
#         print("The received data is corrupted.")
#         choice = str(input("do you want retransmision [y/n]: "))
#         sender_socket.send(bytes(choice, "utf-8"))
#     else:
#         stay_connected = False




# receiver_socket.close()

# sender_socket.close()


