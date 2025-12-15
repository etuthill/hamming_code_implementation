import random

# Generator polynomial g(x) = x^3 + x + 1
G = [1, 0, 1, 1]


def get_user_bits():
    while True:
        raw = input("Enter 4 bits (e.g. 1011): ").strip()
        if len(raw) == 4 and all(c in "01" for c in raw):
            return [int(b) for b in raw]
        print("Invalid input.")


def poly_mod(dividend, divisor):
    dividend = dividend[:]
    while len(dividend) >= len(divisor):
        if dividend[0] == 1:
            for i in range(len(divisor)):
                dividend[i] ^= divisor[i]
        dividend.pop(0)
    return dividend


def encode_cyclic_hamming(data_bits):
    extended = data_bits + [0] * (len(G) - 1)
    remainder = poly_mod(extended, G)
    remainder = [0] * (len(G) - 1 - len(remainder)) + remainder
    return data_bits + remainder


def introduce_error_random(codeword):
    pos = random.randint(0, 6)
    codeword[pos] ^= 1
    print(f"Introduced error at bit {pos + 1}")


def syndrome(codeword):
    """True cyclic syndrome"""
    return poly_mod(codeword, G)


def generate_syndrome_table():
    table = {}
    for i in range(7):
        e = [0] * 7
        e[i] = 1
        syn = tuple(syndrome(e))
        table[syn] = i
    return table


SYNDROME_TABLE = generate_syndrome_table()


def fix_error(codeword):
    syn = syndrome(codeword)

    if all(b == 0 for b in syn):
        print("No error detected.")
        return codeword

    syn_t = tuple(syn)
    if syn_t in SYNDROME_TABLE:
        pos = SYNDROME_TABLE[syn_t]
        print(f"Error detected at bit {pos + 1}")
        corrected = codeword[:]
        corrected[pos] ^= 1
        return corrected
    else:
        print("Uncorrectable error.")
        return codeword


def main():
    data_bits = get_user_bits()
    codeword = encode_cyclic_hamming(data_bits)
    print("Cyclic Hamming codeword:", codeword)

    introduce_error_random(codeword)
    print("Codeword with error:", codeword)

    corrected = fix_error(codeword)
    print("Corrected codeword:", corrected)


if __name__ == "__main__":
    main()
