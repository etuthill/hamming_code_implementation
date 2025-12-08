import random

def get_user_bits():
    """
    Prompt for 4 bits and return them as a list of ints.
    """
    while True:
        raw = input("Enter 4 bits (e.g. 1011): ").strip()

        # check length + only 0/1
        if len(raw) == 4 and all(c in "01" for c in raw):
            return [int(b) for b in raw]

        print("Invalid input. Please enter exactly 4 bits like 0101.")


def encode_hamming74(data_bits):
    """
    Encode 4 data bits into a Hamming (7,4) codeword.
    """
    d1, d2, d3, d4 = data_bits

    # parity bits - calculated using XOR
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p3 = d2 ^ d3 ^ d4

    # final layout
    return [p1, p2, d1, p3, d2, d3, d4]

def introduce_error_random(codeword):
    error_positions = random.sample(range(1), 1) # random positions for errors
    for pos in error_positions:
        codeword[pos] ^= 1  # flip the bit

def fix_errors(codeword):
    """
    Detect and correct errors in a Hamming (7,4) codeword.
    """
    p1, p2, d1, p3, d2, d3, d4 = codeword

    # parity checks
    c1 = p1 ^ d1 ^ d2 ^ d4
    c2 = p2 ^ d1 ^ d3 ^ d4
    c3 = p3 ^ d2 ^ d3 ^ d4

    # find error position
    error_position = c1 * 1 + c2 * 2 + c3 * 4

    if error_position != 0:
        print(f"Error detected at position: {error_position}")
        codeword[error_position - 1] ^= 1  # correct error

    return codeword

def main():
    data_bits = get_user_bits()
    codeword = encode_hamming74(data_bits)
    print("Hamming codeword:", codeword)
    introduce_error_random(codeword)
    print("Codeword with introduced errors:", codeword)
    corrected_codeword = fix_errors(codeword)
    print("Corrected codeword:", corrected_codeword)

if __name__ == "__main__":
    main()
