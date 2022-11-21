import logging
import secrets
from operator import itemgetter
from typing import List
from typing import Optional
from typing import Tuple

from dnd.char import Character
from dnd.dice import d20
from dnd.dice import d6_pool
from dnd.dice import roll_plus_mod
from dnd.dice import CriticalStatus

logger = logging.getLogger(__name__)


def select_target(opponents: List[Character]) -> Optional[int]:
    target = None
    lowest_hp = 10000000
    for i, c in enumerate(opponents):
        if c.hp > 0 and c.hp < lowest_hp:
            target = i
    return target


def compute_initiative(team1: List[Character], team2: List[Character]) -> List[Character]:
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
            opponents = team1 if team == 2 else team2
            target = opponents[select_target(opponents)]
            hit, crit = attack(c, target)
            dmg = 0
            if crit == CriticalStatus.Fail:
                logger.info('Critical failure!')
            elif crit == CriticalStatus.Success:
                logger.info('Critical hit!  Rolling double damage dice.')
                dmg = roll_plus_mod(2 * c.dmg_numd, c.dmg_sized, c.dmg_mod)
            elif hit:
                logger.info(f'{c.name} hits and deals {dmg} points of damage!')
                dmg = roll_plus_mod(c.dmg_numd, c.dmg_sized, c.dmg_mod)
            target.hp -= dmg
            logger.info(f'{target.name} has {target.hp} hp remaining')

            if all([c.hp <= 0 for c in team1]):
                return (rounds, 2)
            if all([c.hp <= 0 for c in team2]):
                return (rounds, 1)

        logger.info('-----')
