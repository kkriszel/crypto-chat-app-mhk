# Merkle-Hellman Knapsack Cryptosystem

import random
import utils

class MHKnapsack:
    @staticmethod
    def generate_private_key(n: int = 8) -> tuple[tuple[int, ...], int, int]:
        """
        Generate a private key for use in the Merkle-Hellman Knapsack Cryptosystem.

        Following the instructions in the handout, construct the private key components
        of the MH Cryptosystem. This consists of 3 tasks:

        1. Build a superincreasing sequence `w` of length n
            (Note: you can check if a sequence is superincreasing with `utils.is_superincreasing(seq)`)
        2. Choose some integer `q` greater than the sum of all elements in `w`
        3. Discover an integer `r` between 2 and q that is coprime to `q` (you can use utils.coprime)

        You'll need to use the random module for this function, which has been imported already.

        Args:
            n (int): The bit size of the message to send. Defaults to 8.

        Returns:
            tuple: A 3-tuple `(w, q, r)`, with `w` a n-tuple, and `q` and `r` ints.
        """

        w = MHKnapsack._generate_superincreasing(n)
        q = MHKnapsack._get_next_in_superincreasing(w)
        r = MHKnapsack._generate_coprime(q)

        return (tuple(w), q, r)

    @staticmethod
    def create_public_key(private_key: tuple[tuple[int, ...], int, int]) -> tuple[int, ...]:
        """
        Create a public key corresponding to the given private key.

        To accomplish this, you only need to build and return `beta` as described in the handout.

            beta = (b_1, b_2, ..., b_n) where b_i = r × w_i mod q

        Hint: this can be written in one line using a list comprehension.

        Args:
            private_key (tuple): The private key as a 3-tuple `(w, q, r)`.

        Returns:
            tuple: The public key as an n-tuple.
        """

        w, q, r = private_key
        beta = tuple((r * wi) % q for wi in w)

        return beta

    @staticmethod
    def encrypt(message: bytes, public_key: tuple[int, ...]) -> list[int]:
        """
        Encrypt an outgoing message using a public key.

        1. Separate the message into chunks the size of the public key (in our case, fixed at 8).
        2. For each byte, determine the 8 bits (the `a_i`s) using `utils.byte_to_bits`.
        3. Encrypt the 8 message bits by computing
            c = sum of a_i * b_i for i = 1 to n.
        4. Return a list of the encrypted cyphertexts for each chunk in the message.

        Hint: think about using `zip` at some point.

        Args:
            message (bytes): The message to be encrypted.
            public_key (tuple): The public key of the desired recipient.

        Returns:
            list: A list of ints representing encrypted bytes.
        """

        encrypted = []
        for a in message:
            alpha = utils.byte_to_bits(a)
            c = sum(ai * bi for ai, bi in zip(alpha, public_key))
            encrypted.append(c)

        return encrypted

    @staticmethod
    def decrypt(message: list[int], private_key: tuple[tuple[int, ...], int, int]) -> bytes:
        """
        Decrypt an incoming message using a private key.

        1. Extract w, q, and r from the private key.
        2. Compute s, the modular inverse of r mod q, using the
            Extended Euclidean algorithm (implemented at `utils.modinv(r, q)`).
        3. For each byte-sized chunk, compute
            c' = cs (mod q).
        4. Solve the superincreasing subset sum using c' and w to recover the original byte.
        5. Reconstitute the encrypted bytes to get the original message back.

        Args:
            message (list): The encrypted message chunks.
            private_key (tuple): The private key of the recipient as a 3-tuple `(w, q, r)`.

        Returns:
            bytes: The decrypted message.
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
        """
        Generate a superincreasing sequence of length n.

        Args:
            n (int): The length of the sequence.

        Returns:
            list: A superincreasing sequence.
        """
        seq = [random.randint(2, 10)]
        for _ in range(n - 1):
            next = MHKnapsack._get_next_in_superincreasing(seq)
            seq.append(next)
        return tuple(seq)

    @staticmethod
    def _get_next_in_superincreasing(seq: list[int]) -> int:
        """
        Get the next value in a superincreasing sequence.

        Args:
            seq (list): The current superincreasing sequence.

        Returns:
            int: The next value in the sequence.
        """
        total = sum(seq)
        return random.randint(total + 1, 2 * total)

    @staticmethod
    def _generate_coprime(q: int) -> int:
        """
        Generate a coprime integer to q.

        Args:
            q (int): The integer to find a coprime for.

        Returns:
            int: A coprime integer to q.
        """
        r = random.randint(2, q - 1)
        while not utils.coprime(q, r):
            r = random.randint(2, q - 1)
        return r

    @staticmethod
    def _solve_superincreasing_subset_sum(cp: int, w: tuple[int, ...]) -> list[int]:
        """
        Solve the superincreasing subset sum problem.

        Args:
            cp (int): The target sum.
            w (tuple): The superincreasing sequence.

        Returns:
            list: A list of bits representing the solution.

        Raises:
            ValueError: If no solution could be found.
        """
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
