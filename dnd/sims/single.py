from typing import List

from dnd.char import Character
from dnd.combat import d20_attack
from dnd.combat import fight
from dnd.combat import pool_attack
from dnd.combat import _2d10_attack


def run_single_d20(team1: List[Character], team2: List[Character]):
    rounds, winners = fight(team1, team2, d20_attack)
    print_results(team1, team2)


def run_single_pool(team1: List[Character], team2: List[Character]):
    rounds, winners = fight(team1, team2, pool_attack)
    print_results(team1, team2)


def run_single_2d10(team1: List[Character], team2: List[Character]):
    rounds, winners = fight(team1, team2, _2d10_attack)
    print_results(team1, team2)


def print_results(team1: List[Character], team2: List[Character]):
    print('Team 1:\n')
    for c in team1:
        print(f'  {c.name}: {c.hp}/{c.max_hp} ({c.state})')
    print('\nTeam 2:\n')
    for c in team2:
        print(f'  {c.name}: {c.hp}/{c.max_hp} ({c.state})')
