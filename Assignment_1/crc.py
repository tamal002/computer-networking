
import random

# computing the remainder of crc
def compute_crc(payload, generator):
    """
    payload: binary string (with appended zeros already)
    generator: binary string of polynomial (e.g. "1101" for x^3 + x^2 + 1)
    """
    payload = list(payload)  # easier to modify
    gen_len = len(generator)

    for i in range(len(payload) - gen_len + 1):
        # Only divide if the current bit is '1'
        if payload[i] == '1':
            for j in range(gen_len):
                # XOR with generator polynomial
                payload[i + j] = str(int(payload[i + j] != generator[j]))

    # remainder is the last (gen_len-1) bits
    remainder = ''.join(payload[-(gen_len-1):])
    return remainder


# set the crc fields in sender's data
def set_crc(frame, test=False):
    CRC_POLYNOMIALS = {
        8: "111010101",
        10: "11000110011",
        16: "11000000000000101",
        32: "100000100110000010001110110110111"
    }
    
    if test == True:
        generator = CRC_POLYNOMIALS[8]
    else:
        degree = random.choice(list(CRC_POLYNOMIALS.keys()))
        generator = CRC_POLYNOMIALS[degree]

    payload = frame[1]
    trailor = frame[2]

    new_payload = payload + '0' * (len(generator) - 1)
    remainder = compute_crc(new_payload, generator)
    trailor["crc"] = remainder
    trailor["generator"] = generator

    return frame


# detecting the error at receiver side
def verify_crc(frames):
    for frame in frames:
        payload = frame[1]
        trailor = frame[2]
        remainder = trailor["crc"]
        generator = trailor["generator"]

        result = compute_crc(payload + remainder, generator)

        if int(result, 2) != 0:
            return False
    return True
            


# def verify_crc(frames):
#     for frame in frames:
#         payload = frame[1]
#         received_crc = frame[2]["crc"]
#         generator = frame[2]["generator"]

#         # Recompute CRC
#         computed_crc = compute_crc(payload, generator)

#         print(f"Payload: {payload}")
#         print(f"Received CRC: {received_crc}")
#         print(f"Computed CRC: {computed_crc}")

#         if computed_crc != received_crc:
#             return False
#     return True



