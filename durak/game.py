"""Core game loop for a simplified two-player Durak game."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from .ai import choose_attack_card, choose_defense_card
from .card import Card, Suit
from .deck import Deck
from .player import Player

HAND_LIMIT = 6


@dataclass
class TurnResult:
    attacker: Player
    defender: Player
    defended: bool
    table_cards: List[Tuple[Card, Card | None]]


class DurakGame:
    """Implements the rules and flow of a two-player Durak game."""

    def __init__(self, *, seed: int | None = None) -> None:
        rng = random.Random(seed) if seed is not None else None
        self.deck = Deck(rng=rng)
        self.table: List[Tuple[Card, Card | None]] = []
        self.players = (
            Player(name="Человек", is_human=True),
            Player(name="Компьютер", is_human=False),
        )
        self.attacker: Player | None = None
        self.defender: Player | None = None

    def setup(self) -> None:
        trump_card = self.deck.setup_trump()
        self.trump = trump_card.suit
        for _ in range(HAND_LIMIT):
            for player in self.players:
                card = self.deck.draw()
                if card:
                    player.hand.append(card)
        for player in self.players:
            player.sort_hand(self.trump)
        self._determine_first_attacker()

    def _determine_first_attacker(self) -> None:
        lowest_trumps = [player.lowest_trump(self.trump) for player in self.players]
        filtered = [card for card in lowest_trumps if card is not None]
        if not filtered:
            self.attacker = self.players[0]
            self.defender = self.players[1]
            return
        lowest_card = min(filtered, key=lambda card: card.rank.strength)
        index = lowest_trumps.index(lowest_card)
        self.attacker = self.players[index]
        self.defender = self.players[1 - index]

    def play_turn(
        self,
        attack_cards: Iterable[Card] | None = None,
        defense_cards: Iterable[Card] | None = None,
    ) -> TurnResult:
        if self.attacker is None or self.defender is None:
            raise RuntimeError("Game not set up. Call setup() before playing.")

        self.table.clear()
        attacking_card = self._choose_attack_card(attack_cards)
        if attacking_card is None:
            raise RuntimeError("Attacker must play a card.")

        self.attacker.remove_card(attacking_card)
        defending_card = self._choose_defense_card(attacking_card, defense_cards)
        defended = defending_card is not None

        if defended:
            self.defender.remove_card(defending_card)  # type: ignore[arg-type]
            self.table.append((attacking_card, defending_card))
        else:
            self.table.append((attacking_card, None))
            self.defender.draw([attacking_card], trump=self.trump)

        self._refill_hands()
        self._rotate_roles(defended)
        return TurnResult(
            attacker=self.attacker,
            defender=self.defender,
            defended=defended,
            table_cards=list(self.table),
        )

    def _choose_attack_card(
        self, attack_cards: Iterable[Card] | None
    ) -> Card | None:
        if attack_cards:
            cards = list(attack_cards)
            if len(cards) != 1:
                raise ValueError("В этой версии игры можно атаковать только одной картой.")
            card = cards[0]
            if card not in self.attacker.hand:
                raise ValueError("Attacking card not in hand.")
            return card
        if self.attacker.is_human:
            raise ValueError("Human attacker must choose a card.")
        return choose_attack_card(self.attacker.hand, self.trump)

    def _choose_defense_card(
        self,
        attacking_card: Card,
        defense_cards: Iterable[Card] | None,
    ) -> Card | None:
        if defense_cards:
            cards = list(defense_cards)
            if len(cards) != 1:
                raise ValueError("Защищаться можно только одной картой.")
            card = cards[0]
            if card not in self.defender.hand:
                raise ValueError("Defending card not in hand.")
            if not card.beats(attacking_card, self.trump):
                raise ValueError("Эта карта не бьёт атакующую карту.")
            return card
        if self.defender.is_human:
            return None
        return choose_defense_card(self.defender.hand, attacking_card, self.trump)

    def _refill_hands(self) -> None:
        order = [self.attacker, self.defender]
        for player in order:
            if player is None:
                continue
            new_cards = []
            while len(player.hand) + len(new_cards) < HAND_LIMIT:
                card = self.deck.draw()
                if card is None:
                    break
                new_cards.append(card)
            if new_cards:
                player.draw(new_cards, trump=self.trump)

    def _rotate_roles(self, defended: bool) -> None:
        if defended:
            self.attacker, self.defender = self.defender, self.attacker
        else:
            # defender picked up the cards and remains defender
            pass

    def is_finished(self) -> bool:
        deck_empty = len(self.deck) == 0
        players_out = [player for player in self.players if not player.hand]
        return deck_empty and len(players_out) == 1

    def get_winner(self) -> Player | None:
        if not self.is_finished():
            return None
        remaining = [player for player in self.players if player.hand]
        if not remaining:
            return None
        return self.players[0] if self.players[1] in remaining else self.players[1]
