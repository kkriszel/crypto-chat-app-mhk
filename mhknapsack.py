# Merkle-Hellman Knapsack Cryptosystem

import random
import utils

class MHKnapsack:
    @staticmethod
    def generate_private_key(n: int = 8) -> tuple[tuple[int, ...], int, int]:
        """Generate a private key for use in the Merkle-Hellman Knapsack Cryptosystem."""

        """
        Following the instructions in the handout, construct the private key components
        of the MH Cryptosystem. This consistutes 3 tasks:

        1. Build a superincreasing sequence `w` of length n
            (Note: you can check if a sequence is superincreasing with `utils.is_superincreasing(seq)`)
        2. Choose some integer `q` greater than the sum of all elements in `w`
        3. Discover an integer `r` between 2 and q that is coprime to `q` (you can use utils.coprime)

        You'll need to use the random module for this function, which has been imported already

        Somehow, you'll have to return all of these values out of this function! Can we do that in Python?!

        @param n bitsize of message to send (default 8)
        @type n int

        @return 3-tuple `(w, q, r)`, with `w` a n-tuple, and q and r ints.
        """

        w = MHKnapsack._generate_superincreasing(n)
        q = MHKnapsack._get_next_in_superincreasing(w)
        r = MHKnapsack._generate_coprime(q)

        return (tuple(w), q, r)

    @staticmethod
    def create_public_key(private_key: tuple[tuple[int, ...], int, int]) -> tuple[int, ...]:
        """Create a public key corresponding to the given private key."""

        """
        To accomplish this, you only need to build and return `beta` as described in the handout.

            beta = (b_1, b_2, ..., b_n) where b_i = r × w_i mod q

        Hint: this can be written in one line using a list comprehension

        @param private_key The private key
        @type private_key 3-tuple `(w, q, r)`, with `w` a n-tuple, and q and r ints.

        @return n-tuple public key
        """

        w, q, r = private_key
        beta = tuple((r * wi) % q for wi in w)

        return beta

    @staticmethod
    def encrypt(message: bytes, public_key: tuple[int, ...]) -> list[int]:
        """Encrypt an outgoing message using a public key."""

        """
        1. Separate the message into chunks the size of the public key (in our case, fixed at 8)
        2. For each byte, determine the 8 bits (the `a_i`s) using `utils.byte_to_bits`
        3. Encrypt the 8 message bits by computing
            c = sum of a_i * b_i for i = 1 to n
        4. Return a list of the encrypted cyphertexts for each chunk in the message

        Hint: think about using `zip` at some point

        @param message The message to be encrypted
        @type message bytes
        @param public_key The public key of the desired recipient
        @type public_key n-tuple of ints

        @return list of ints representing encrypted bytes
        """

        encrypted = []
        for a in message:
            alpha = utils.byte_to_bits(a)
            c = sum(ai * bi for ai, bi in zip(alpha, public_key))
            encrypted.append(c)

        return encrypted

    @staticmethod
    def decrypt(message: list[int], private_key: tuple[tuple[int, ...], int, int]) -> bytes:
        """Decrypt an incoming message using a private key"""

        """
        1. Extract w, q, and r from the private key
        2. Compute s, the modular inverse of r mod q, using the
            Extended Euclidean algorithm (implemented at `utils.modinv(r, q)`)
        3. For each byte-sized chunk, compute
            c' = cs (mod q)
        4. Solve the superincreasing subset sum using c' and w to recover the original byte
        5. Reconsitite the encrypted bytes to get the original message back

        @param message Encrypted message chunks
        @type message list of ints
        @param private_key The private key of the recipient
        @type private_key 3-tuple of w, q, and r

        @return bytearray or str of decrypted characters
        """

        w, q, r = private_key

        s = utils.modinv(r, q)

        decrypted = bytearray()
        for c in message:
            cp = (c * s) % q
            subset = MHKnapsack._solve_superincreasing_subset_sum(cp, w)
            alpha = utils.bits_to_byte(subset)
            decrypted.append(alpha)

        return bytes(decrypted)

    @staticmethod
    def _generate_superincreasing(n: int) -> list[int]:
        seq = [random.randint(2, 10)]
        for _ in range(n - 1):
            next = MHKnapsack._get_next_in_superincreasing(seq)
            seq.append(next)
        return tuple(seq)

    @staticmethod
    def _get_next_in_superincreasing(seq: list[int]) -> int:
        total = sum(seq)
        return random.randint(total + 1, 2 * total)

    @staticmethod
    def _generate_coprime(q: int) -> int:
        r = random.randint(2, q - 1)
        while not utils.coprime(q, r):
            r = random.randint(2, q - 1)
        return r

    @staticmethod
    def _solve_superincreasing_subset_sum(cp: int, w: tuple[int, ...]) -> list[int]:
        if not utils.is_superincreasing(w):
            raise ValueError("w must be superincreasing")

        result = [0] * len(w)

        for i in range(len(w) - 1, -1, -1):
            if cp >= w[i]:
                result[i] = 1
                cp -= w[i]

        if cp != 0:
            raise ValueError("no solution could be found")

        return result
