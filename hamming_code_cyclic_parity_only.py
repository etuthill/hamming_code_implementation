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
    while dividend and dividend[0] == 0:
        dividend.pop(0)

    while len(dividend) >= len(divisor):
        if dividend[0] == 1:
            for i in range(len(divisor)):
                dividend[i] ^= divisor[i]
        dividend.pop(0)
        while dividend and dividend[0] == 0:
            dividend.pop(0)

    return dividend


def encode_cyclic_hamming(data_bits):
    extended = data_bits + [0, 0, 0]
    remainder = poly_mod(extended, G)
    remainder = [0] * (3 - len(remainder)) + remainder

    codeword = []
    for i in range(7):
        if i < 4:
            codeword.append(extended[i])
        else:
            codeword.append(extended[i] ^ remainder[i - 4])

    return codeword


def introduce_error_random(codeword):
    pos = random.randint(0, 6)
    codeword[pos] ^= 1
    print(f"Introduced error at bit {pos + 1}")


def compute_syndrome_register(codeword):
    reg = [0] * (len(H) - 1)

    for bit in reversed(codeword):
        feedback = bit ^ reg[0]

        for i in range(len(reg) - 1):
            if H[i + 1] == 1:
                reg[i] = reg[i + 1] ^ feedback
            else:
                reg[i] = reg[i + 1]

        reg[-1] = feedback if H[-1] == 1 else 0

    return reg


def syndrome_lfsr_step(reg):
    feedback = reg[0]
    new = [0] * len(reg)

    for i in range(len(reg) - 1):
        if H[i + 1] == 1:
            new[i] = reg[i + 1] ^ feedback
        else:
            new[i] = reg[i + 1]

    new[-1] = feedback if H[-1] == 1 else 0
    return new


def unit_syndrome():
    """
    Syndrome corresponding to a single error in the LSB position.
    This defines the correct polynomial basis for this LFSR.
    """
    cw = [0, 0, 0, 0, 0, 0, 1]
    return compute_syndrome_register(cw)


def find_error_position_from_syndrome(syn, n):
    target = unit_syndrome()
    reg = syn[:]

    for shift in range(n):
        if reg == target:
            return shift
        reg = syndrome_lfsr_step(reg)

    return None


def fix_error_circuit(codeword):
    syn = compute_syndrome_register(codeword)

    if sum(syn) == 0:
        print("No error detected.")
        return codeword

    pos = find_error_position_from_syndrome(syn, len(codeword))

    if pos is None:
        print("Error could not be corrected (multiple errors?)")
        return codeword

    print(f"Error detected at position {pos + 1}")
    corrected = codeword[:]
    corrected[pos] ^= 1
    return corrected


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
