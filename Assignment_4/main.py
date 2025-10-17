import numpy as np

# ANSI color codes for better readability
class Color:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"

def is_power_of_two(n):
    """Check if a number is a power of two."""
    return (n > 0) and (n & (n - 1) == 0)

def generate_walsh_codes(n):
    """Recursively generate n x n Walsh-Hadamard matrix."""
    # base case
    if n == 1:
        return np.array([[1]])
    h_prev = generate_walsh_codes(n // 2)
    h_top = np.hstack((h_prev, h_prev))
    h_bottom = np.hstack((h_prev, -h_prev))
    return np.vstack((h_top, h_bottom))

def main():
    print(f"{Color.HEADER}{Color.BOLD}CDMA Channel Simulation using Walsh Codes{Color.END}")
    print(f"{Color.CYAN}{'-'*60}{Color.END}")

    # Step 1: Number of stations
    while True:
        try:
            num_stations = int(input(f"{Color.YELLOW}Enter number of stations (2, 4, 8...): {Color.END}"))
            if is_power_of_two(num_stations):
                break
            else:
                print(f"{Color.RED} Must be a power of two! Try again.{Color.END}")
        except ValueError:
            print(f"{Color.RED} Invalid input! Enter a number.{Color.END}")

    # Step 2: Generate Walsh codes
    walsh_codes = generate_walsh_codes(num_stations)
    print(f"\n{Color.GREEN}{Color.BOLD}Generated Walsh Codes:{Color.END}")
    for i, code in enumerate(walsh_codes):
        print(f"  Station {i+1} Code (C{i+1}): {Color.CYAN}{code}{Color.END}")

    # Step 3: Data input
    data_bits = []
    print(f"\n{Color.BLUE}{Color.BOLD}Enter the data bit (0 or 1) for each station:{Color.END}")
    for i in range(num_stations):
        while True:
            try:
                bit = int(input(f"  Station {i+1} → d{i+1}: "))
                if bit in [0, 1]:
                    data_bits.append(-1 if bit == 0 else 1)
                    break
                else:
                    print(f"{Color.RED} Enter 0 or 1 only.{Color.END}")
            except ValueError:
                print(f"{Color.RED} Invalid input! Enter 0 or 1.{Color.END}")

    print(f"\nOriginal Data Bits (d): {Color.YELLOW}{np.array(data_bits)}{Color.END}")

    # Step 4: Encoding
    encoded_signals = []
    print(f"\n{Color.GREEN}{Color.BOLD}Encoding Each Station's Data:{Color.END}")
    for i in range(num_stations):
        encoded_signal = data_bits[i] * walsh_codes[i]
        encoded_signals.append(encoded_signal)
        print(f"  Station {i+1}: {Color.CYAN}{encoded_signal}{Color.END}")

    # Step 5: Combine all signals on channel
    channel_signal = np.sum(encoded_signals, axis=0)
    print(f"\n{Color.YELLOW}{Color.BOLD}Shared Channel Signal (Sum of all):{Color.END}")
    print(f"  {Color.BLUE}{channel_signal}{Color.END}")

    # Step 6: Decode for chosen station
    print(f"\n{Color.CYAN}{'-'*60}{Color.END}")
    print(f"{Color.BOLD} Data Reconstruction at Receiver{Color.END}")
    print(f"{Color.CYAN}{'-'*60}{Color.END}")

    while True:
        try:
            target_station = int(input(f"Decode which station? (1-{num_stations}): "))
            if 1 <= target_station <= num_stations:
                break
            else:
                print(f"{Color.RED} Invalid station index.{Color.END}")
        except ValueError:
            print(f"{Color.RED} Invalid input! Enter a number.{Color.END}")

    target_code = walsh_codes[target_station - 1]
    dot_product = np.dot(channel_signal, target_code)
    recovered_data = dot_product / num_stations

    recovered_bit = 1 if recovered_data > 0 else 0
    original_bit = 1 if data_bits[target_station - 1] > 0 else 0

    print(f"\n{Color.BOLD}Decoding using C{target_station}:{Color.END} {Color.CYAN}{target_code}{Color.END}")
    print(f"{Color.YELLOW}Dot Product = {dot_product}, Normalized = {recovered_data}{Color.END}")
    print(f"\n{Color.GREEN if recovered_bit==original_bit else Color.RED}Result for Station {target_station}:{Color.END}")
    print(f"  Original Bit: {Color.BLUE}{original_bit}{Color.END}")
    print(f"  Recovered Bit: {Color.BLUE}{recovered_bit}{Color.END}")

    if original_bit == recovered_bit:
        print(f"{Color.GREEN} Perfect Reconstruction Successful!{Color.END}")
    else:
        print(f"{Color.RED}❌ Reconstruction Error!{Color.END}")

    print(f"{Color.CYAN}{'-'*60}{Color.END}")

if __name__ == "__main__":
    main()
