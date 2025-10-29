"""Implementation of a 36-card deck used in Durak."""

from __future__ import annotations

import random
from collections import deque
from typing import Deque, Iterable, Iterator

from .card import Card, Rank, Suit


class Deck:
    """Represents a deck of cards."""

    def __init__(self, *, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self._cards: Deque[Card] = deque(self._generate_deck())
        self._rng.shuffle(list_cards := list(self._cards))
        self._cards = deque(list_cards)

    @staticmethod
    def _generate_deck() -> Iterable[Card]:
        for suit in Suit:
            for rank in Rank:
                yield Card(suit=suit, rank=rank)

    def draw(self) -> Card | None:
        """Draw a card from the top of the deck."""

        if not self._cards:
            return None
        return self._cards.popleft()

    def place_bottom(self, card: Card) -> None:
        """Place a card at the bottom of the deck."""

        self._cards.append(card)

    @property
    def trump(self) -> Card:
        """The trump indicator card."""

        if not hasattr(self, "_trump"):
            raise RuntimeError("Trump not set. Call setup_trump() first.")
        return self._trump

    def setup_trump(self) -> Card:
        """Reveal and set the trump card."""

        card = self.draw()
        if card is None:
            raise RuntimeError("Cannot set trump on an empty deck.")
        self._trump = card
        self.place_bottom(card)
        return card

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._cards)

    def __iter__(self) -> Iterator[Card]:  # pragma: no cover - convenience
        return iter(self._cards)
