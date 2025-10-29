"""Simple AI strategies for the Durak game."""

from __future__ import annotations

from typing import Iterable, Sequence

from .card import Card, Suit


def choose_attack_card(hand: Sequence[Card], trump: Suit) -> Card | None:
    """Choose a card to start an attack."""

    if not hand:
        return None
    non_trumps = [card for card in hand if card.suit != trump]
    if non_trumps:
        return min(non_trumps, key=lambda card: card.rank.strength)
    return min(hand, key=lambda card: card.rank.strength)


def choose_defense_card(
    hand: Sequence[Card],
    attacking_card: Card,
    trump: Suit,
) -> Card | None:
    """Return the smallest card that can beat ``attacking_card``."""

    beating_cards: Iterable[Card] = (
        card
        for card in hand
        if card.beats(attacking_card, trump)
    )
    return min(
        beating_cards,
        key=lambda card: (card.suit != trump, card.rank.strength),
        default=None,
    )
