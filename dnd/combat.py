import logging
import secrets
from operator import itemgetter
from typing import List
from typing import Tuple

from dnd.char import Character
from dnd.dice import CriticalStatus
from dnd.dice import d20
from dnd.dice import d6_pool

logger = logging.getLogger(__name__)


def compute_initiative(
    team1: List[Character],
    team2: List[Character],
) -> List[Tuple[float, Character, int]]:
    order = []
    for c in team1:
        # append a small random value to use as a tiebreaker
        r, _ = d20(c.init_mod)
        initiative = r + (secrets.randbelow(100) / 100)
        order.append((initiative, c, 1))

    for c in team2:
        # append a small random value to use as a tiebreaker
        r, _ = d20(c.init_mod)
        initiative = r + (secrets.randbelow(100) / 100)
        order.append((initiative, c, 2))

    order.sort(key=itemgetter(0), reverse=True)
    logger.info('Initiative Order:')
    for (i, c, team) in order:
        logger.info(f'{c.name} [{team}]: {i}')

    return order


def d20_attack(c, target) -> Tuple[bool, CriticalStatus]:
    attack_roll, crit = d20(c.attack_bonus, can_crit=True)
    logger.info(f'{c.name} attacks {target.name} with a {attack_roll} versus {target.ac} AC')
    return (attack_roll >= target.ac, crit)


def pool_attack(c, target) -> Tuple[bool, CriticalStatus]:
    attack_roll, crit = d6_pool(5 + c.attack_bonus, can_crit=True)
    modified_ac = target.ac - 10
    logger.info(f'{c.name} attacks {target.name} with a {attack_roll} versus {modified_ac} AC')
    return (attack_roll >= modified_ac, crit)


def fight(team1: List[Character], team2: List[Character], attack) -> Tuple[int, int]:
    order = compute_initiative(team1, team2)
    rounds = 0
    while True:
        rounds += 1
        for (_, c, team) in order:
            if all([c.hp <= 0 for c in team1]):
                return (rounds, 2)
            if all([c.hp <= 0 for c in team2]):
                return (rounds, 1)
            allies, opponents = (team2, team1) if team == 2 else (team1, team2)

            target = c.select_target(allies, opponents)
            if target is not None:
                hit, crit = attack(c, target)
                target.hp -= c.compute_damage(hit, crit)
                logger.info(f'{target.name} has {target.hp} hp remaining')
            else:
                continue

        logger.info('-----')
