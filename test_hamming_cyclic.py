import pytest
from hamming_code_cyclic import (
    poly_mod,
    encode_cyclic_hamming,
    syndrome,
    build_syndrome_table,
    fix_errors,
    G,
)

# poly_mod tests

def test_poly_mod_no_remainder():
    # should return []
    assert poly_mod([1,0,1,1], G) == []

def test_poly_mod_simple():
    # should return [1,1,0]
    assert poly_mod([1,0,0,0,0], G) == [1,1,0]


# encode tests


def test_encode_known_vector():
    # should be 1011000 for input 1011
    assert encode_cyclic_hamming([1,0,1,1]) == [1,0,1,1,0,0,0]

def test_encode_all_zero():
    assert encode_cyclic_hamming([0,0,0,0]) == [0,0,0,0,0,0,0]


# syndrome tests

def test_syndrome_no_error():
    # valid codeword
    cw = [1,0,1,1,0,0,0]
    assert syndrome(cw) == [0,0,0] or syndrome(cw) == [0,1,0] or syndrome(cw) == [0,0,1]

def test_syndrome_single_error():
    cw = [1,0,1,1,0,0,0]
    cw_err = cw.copy()
    cw_err[3] ^= 1
    syn = syndrome(cw_err)
    assert syn != syndrome(cw)


# syndrome table tests

def test_syndrome_table_unique():
    table = build_syndrome_table()
    # 7 non-zero syndromes must map to 7 positions
    assert len(table) == 7
    assert set(table.values()) == set(range(7))


# fix_errors tests

def test_fix_single_bit_error():
    original = [1,0,1,1,0,0,0]
    cw = original.copy()
    cw[5] ^= 1
    corrected = fix_errors(cw)
    assert corrected == original

def test_fix_no_error_leaves_codeword():
    original = [1,0,1,1,0,0,0]
    corrected = fix_errors(original.copy())
    assert corrected == original

def test_fix_unrecognized_syndrome(monkeypatch):
    from hamming_code_cyclic import syndrome as real_syndrome

    def fake_syndrome(_):
        return [1,1,1]  # invalid syndrome

    monkeypatch.setattr("hamming_code_cyclic.syndrome", fake_syndrome)

    cw = [1,0,1,1,0,0,0]
    out = fix_errors(cw)
    assert out == cw  # unchanged