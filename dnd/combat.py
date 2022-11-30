import logging
from operator import itemgetter
from random import random
from typing import List
from typing import Tuple

from dnd.char import Action
from dnd.char import Character
from dnd.char import State
from dnd.dice import Advantage
from dnd.dice import CriticalStatus
from dnd.dice import d20
from dnd.dice import d6_pool
from dnd.dice import _2d10

logger = logging.getLogger(__name__)
BASE_POOL_SIZE = 5


def compute_initiative(
    team1: List[Character],
    team2: List[Character],
) -> List[Tuple[float, Character, int]]:
    order = []
    for c in team1:
        # append a small random value to use as a tiebreaker
        r, _ = d20(c.init_mod)
        initiative = r + random()
        order.append((initiative, c, 1))

    for c in team2:
        # append a small random value to use as a tiebreaker
        r, _ = d20(c.init_mod)
        initiative = r + random()
        order.append((initiative, c, 2))

    order.sort(key=itemgetter(0), reverse=True)
    logger.info('Initiative Order:')
    for (i, c, team) in order:
        logger.info(f'{c.name} [{team}]: {i}')

    return order


def get_advantages(team: int) -> int:
    v = random()
    if team == 1:
        if v < 0.05:
            return -1
        elif v < 0.15:
            return 0
        elif v < 0.4:
            return 1
        elif v < 0.9:
            return 2
        else:
            return 3
    if team == 2:
        if v < 0.25:
            return -1
        elif v < 0.75:
            return 0
        else:
            return 1
    return 0


def d20_attack(c: Character, target: Character, adv: int) -> Tuple[bool, CriticalStatus]:
    advantage = Advantage.Empty
    if ((target.state == State.Stunned) and (adv >= 0)) or (adv > 0):
        advantage = Advantage.Advantage
    elif adv < 0:
        advantage = Advantage.Disadvantage

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


def _2d10_attack(c: Character, target: Character, adv: int) -> Tuple[bool, CriticalStatus]:
    if target.state == State.Stunned:
        adv += 1
    adv = max(min(adv, 3), -3)
    attack_roll, crit = _2d10(c.attack_bonus, can_crit=True, advantage=adv)
    logger.info(
        f'{c.name} attacks {target.name}: {attack_roll} versus {target.ac} AC'
    )
    return (attack_roll >= target.ac, crit)


def pool_attack(c: Character, target: Character, adv: int) -> Tuple[bool, CriticalStatus]:
    if target.state == State.Stunned:
        adv += 1
    adv = max(min(adv, 3), -3)
    pool_size = BASE_POOL_SIZE + c.attack_bonus + adv
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
                        adv = get_advantages(team)
                        # adv = 0
                        hit, crit = attack(c, target, adv)
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
