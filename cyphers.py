class SolitaireKeyStream:
    NUM_CARDS = 54
    JOKER_W = NUM_CARDS - 1
    JOKER_B = NUM_CARDS

    deck: list[int]

    def __init__(self, deck: list[int] | None = None) -> None:
        if deck is None:
            self.deck = list(range(1, self.NUM_CARDS + 1))
        else:
            self.deck = deck

    def get_next_bytes(self, num_bytes: int) -> bytes:
        next_bytes = bytearray()

        for _ in range(num_bytes):
            next_bytes.append(self._get_next_byte())

        return bytes(next_bytes)

    def _get_next_byte(self) -> int:
        twobits = [self._get_next_value() % 4 for _ in range(4)]
        return twobits[0] + (twobits[1] << 2) + (twobits[2] << 4) + (twobits[3] << 6)

    def _get_next_value(self) -> int:
        while True:
            self._swap_jokers()
            self._triple_cut()
            self._count_cut()
            value = self._get_value()
            if value:
                return value

    def _swap_jokers(self) -> None:
        index_w = self.deck.index(self.JOKER_W)
        self.deck.remove(self.JOKER_W)

        if index_w == self.NUM_CARDS - 1:
            self.deck.insert(1, self.JOKER_W)
        else:
            self.deck.insert(index_w + 1, self.JOKER_W)

        index_b = self.deck.index(self.JOKER_B)
        self.deck.remove(self.JOKER_B)

        if index_b == self.NUM_CARDS - 2:
            self.deck.insert(1, self.JOKER_B)
        elif index_b == self.NUM_CARDS - 1:
            self.deck.insert(2, self.JOKER_B)
        else:
            self.deck.insert(index_b + 2, self.JOKER_B)

    def _triple_cut(self) -> None:
        index_1 = self.deck.index(self.JOKER_W)
        index_2 = self.deck.index(self.JOKER_B)

        if index_1 > index_2:
            index_1, index_2 = index_2, index_1

        self.deck = self.deck[index_2 + 1:] + self.deck[index_1:index_2 + 1] + self.deck[:index_1]

    def _count_cut(self) -> None:
        bottom_value = self.deck[-1]

        if bottom_value in [self.JOKER_W, self.JOKER_B]:
            return

        self.deck = self.deck[bottom_value:self.NUM_CARDS - 1] + self.deck[:bottom_value] + [bottom_value]

    def _get_value(self) -> int | None:
        top_value = self.deck[0]

        if top_value in [self.JOKER_W, self.JOKER_B]:
            top_value = self.JOKER_W

        if self.deck[top_value] in [self.JOKER_W, self.JOKER_B]:
            return None

        return self.deck[top_value]

class StreamCypher:
    key_stream: SolitaireKeyStream

    def __init__(self, key_stream: SolitaireKeyStream) -> None:
        self.key_stream = key_stream

    def encode(self, input_stream: bytes) -> bytes:
        key = self.key_stream.get_next_bytes(len(input_stream))
        encrypted_data = [input_byte ^ key_byte for (input_byte, key_byte) in zip(input_stream, key)]
        return bytes(encrypted_data)

    def decode(self, input_stream: bytes) -> bytes:
        return self.encode(input_stream)
