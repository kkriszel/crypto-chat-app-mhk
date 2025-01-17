import unittest

import random
from cyphers import SolitaireKeyStream, StreamCypher

class TestSolitaireKeyStream(unittest.TestCase):
    def test_init_with_default_deck(self):
        key_stream = SolitaireKeyStream()
        self.assertEqual(len(key_stream.deck), SolitaireKeyStream.NUM_CARDS)
        self.assertEqual(key_stream.deck[0], 1)
        self.assertEqual(key_stream.deck[-1], SolitaireKeyStream.JOKER_B)

    def test_init_with_custom_deck(self):
        deck = list(range(1, 55))
        random.shuffle(deck)
        key_stream = SolitaireKeyStream(deck)
        self.assertEqual(key_stream.deck, deck)

    def test_get_next_bytes_count(self):
        key_stream = SolitaireKeyStream()
        num_bytes = 19
        next_bytes = key_stream.get_next_bytes(num_bytes)
        self.assertEqual(len(next_bytes), num_bytes)

    def test_swap_jokers(self):
        key_stream = SolitaireKeyStream()
        initial_deck = key_stream.deck.copy()
        key_stream._swap_jokers()
        self.assertNotEqual(initial_deck, key_stream.deck)

    def test_triple_cut(self):
        key_stream = SolitaireKeyStream()
        initial_deck = key_stream.deck.copy()
        key_stream._triple_cut()
        self.assertNotEqual(initial_deck, key_stream.deck)

    def test_get_next_value(self):
        key_stream = SolitaireKeyStream()
        value = key_stream._get_next_value()
        self.assertIsNotNone(value)

    def test_get_next_byte(self):
        key_stream = SolitaireKeyStream()
        byte = key_stream._get_next_byte()
        self.assertIsInstance(byte, int)
        self.assertGreaterEqual(byte, 0)
        self.assertLessEqual(byte, 255)

class TestStreamCypher(unittest.TestCase):
    def test_encode_decode_default_deck(self):
        key_stream1 = SolitaireKeyStream()
        key_stream2 = SolitaireKeyStream()

        stream_cypher1 = StreamCypher(key_stream1)
        stream_cypher2 = StreamCypher(key_stream2)

        input_data = b'I Love Python!'
        encoded_data = stream_cypher1.encode(input_data)
        decoded_data = stream_cypher2.decode(encoded_data)

        self.assertEqual(input_data, decoded_data)

    def test_encode_decode_random_deck(self):
        deck = list(range(1, 55))
        random.shuffle(deck)

        deck1 = deck.copy()
        deck2 = deck.copy()

        key_stream1 = SolitaireKeyStream(deck1)
        key_stream2 = SolitaireKeyStream(deck2)

        stream_cypher1 = StreamCypher(key_stream1)
        stream_cypher2 = StreamCypher(key_stream2)

        input_data = b'I Love Python!'
        encoded_data = stream_cypher1.encode(input_data)
        decoded_data = stream_cypher2.decode(encoded_data)

        self.assertEqual(input_data, decoded_data)

    def test_encode_decode_with_unicode(self):
        key_stream1 = SolitaireKeyStream()
        key_stream2 = SolitaireKeyStream()

        stream_cypher1 = StreamCypher(key_stream1)
        stream_cypher2 = StreamCypher(key_stream2)

        input_data = '👋🤑🐮🚝🎼🇺🇲'.encode()
        encoded_data = stream_cypher1.encode(input_data)
        decoded_data = stream_cypher2.decode(encoded_data)

        self.assertEqual(input_data, decoded_data)

if __name__ == '__main__':
    unittest.main()
