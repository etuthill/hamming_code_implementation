# work in progress, abandoned 
# basically subbing out need for syndrome table with just party
# check polynomial

import random

# Generator polynomial g(x) = x^3 + x + 1 
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
    dividend = dividend[:]
    divisor_len = len(divisor)
    while dividend and dividend[0] == 0:
        dividend.pop(0)
    while len(dividend) >= divisor_len:
        if dividend[0] == 1:
            for i in range(divisor_len):
                dividend[i] ^= divisor[i]
        dividend.pop(0)
        while dividend and dividend[0] == 0:
            dividend.pop(0)
    return dividend

def encode_cyclic_hamming(data_bits):
    extended = data_bits + [0, 0, 0]  # shift by x^3
    remainder = poly_mod(extended, G)
    remainder = [0]*(3 - len(remainder)) + remainder
    codeword = [extended[i] ^ remainder[i-4] if i >= 4 else extended[i] for i in range(7)]
    return codeword

def introduce_error_random(codeword):
    pos = random.randint(0, 6)
    codeword[pos] ^= 1
    print(f"Introduced error at bit {pos+1}")

def compute_syndrome_register(codeword):
    """
    Circuit-like syndrome computation using H(x) shift register.
    Returns syndrome as 4 bits (length of H(x)-1)
    """
    reg = [0]*(len(H)-1)
    for bit in codeword:
        feedback = bit ^ reg[0]
        # shift left
        for i in range(len(reg)-1):
            if H[i+1] == 1:
                reg[i] = reg[i+1] ^ feedback
            else:
                reg[i] = reg[i+1]
        reg[-1] = feedback if H[-1]==1 else 0
    return reg

def fix_error_circuit(codeword):
    """
    Correct a single-bit error using syndrome.
    """
    syn = compute_syndrome_register(codeword)
    if sum(syn) == 0:
        print("No error detected.")
        return codeword
    
    for i in range(len(codeword)):
        test = codeword[:]
        test[i] ^= 1
        test_syn = compute_syndrome_register(test)
        if sum(test_syn) == 0:
            print(f"Error detected at position {i+1}")
            return test
    
    print("Error could not be corrected (multiple errors?)")
    return codeword

def main():
    data_bits = get_user_bits()
    codeword = encode_cyclic_hamming(data_bits)
    print("Cyclic Hamming codeword:", codeword)

    introduce_error_random(codeword)
    print("Codeword with error:", codeword)

    corrected = fix_error_circuit(codeword)
    print("Corrected codeword:", corrected)

if __name__ == "__main__":
    main()
