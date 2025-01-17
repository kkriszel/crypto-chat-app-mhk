import unittest

from mhknapsack import MHKnapsack
import utils

class TestMHKnapsack(unittest.TestCase):
    def test_generate_private_key(self):
        private_key = MHKnapsack.generate_private_key()
        w, q, r = private_key

        self.assertTrue(utils.is_superincreasing(w))
        self.assertGreater(q, sum(w))
        self.assertTrue(utils.coprime(q, r))

    def test_create_public_key(self):
        private_key = MHKnapsack.generate_private_key()
        public_key = MHKnapsack.create_public_key(private_key)

        self.assertEqual(len(public_key), len(private_key[0]))

    def test_encrypt_decrypt(self):
        private_key = MHKnapsack.generate_private_key()
        public_key = MHKnapsack.create_public_key(private_key)

        message = b'I Love Python!'
        encrypted = MHKnapsack.encrypt(message, public_key)
        decrypted = MHKnapsack.decrypt(encrypted, private_key)

        self.assertEqual(message, decrypted)

    def test_encrypt_decrypt_with_unicode(self):
        private_key = MHKnapsack.generate_private_key()
        public_key = MHKnapsack.create_public_key(private_key)

        message = '👋🤑🐮🚝🎼🇺🇲'.encode()
        encrypted = MHKnapsack.encrypt(message, public_key)
        decrypted = MHKnapsack.decrypt(encrypted, private_key)

        self.assertEqual(message, decrypted)

    def test_generate_superincreasing(self):
        result = MHKnapsack._generate_superincreasing(8)
        self.assertTrue(utils.is_superincreasing(result))

    def test_get_next_in_superincreasing(self):
        seq = [2, 6, 19, 49, 90]
        result = MHKnapsack._get_next_in_superincreasing(seq)
        self.assertGreater(result, sum(seq))

    def test_generate_coprime(self):
        q = 100
        result = MHKnapsack._generate_coprime(q)
        self.assertTrue(utils.coprime(q, result))

    def test_solve_superincreasing_subset_sum(self):
        w = (2, 6, 19, 49, 90)
        cp = 70
        result = MHKnapsack._solve_superincreasing_subset_sum(cp, w)
        sumres = sum(wi * ri for wi, ri in zip(w, result))
        self.assertEqual(sumres, cp)

if __name__ == '__main__':
    unittest.main()
