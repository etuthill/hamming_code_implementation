import random

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# generator polynomial g(x) = x^3 + x + 1 
G = [1, 0, 1, 1]

# Parity-check polynomial h(x) = x^4 + x^2 + x + 1
H = [1, 0, 1, 1, 1]

def get_user_bits():
    while True:
        raw = input("Enter 4 bits: ").strip()
        if len(raw) == 4 and all(c in "01" for c in raw):
            return [int(b) for b in raw]
        print("Invalid input. Please enter exactly 4 bits.")

def bits_to_poly(bits):
    """
    Convert bit coefficients (MSB first) into a readable polynomial string.
    """
    degree = len(bits) - 1
    terms = []
    for i, bit in enumerate(bits):
        if bit == 0:
            continue
        power = degree - i
        if power == 0:
            terms.append("1")
        elif power == 1:
            terms.append("x")
        else:
            terms.append(f"x^{power}")
    return " + ".join(terms) if terms else "0"

def format_bits(bits):
    return "  ".join(str(b) for b in bits)

def pad_left(bits, width):
    """Left-pad a bit vector with zeros to a target width."""
    return [0] * (width - len(bits)) + bits

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

def long_division_with_steps(dividend, divisor):
    """
    Long division over GF(2) while keeping the length intact so we can show
    each XOR. Returns the remainder (last len(divisor)-1 bits) and a list of
    step dictionaries used for visualization.
    """
    work = dividend[:]
    steps = []
    divisor_len = len(divisor)

    for shift in range(len(dividend) - divisor_len + 1):
        leading = work[shift]
        step = {
            "shift": shift,
            "leading": leading,
            "before": work[:],
            "divisor": divisor[:],
        }

        if leading == 1:
            for i in range(divisor_len):
                work[shift + i] ^= divisor[i]
        step["after"] = work[:]
        steps.append(step)

    remainder = work[-(divisor_len - 1):]
    return remainder, steps

def print_division_steps(dividend, divisor, title, steps=None, remainder=None):
    """
    Pretty-print the long division steps. Does not mutate the incoming dividend.
    """
    print(title)
    print(f"Dividend : {format_bits(dividend)}  (multiply data by x^{len(divisor)-1})")
    print(f"Divisor  : {format_bits(divisor)}  g(x) = {bits_to_poly(divisor)}\n")

    if steps is None or remainder is None:
        remainder, steps = long_division_with_steps(dividend, divisor)

    for step in steps:
        shift = step["shift"]
        power = len(dividend) - shift - 1
        print(f"Step {shift+1} – align g(x) with bit {shift+1} (x^{power} term)")
        print(f"  current : {format_bits(step['before'])}")
        if step["leading"] == 1:
            aligned_divisor = ("  " * shift) + format_bits(step["divisor"])
            print(f"  xor g(x): {aligned_divisor}")
        else:
            print("  leading 0 → nothing to XOR")
        print(f"  result  : {format_bits(step['after'])}\n")

    print(f"Remainder (parity) : {format_bits(remainder)}  -> {bits_to_poly(remainder)}\n")
    return remainder

def plot_division_grid(dividend, steps, filename, title):
    """
    Plot a grid showing the intermediate bit strings after each XOR step.
    """
    rows = [step["before"][:] for step in steps]
    rows.append(steps[-1]["after"][:])  # final state
    labels = [f"step {i+1} (lead {step['leading']})" for i, step in enumerate(steps)]
    labels.append("final")

    cmap = ListedColormap(["#f2f2f2", "#1a73e8"])
    fig, ax = plt.subplots(figsize=(8, 0.5 * len(rows) + 1))
    im = ax.imshow(rows, cmap=cmap, vmin=0, vmax=1, aspect="auto")

    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xticks(range(len(dividend)))
    ax.set_xticklabels([f"b{idx+1}" for idx in range(len(dividend))], fontsize=9)
    ax.set_title(title, fontsize=12, pad=10)

    # label bits in each cell
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            ax.text(c, r, str(val), ha="center", va="center", color="#111", fontsize=9)

    ax.set_xlabel("Bit position (MSB → LSB)")
    fig.tight_layout()
    fig.savefig(filename, dpi=200, bbox_inches="tight")
    plt.close(fig)

def plot_bit_row(ax, bits, title, highlight=None, width=None):
    width = width or len(bits)
    padded = pad_left(bits, width)
    ax.set_title(title, loc="left", fontsize=10)
    ax.set_xlim(-0.5, width - 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.axis("off")

    for i, bit in enumerate(padded):
        rect = plt.Rectangle((i - 0.45, -0.3), 0.9, 0.6,
                             facecolor="#1a73e8" if bit else "#f2f2f2",
                             edgecolor="#888", linewidth=1.0,
                             alpha=0.9 if highlight is None or i not in highlight else 0.5)
        ax.add_patch(rect)
        ax.text(i, 0, str(bit), ha="center", va="center", fontsize=10, color="#111")
    ax.set_xticks(range(width))
    ax.set_xticklabels([f"{width - i}" for i in range(width)], fontsize=8)
    ax.set_xlabel("bit index (power of x from left)", fontsize=8)

def plot_flow(data_bits, parity, codeword, received, syndrome_bits, filename):
    """
    Visual flow of the main vectors in the cyclic code process.
    """
    width = max(len(codeword), len(received))
    rows = [
        ("Data d(x)", data_bits),
        ("Shifted d(x)*x^3", data_bits + [0, 0, 0]),
        ("Parity", pad_left(parity, width)),
        ("Codeword c(x)", codeword),
        ("Received", received),
        ("Syndrome s(x)", pad_left(syndrome_bits, width)),
    ]

    fig, axes = plt.subplots(len(rows), 1, figsize=(10, 1.4 * len(rows)))
    for ax, (label, bits) in zip(axes, rows):
        plot_bit_row(ax, bits, label, width=width)
    fig.suptitle("Cyclic Hamming (7,4) flow", fontsize=13, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(filename, dpi=200, bbox_inches="tight")
    plt.close(fig)

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

def show_bit_positions(label, bits):
    
    degree = len(bits) - 1
    
    powers = []
    
    for i in range(len(bits)):
        power = degree - i
        if power == 0:
            powers.append("1")
        elif power == 1:
            powers.append("x")
        else:
            powers.append(f"x^{power}")

    print(f"{label}:")
    print("  powers    :", "  ".join(powers))
    print("  positions :", "  ".join(str(i + 1) for i in range(len(bits))))
    print("  bits      :", format_bits(bits))
    print()

def introduce_error_random(codeword):
    pos = random.randint(0, 6)
    
    codeword[pos] ^= 1
    print(f"Introduced error at bit {pos+1}")

def syndrome(codeword):
    syn = poly_mod(codeword, G)
    
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

def structured_demo(data_bits):


    input()

    print("1) Start with data bits d\n")
    print("Raw data bits:")
    print("  d =", format_bits(data_bits))
    print("  d(x) =", bits_to_poly(data_bits))
    print()


    input()
    print("2) Multiply by x^3 (make room for parity)\n")
    extended = data_bits + [0, 0, 0]
    print("Shifted data:")
    print("  d(x)·x^3 =", bits_to_poly(extended))
    print("  bits     =", format_bits(extended))
    print()

    input()
    print("3) Divide by generator g(x) to compute parity\n")
    print("Generator polynomial:")
    print("  g(x) =", bits_to_poly(G))
    print()

    remainder = poly_mod(extended, G)
    remainder = [0] * (3 - len(remainder)) + remainder

    print("Division result:")
    print("  remainder =", format_bits(remainder))
    print("  parity p(x) =", bits_to_poly(remainder))
    print()


    input()
    print("4) Form codeword c(x) = d(x)·x^3 + p(x)\n")
    codeword = encode_cyclic_hamming(data_bits)

    print("Codeword:")
    print("  bits =", format_bits(codeword))
    print("  c(x) =", bits_to_poly(codeword))
    print()

    print("Check validity:")
    print("  c(x) mod g(x) =", format_bits(syndrome(codeword)))
    print("  (must be 000 for a valid codeword)\n")


    input()
    print("5) Cyclic shift (rotation)\n")
    rotated = codeword[1:] + [codeword[0]]

    print("Cyclic shift = multiply by x (mod x^7 − 1)")
    print("  rotated bits =", format_bits(rotated))
    print("  rotated poly =", bits_to_poly(rotated))
    print()

    print("Validity after shift:")
    print("  rotated mod g(x) =", format_bits(syndrome(rotated)))
    print("  (still valid -> this is why the code is cyclic)\n")


    input()
    print("6) Introduce a single-bit error\n")
    received = rotated[:]
    error_pos = random.randint(0, 6)
    received[error_pos] ^= 1

    print(f"Error introduced at position {error_pos + 1}")
    print("Received word:")
    print("  r(x) =", bits_to_poly(received))
    print("  bits =", format_bits(received))
    print()


    input()
    print("7) Compute syndrome s(x) = r(x) mod g(x)\n")
    syn = syndrome(received)
    syn_val = int("".join(map(str, syn)), 2)

    print("Syndrome:")
    print("  s(x) =", bits_to_poly(syn))
    print("  bits =", format_bits(syn))
    print("  numeric value =", syn_val)
    print()


    input()
    print("8) Use syndrome as a lookup key\n")
    table = build_syndrome_table()

    print("Syndrome table (value -> error position):")
    for k in sorted(table):
        print(f"  {k:03b} -> bit {table[k] + 1}")
    print()

    if syn_val in table:
        fix_pos = table[syn_val]
        print(f"Error located at bit {fix_pos + 1}")
        received[fix_pos] ^= 1

    print("\nCorrected codeword:")
    print("  bits =", format_bits(received))
    print("  c(x) =", bits_to_poly(received))
    print("  mod g(x) =", format_bits(syndrome(received)))
    print("\nEnd of Demo")


def main():
    data_bits = get_user_bits()
    structured_demo(data_bits)

if __name__ == "__main__":
    main()
