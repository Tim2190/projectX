"""Card and enumerations used in the Durak card game."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Suit(str, Enum):
    """Possible suits in the deck."""

    SPADES = "♠"
    CLUBS = "♣"
    HEARTS = "♥"
    DIAMONDS = "♦"

    def __str__(self) -> str:
        return self.value


class Rank(str, Enum):
    """Possible ranks in the deck."""

    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

    @property
    def strength(self) -> int:
        """Numeric strength used for comparing cards."""

        order = {
            Rank.SIX: 6,
            Rank.SEVEN: 7,
            Rank.EIGHT: 8,
            Rank.NINE: 9,
            Rank.TEN: 10,
            Rank.JACK: 11,
            Rank.QUEEN: 12,
            Rank.KING: 13,
            Rank.ACE: 14,
        }
        return order[self]

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Card:
    """A single playing card."""

    suit: Suit
    rank: Rank

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

    def beats(self, other: "Card", trump: Suit) -> bool:
        """Return True if this card beats ``other`` given a trump suit."""

        if self.suit == other.suit:
            return self.rank.strength > other.rank.strength
        if self.suit == trump and other.suit != trump:
            return True
        return False

    @property
    def sort_key(self) -> tuple[int, int]:
        """Return a key useful for sorting cards."""

        suit_priority = {
            Suit.SPADES: 0,
            Suit.CLUBS: 1,
            Suit.HEARTS: 2,
            Suit.DIAMONDS: 3,
        }
        return suit_priority[self.suit], self.rank.strength
