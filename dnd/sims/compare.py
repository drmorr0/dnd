from typing import List

from dnd.char import Character
from dnd.char import State
from dnd.combat import _2d10_attack
from dnd.combat import d20_attack
from dnd.combat import fight
from dnd.combat import pool_attack


def run_comparison(team1: List[Character], team2: List[Character], iterations: int):
    d20_rounds_accum, pool_rounds_accum, _2d10_rounds_accum = 0, 0, 0
    d20_survivors = {c.name: 0 for c in team1}
    pool_survivors = {c.name: 0 for c in team1}
    _2d10_survivors = {c.name: 0 for c in team1}
    d20_winning_team, pool_winning_team, _2d10_winning_team = {1: 0, 2: 0}, {1: 0, 2: 0}, {1: 0, 2: 0}

    print('Running d20 simulation')
    for _ in range(iterations):
        for c in team1:
            c.reset()
        for c in team2:
            c.reset()

        rounds, winners = fight(team1, team2, d20_attack)
        d20_rounds_accum += rounds
        d20_winning_team[winners] += 1
        for c in team1:
            if c.state != State.Dead:
                d20_survivors[c.name] += 1

    print('Running pool simulation')
    for _ in range(iterations):
        for c in team1:
            c.reset()
        for c in team2:
            c.reset()

        rounds, winners = fight(team1, team2, pool_attack)
        pool_rounds_accum += rounds
        pool_winning_team[winners] += 1
        for c in team1:
            if c.state != State.Dead:
                pool_survivors[c.name] += 1

    print('Running 2d10 simulation')
    for _ in range(iterations):
        for c in team1:
            c.reset()
        for c in team2:
            c.reset()

        rounds, winners = fight(team1, team2, _2d10_attack)
        _2d10_rounds_accum += rounds
        _2d10_winning_team[winners] += 1
        for c in team1:
            if c.state != State.Dead:
                _2d10_survivors[c.name] += 1

    d20_avg_rounds = d20_rounds_accum / iterations
    pool_avg_rounds = pool_rounds_accum / iterations
    _2d10_avg_rounds = _2d10_rounds_accum / iterations
    print(f'Ran comparison for {iterations} iterations.  Results:')
    print(
        f'  - D20: average rounds: {d20_avg_rounds}; win counts: {d20_winning_team};\n'
        f'    survivor counts: {d20_survivors}',
    )
    print(
        f'  - D6 pool: average rounds: {pool_avg_rounds}; win counts: {pool_winning_team};\n'
        f'    survivor counts: {pool_survivors}',
    )
    print(
        f'  - 2d10: average rounds: {_2d10_avg_rounds}; win counts: {_2d10_winning_team};\n'
        f'    survivor counts: {_2d10_survivors}',
    )
