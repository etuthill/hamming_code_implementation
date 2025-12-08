import random

# generator
G = [
    [1, 0, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 1],
    [0, 0, 1, 0, 0, 1, 1],
    [0, 0, 0, 1, 1, 1, 1],
]

# parity-check
H = [
    [1, 0, 1, 0, 1, 0, 1],
    [0, 1, 1, 0, 0, 1, 1],
    [0, 0, 0, 1, 1, 1, 1],
]

def get_user_bits():
    while True:
        raw = input("Enter 4 bits (e.g. 1011): ").strip()
        if len(raw) == 4 and all(c in "01" for c in raw):
            return [int(b) for b in raw]
        print("Invalid input. Please enter exactly 4 bits.")

def matrix_multiply_vec(M, v):
    """
    Multiply matrix M by vector v over GF(2).
    """
    return [
        sum(mij * vj for mij, vj in zip(row, v)) % 2
        for row in M
    ]


def encode_hamming74(data_bits):
    """
    Encoding: treat data_bits as a length-4 row vector and multiply
    on the left by G to produce a length-7 codeword.
    result[j] = sum_i data_bits[i] * G[i][j] (mod 2)
    """
    n_cols = len(G[0])
    k = len(G)
    return [
        sum(data_bits[i] * G[i][j] for i in range(k)) % 2
        for j in range(n_cols)
    ]


def introduce_error_random(codeword):
    """
    Flip one random bit.
    """
    pos = random.randint(0, 6)
    codeword[pos] ^= 1


def fix_errors(codeword):
    """
    Compute H * codeword and correct a single-bit error
    """
    syndrome = matrix_multiply_vec(H, codeword)
    s_val = syndrome[0] * 1 + syndrome[1] * 2 + syndrome[2] * 4
    if s_val != 0:
        print(f"Error detected at position {s_val}")
        codeword[s_val - 1] ^= 1
    return codeword



def main():
    data_bits = get_user_bits()
    codeword = encode_hamming74(data_bits)
    print("Hamming codeword:", codeword)

    introduce_error_random(codeword)
    print("Codeword with introduced eWrror:", codeword)

    corrected = fix_errors(codeword)
    print("Corrected codeword:", corrected)


if __name__ == "__main__":
    main()
