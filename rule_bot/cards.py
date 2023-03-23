from enum import Enum


class Rank(Enum):
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13
    Ace = 14

    # noinspection PyTypeChecker
    def __lt__(self, other):
        return self.value < other.value

    # noinspection PyTypeChecker
    def __le__(self, other):
        return self.value <= other.value

    def __hash__(self):
        return hash(self.value)

    # noinspection PyTypeChecker
    def __str__(self):
        if self.value < self.Ten.value:
            return str(int(self.value))
        if self == self.Ten:
            return 'T'
        return self.name[0]

    @classmethod
    def _str_map(cls):
        return {
            '2': cls.Two,
            '3': cls.Three,
            '4': cls.Four,
            '5': cls.Five,
            '6': cls.Six,
            '7': cls.Seven,
            '8': cls.Eight,
            '9': cls.Nine,
            'T': cls.Ten,
            'J': cls.Jack,
            'Q': cls.Queen,
            'K': cls.King,
            'A': cls.Ace,
        }

    @classmethod
    def parse(cls, s):
        rank = cls._str_map().get(s.upper())
        if rank is None:
            raise ValueError(f"Bad rank: {s}")
        return rank

    def next(self):
        try:
            return Rank(self.value + 1)
        except ValueError:
            assert self == self.Ace
            return self.Two

    def prev(self):
        try:
            return Rank(self.value - 1)
        except ValueError:
            assert self == self.Two
            return self.Ace

    def covered_straight_max_rank(self):
        if self in [self.Jack, self.Queen, self.King]:
            return self.Ace

        if self == self.Ace:
            # ace as low card - 1...5
            return self.Five

        return Rank(self.value + 4)


class Suit(Enum):
    Spades = 1
    Hearts = 2
    Diamonds = 3
    Clubs = 4

    def __str__(self):
        return self.name[0]

    @classmethod
    def _str_map(cls):
        return {
            's': cls.Spades,
            'h': cls.Hearts,
            'd': cls.Diamonds,
            'c': cls.Clubs,
        }

    @classmethod
    def parse(cls, s):
        suit = cls._str_map().get(s.lower())
        if suit is None:
            raise ValueError(f"Bad suit: {s}")
        return suit


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def same_suit(self, other):
        return self.suit == other.suit

    def off_suit(self, other):
        return not self.same_suit(other)

    @classmethod
    def sort_by_rank(cls, cards):
        return list(sorted(cards, key=lambda c: c.rank.value))

    @classmethod
    def sort_by_rank_desc(cls, cards):
        return list(sorted(cards, key=lambda c: -c.rank.value))

    def __str__(self):
        return f"{self.rank}{self.suit}"

    @classmethod
    def parse(cls, s):
        if len(s) != 2:
            raise ValueError(f"The string '{s}' is invalid representation of a Card")

        return cls(Rank.parse(s[0]), Suit.parse(s[1]))

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit.value))
