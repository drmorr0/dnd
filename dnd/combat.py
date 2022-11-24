import logging
import secrets
from operator import itemgetter
from typing import List
from typing import Tuple

from dnd.char import Action
from dnd.char import Character
from dnd.char import State
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
    advantage = (target.state == State.Stunned)
    attack_roll, crit = d20(c.attack_bonus, can_crit=True, advantage=advantage)
    if advantage:
        logger.info(
            f'{c.name} attacks {target.name} with advantage: {attack_roll} versus {target.ac} AC',
        )
    else:
        logger.info(
            f'{c.name} attacks {target.name}: {attack_roll} versus {target.ac} AC',
        )
    return (attack_roll >= target.ac, crit)


def pool_attack(c, target) -> Tuple[bool, CriticalStatus]:
    base = 6 if target.state == State.Stunned else 5
    pool_size = base + c.attack_bonus
    attack_roll, crit = d6_pool(pool_size, can_crit=True)
    modified_ac = target.ac - 10
    logger.info(
        f'{c.name} attacks {target.name}: {attack_roll} versus {modified_ac} AC '
        f'(pool size = {pool_size})',
    )
    return (attack_roll >= modified_ac, crit)


def fight(team1: List[Character], team2: List[Character], attack) -> Tuple[int, int]:
    order = compute_initiative(team1, team2)
    rounds = 0
    while True:
        rounds += 1
        for (_, c, team) in order:
            if all([c.state == State.Dead for c in team1]):
                return (rounds, 2)
            if all([c.state == State.Dead for c in team2]):
                return (rounds, 1)

            if c.state != State.Alive:
                continue

            allies, opponents = (team2, team1) if team == 2 else (team1, team2)
            target, action = c.select_target(allies, opponents)
            # make sure this happens _after_ select_target so we don't re-stun
            stunned_target = c.stunned_target
            c.stunned_target = None

            if target is not None:
                if action == Action.Attack:
                    for _ in range(c.num_attacks):
                        hit, crit = attack(c, target)
                        dmg = c.compute_damage(hit, crit)
                        target.apply_dmg(dmg)
                        if dmg > 0:
                            logger.info(
                                f'{c.name} hits and deals {dmg} points of damage to {target.name}!'
                            )
                            logger.info(f'{target.name} has {target.hp} hp remaining')
                elif action == Action.Heal:
                    dmg = c.compute_special_damage()
                    healing = min(dmg, target.max_hp - target.hp)
                    target.hp += healing
                    logger.info(f'{c.name} heals {healing} points of damage to {target.name}!')
                    logger.info(f'{target.name} has {target.hp} hp remaining')
                elif action == Action.Stun:
                    logger.info(f'{c.name} stuns {target.name}')
                    c.stunned_target = target
                    target.state = State.Stunned

            if stunned_target is not None and stunned_target != c.stunned_target:
                stunned_target.state = State.Alive if stunned_target.hp > 0 else State.Dead

        logger.info('-----')
