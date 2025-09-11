import socket
import json
import math

receiver_socket = socket.socket()
print("Receiver socket is created")

receiver_socket.bind(('localhost', 9999))
receiver_socket.listen(1)

sender_socket, sender_address = receiver_socket.accept()
print(f"\033[32mSuccessfully connected with the sender {sender_address}.\033[0m\n")

frames = []
no_frames = int(sender_socket.recv(1204).decode())
count = 0
expected_seq = 0

# Simulate intentional packet loss at middle frame (same rule as Stop-and-Wait)
frame_loss = math.ceil(no_frames / 2)
loss = True

while count < no_frames:
    json_frame = sender_socket.recv(1204).decode()
    if not json_frame:
        break

    frame = json.loads(json_frame)
    header = frame[0]
    seq = header["seq"]

    if loss and seq == frame_loss:
        print(f"\033[31mSimulated loss at frame seq={seq}\033[0m\n")
        loss = False
        # Do not ACK → sender will timeout
        continue

    if seq == expected_seq:
        frames.append(frame)
        print(f"\033[32mFrame received correctly:\033[0m seq={seq}\n")
        sender_socket.send(str(seq).encode("utf-8"))  # cumulative ACK
        expected_seq += 1
        count += 1
    else:
        # send last ACK again (cumulative)
        sender_socket.send(str(expected_seq - 1).encode("utf-8"))
        print(f"\033[33mOut-of-order frame {seq} discarded, sent duplicate ACK {expected_seq-1}\033[0m\n")

# Reassemble frames
data = ""
for frame in frames:
    header, payload, trailer = frame
    padding = trailer["padding"]
    if padding > 0:
        payload = payload[:-padding]
    for i in range(0, len(payload), 8):
        byte = payload[i:i + 8]
        if len(byte) == 8:
            data += chr(int(byte, 2))

print(f"Received data: {data}\n")

# close connections
sender_socket.close()
receiver_socket.close()
