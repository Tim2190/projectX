"""Console interface for playing a simplified game of Durak."""

from __future__ import annotations

import sys
from typing import List, Optional

from durak.ai import choose_attack_card
from durak.card import Card
from durak.game import DurakGame


def format_hand(hand: List[Card]) -> str:
    return "  ".join(f"[{index}] {card}" for index, card in enumerate(hand, start=1))


def prompt_attack(player_name: str, hand: List[Card]) -> Card:
    while True:
        print(f"\n{player_name}, ваш ход. Ваши карты: {format_hand(hand)}")
        choice = input("Выберите номер карты для атаки: ").strip()
        if not choice.isdigit():
            print("Введите номер карты.")
            continue
        index = int(choice)
        if not 1 <= index <= len(hand):
            print("Некорректный номер карты.")
            continue
        return hand[index - 1]


def prompt_defense(player_name: str, hand: List[Card], attacking_card: Card) -> Optional[Card]:
    while True:
        print(f"\n{player_name}, на вас нападают картой {attacking_card}.")
        print(f"Ваши карты: {format_hand(hand)}")
        choice = input(
            "Введите номер карты, чтобы отбиться, или нажмите Enter, чтобы взять карты: "
        ).strip()
        if not choice:
            return None
        if not choice.isdigit():
            print("Введите номер карты или оставьте поле пустым.")
            continue
        index = int(choice)
        if not 1 <= index <= len(hand):
            print("Некорректный номер карты.")
            continue
        return hand[index - 1]


def main() -> int:
    print("Добро пожаловать в игру 'Карты Дурак'!")
    print("Игра ведётся по упрощённым правилам: атаку можно вести только одной картой.")
    game = DurakGame()
    game.setup()
    print(f"Козырная масть: {game.trump}")

    while True:
        if game.is_finished():
            winner = game.get_winner()
            if winner is None:
                print("Ничья!")
            elif winner.is_human:
                print("Поздравляем! Вы победили.")
            else:
                print("Компьютер выиграл. Попробуйте ещё раз!")
            return 0

        attacker = game.attacker
        defender = game.defender
        if attacker is None or defender is None:
            raise RuntimeError("Игра не настроена корректно.")

        if attacker.is_human:
            attack_card = prompt_attack(attacker.name, attacker.hand)
        else:
            attack_card = choose_attack_card(attacker.hand, game.trump)
            print(f"\n{attacker.name} атакует картой {attack_card}.")

        if defender.is_human:
            defense_card = prompt_defense(defender.name, defender.hand, attack_card)
            defense_cards = [defense_card] if defense_card else None
        else:
            defense_cards = None

        try:
            result = game.play_turn(
                attack_cards=[attack_card],
                defense_cards=defense_cards,
            )
        except ValueError as error:
            print(f"Ошибка: {error}")
            continue

        if result.defended:
            print("Защита успешна. Ход переходит к защищавшемуся.")
        else:
            print("Защита не удалась. Защитнику пришлось взять карту и он снова в обороне.")

        print(
            "Карты на столе: "
            + ", ".join(
                f"{attack}{'/' + str(defense) if defense else ''}" for attack, defense in result.table_cards
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
