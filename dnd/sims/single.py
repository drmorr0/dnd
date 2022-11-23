from typing import List

from dnd.char import Character
from dnd.combat import d20_attack
from dnd.combat import fight
from dnd.combat import pool_attack


def run_single_d20(team1: List[Character], team2: List[Character]):
    rounds, winners = fight(team1, team2, d20_attack)


def run_single_pool(team1: List[Character], team2: List[Character]):
    rounds, winners = fight(team1, team2, pool_attack)
