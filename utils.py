"""
Taken from: https://github.com/stanfordpython/python-assignments/tree/development/assign1
"""
import math

class Error(Exception):
    """Base class for exceptions in this module."""

class BinaryConversionError(Error):
    """Custom exception for invalid binary conversions."""
    pass

def is_superincreasing(seq: tuple[int]) -> bool:
    """Return whether a given sequence is superincreasing."""
    ct = 0  # Total so far
    for n in seq:
        if n <= ct:
            return False
        ct += n
    return True

def modinv(a: int, b: int) -> int:
    """Returns the modular inverse of a mod b.

    Pre: a < b and gcd(a, b) = 1

    Adapted from https://en.wikibooks.org/wiki/Algorithm_Implementation/
    Mathematics/Extended_Euclidean_algorithm#Python
    """
    saved = b
    x, y, u, v = 0, 1, 1, 0
    while a:
        q, r = b // a, b % a
        m, n = x - u*q, y - v*q
        b, a, x, y, u, v = a, r, u, v, m, n
    return x % saved

def coprime(a: int, b: int) -> bool:
    """Returns True iff `gcd(a, b) == 1`, i.e. iff `a` and `b` are coprime"""
    return math.gcd(a, b) == 1

def byte_to_bits(byte: int) -> list[int]:
    if not 0 <= byte <= 255:
        raise BinaryConversionError(byte)

    out = []
    for i in range(8):
        out.append(byte & 1)
        byte >>= 1
    return out[::-1]

def bits_to_byte(bits: list[int]) -> int:
    if not all(bit == 0 or bit == 1 for bit in bits):
        raise BinaryConversionError("Invalid bitstring passed")

    byte = 0
    for bit in bits:
        byte *= 2
        if bit:
            byte += 1
    return byte

def is_list_of_ints(var: any) -> bool:
    return isinstance(var, list) and all(isinstance(item, int) for item in var)
