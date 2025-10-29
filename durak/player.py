"""Player-related classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from .card import Card, Suit


@dataclass
class Player:
    """Represents a player in the game."""

    name: str
    is_human: bool
    hand: List[Card] = field(default_factory=list)

    def draw(self, cards: Iterable[Card], trump: Suit | None = None) -> None:
        self.hand.extend(cards)
        self.sort_hand(trump)

    def remove_card(self, card: Card) -> None:
        self.hand.remove(card)

    def sort_hand(self, trump: Suit | None = None) -> None:
        if trump is None:
            self.hand.sort(key=lambda card: card.sort_key)
            return

        def sort_key(card: Card) -> tuple[int, int]:
            suit_priority = 1 if card.suit == trump else 0
            return (suit_priority, card.rank.strength)

        self.hand.sort(key=sort_key)

    def has_cards(self) -> bool:
        return bool(self.hand)

    def lowest_trump(self, trump: Suit) -> Card | None:
        trumps = [card for card in self.hand if card.suit == trump]
        if not trumps:
            return None
        return min(trumps, key=lambda card: card.rank.strength)
