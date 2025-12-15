import random

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

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

def visualize_cyclic_walkthrough(data_bits):
    """
    Walk through encoding and decoding for the cyclic (7,4) Hamming code with
    clear, math-friendly prints.
    """
    print("\n=== Cyclic Hamming (7,4) visual walkthrough ===\n")
    print(f"User data d(x): {format_bits(data_bits)}  -> {bits_to_poly(data_bits)}")
    print(f"Generator g(x): {format_bits(G)}  -> {bits_to_poly(G)}")
    print("g(x) divides every valid codeword polynomial.\n")

    # Encoding
    print("1) Shift data by x^3 (append 3 zeros) before dividing by g(x):")
    shifted = data_bits + [0, 0, 0]
    show_bit_positions("Shifted data", shifted)

    print("2) Divide shifted data by g(x) over GF(2) to get the parity remainder:")
    remainder, encode_steps = long_division_with_steps(shifted, G)
    print_division_steps(shifted, G, "Polynomial long division steps:", steps=encode_steps, remainder=remainder)
    parity = pad_left(remainder, len(G) - 1)
    print(f"Parity bits (highest to lowest power): {format_bits(parity)}\n")
    plot_division_grid(shifted, encode_steps, "cyclic_division_encode.png", "Encoding division (d(x)*x^3) ÷ g(x)")

    print("3) XOR the parity onto the shifted data to get the 7-bit codeword:")
    codeword = encode_cyclic_hamming(data_bits)
    show_bit_positions("Codeword c(x)", codeword)

    # Optional error introduction
    choice = input("Flip a bit to see error detection? (enter 1-7, 'r' for random, or press Enter to skip): ").strip().lower()
    err_pos = None
    if choice == "r":
        err_pos = random.randint(0, 6)
    elif choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= 7:
            err_pos = idx - 1

    received = codeword[:]
    if err_pos is not None:
        received[err_pos] ^= 1
        print(f"\nIntroduced a single-bit error at position {err_pos + 1}.")
    else:
        print("\nNo error introduced.")
    show_bit_positions("Received word", received)

    # Syndrome
    print("4) Compute the syndrome s(x) = received mod g(x):")
    syn_remainder, syndrome_steps = long_division_with_steps(received, G)
    print_division_steps(received, G, "Syndrome division:", steps=syndrome_steps, remainder=syn_remainder)
    syn = pad_left(syn_remainder, len(G) - 1)
    plot_division_grid(received, syndrome_steps, "cyclic_division_syndrome.png", "Syndrome division (received) ÷ g(x)")

    syn_val = int("".join(map(str, syn)), 2)
    table = build_syndrome_table()
    if syn_val == 0:
        print("Syndrome is 000 → received word lies in the code. No correction needed.\n")
    else:
        if syn_val in table:
            pos = table[syn_val]
            print(f"Syndrome {format_bits(syn)} corresponds to bit position {pos + 1}.")
            corrected = received[:]
            corrected[pos] ^= 1
            show_bit_positions("Corrected word", corrected)
        else:
            print("Syndrome not recognized (likely multiple errors).\n")

    plot_flow(data_bits, parity, codeword, received, syn, "cyclic_hamming_flow.png")

def main():
    data_bits = get_user_bits()
    visualize_cyclic_walkthrough(data_bits)

if __name__ == "__main__":
    main()
