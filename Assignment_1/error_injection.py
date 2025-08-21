
import random

def inject_error(frame):
    number_of_erros = random.randint(0, 5)
    payload = list(frame[1])   # convert string → list of chars (mutable) since string is immutable in python
    while number_of_erros >= 1:
        error_position = random.randint(0, 63)
        if payload[error_position] == '0':
            payload[error_position] = '1'
        else:
            payload[error_position] = '0'
        number_of_erros -= 1
    frame[1] = "".join(payload)  # back to string
    return frame