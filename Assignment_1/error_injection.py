
import random

# For geberal usecase
def inject_error(frame):
    number_of_erros = random.randint(0, 5)
    payload = list(frame[1])   # convert string → list of chars (mutable) since string is immutable in python
    header = frame[0]
    header["number_of_errors"] = str(number_of_erros)
    while number_of_erros >= 1:
        error_position = random.randint(0, 63)
        if payload[error_position] == '0':
            payload[error_position] = '1'
        else:
            payload[error_position] = '0'
        header["error_positions"].append(error_position)
        number_of_erros -= 1
    frame[1] = "".join(payload)  # back to string
    return frame


# For desired scenaio cases


def detected_by_both(frame):
    payload = list(frame[1])
    header = frame[0]
    payload[18] = '1'
    header["number_of_errors"] = str(1)
    header["error_positions"].append(18)
    frame[1] = "".join(payload)
    return frame


def detected_by_crc_only(frame):
    payload = list(frame[1])
    header = frame[0]
    payload[31] = '1'
    payload[39] = '0'
    header["number_of_errors"] = str(2)
    header["error_positions"] = [31, 39]
    frame[1] = "".join(payload)
    return frame



def detected_by_checksum_only(frame):
    payload = list(frame[1])
    
    if payload[18] == '1':
        payload[18] = '0'
    else:
        payload[18] = '1'
    
    frame[1] = "".join(payload)
    return frame
