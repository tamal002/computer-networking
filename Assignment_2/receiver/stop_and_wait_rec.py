import socket
import json

receiver_socket = socket.socket()
print("Receiver socket is created")

receiver_socket.bind(('localhost', 9999))
receiver_socket.listen(1)

sender_socket, sender_address = receiver_socket.accept()
print(f"\033[32mSuccessfully connected with the sender {sender_address}.\033[0m\n")


frames = []
no_frames = int(sender_socket.recv(1204).decode())
count = 0
ack = 0
while count < no_frames:
    json_frame = sender_socket.recv(1204).decode()
    frame = json.loads(json_frame)
    header = frame[0]
    seq = header["seq"]
    if seq == ack:
        ack = 1 - ack
        sender_socket.send(str(ack).encode("utf-8"))
        frames.append(frame)
        count += 1
    
# reassembling the frames and retrieving the data.
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
print(f"received data: {data}\n")


# connection termination
sender_socket.close()
receiver_socket.close()

