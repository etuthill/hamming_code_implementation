import random

# generator polynomial g(x) = x^3 + x + 1 
G = [1, 0, 1, 1]

# Parity-check polynomial h(x) = x^4 + x^2 + x + 1
H = [1, 0, 1, 1, 1]

def get_user_bits():
    while True:
        raw = input("Enter 4 bits (e.g. 1011): ").strip()
        if len(raw) == 4 and all(c in "01" for c in raw):
            return [int(b) for b in raw]
        print("Invalid input. Please enter exactly 4 bits.")

def poly_mod(dividend, divisor):
    """
    Polynomial division over GF(2), MSB-first.
    Returns the remainder with leading zeros trimmed.
    """
    dividend = dividend[:]  # copy
    divisor_len = len(divisor)

    # remove leading zeros in dividend
    while dividend and dividend[0] == 0:
        dividend.pop(0)

    while len(dividend) >= divisor_len:
        if dividend[0] == 1:
            for i in range(divisor_len):
                dividend[i] ^= divisor[i]
        dividend.pop(0)
        # trim leading zeros after each step
        while dividend and dividend[0] == 0:
            dividend.pop(0)

    return dividend 

def encode_cyclic_hamming(data_bits):
    """
    Encode 4 data bits into 7 bit codeword.
    """
    # multiply by x^3 append 3 zeros
    extended = data_bits + [0, 0, 0]

    # remainder
    remainder = poly_mod(extended, G)

    # remainder to length 3
    remainder = [0] * (3 - len(remainder)) + remainder

    # add remainder (xor)
    codeword = [extended[i] ^ remainder[i - 4] if i >= 4 else extended[i]
                for i in range(7)]

    return codeword

def introduce_error_random(codeword):
    pos = random.randint(0, 6)
    codeword[pos] ^= 1
    print(f"Introduced error at bit {pos+1}")

def syndrome(codeword):
    syn = poly_mod(codeword, G)
    # always pad to 3 bits
    return [0] * (3 - len(syn)) + syn

def build_syndrome_table():
    table = {}
    for pos in range(7):
        e = [0]*7
        e[pos] = 1
        syn = syndrome(e)
        s_val = int("".join(map(str, syn)), 2)
        table[s_val] = pos
    return table

def fix_errors(codeword):
    """
    Correct a single-bit error using a precomputed syndrome lookup table.
    """

    syn = syndrome(codeword)
    
    # convert syndrome bits to integer
    s_val = int("".join(map(str, syn)), 2)

    if s_val == 0:
        print("No error detected.")
        return codeword
    
    syndrome_table = build_syndrome_table()

    if s_val in syndrome_table:
        pos = syndrome_table[s_val]
        print(f"Error detected at position {pos+1}")
        codeword[pos] ^= 1
    else:
        print("Unrecognized syndrome (multiple errors?)")

    return codeword

def main():
    data_bits = get_user_bits()
    codeword = encode_cyclic_hamming(data_bits)
    print("Cyclic Hamming codeword:", codeword)

    introduce_error_random(codeword)
    print("Codeword with error:", codeword)

    corrected = fix_errors(codeword)
    print("Corrected codeword:", corrected)

if __name__ == "__main__":
    main()
