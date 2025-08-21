'''

=> We will devide the code words into chuncks where each chunks will be of 16 bit.

=> let say our datawords is [HELLO], now each character will be converted into ASCII and then the decimal 
   ASCII will be converted into binary. 

'''

# frame[0: header{HOST, PORT}, 1: payload, 2: trailer{padding, crc, checksum}]

# set checksum
def set_checksum(frame):
   checksum = 0
   data_sum = 0
   payload = frame[1]
   trailer = frame[2]
   for i in range(0, len(payload), 8):
      binary_data = payload[i : i + 8]
      decimal_data = int(binary_data, 2)
      data_sum += decimal_data
   checksum = -data_sum
   trailer["checksum"] = checksum
   return frame



#verifying the checksum
def verify_checksum(frames):
   for frame in frames:
      payload = frame[1]
      trailer = frame[2]
      received_checksum = trailer["checksum"]

      computed_sum = 0
      for i in range(0, len(payload), 8):
         binary_data = payload[i : i + 8]
         decimal_data = int(binary_data, 2)
         computed_sum += decimal_data
      if (computed_sum + received_checksum) != 0:
         return False
   return True



   