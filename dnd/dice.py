import logging
import random
from enum import Enum
from typing import Callable
from typing import List
from typing import Tuple

logger = logging.getLogger(__name__)
HIT_MAP = [0, 0, 0, 0, 0, 1, 2]


class Advantage(Enum):
    Disadvantage = -1
    Empty = 0
    Advantage = 1


class CriticalStatus(Enum):
    Fail = -1
    Empty = 0
    Success = 1


def roll(num: int, sides: int) -> List[int]:
    rolls = [random.randint(1, sides) for i in range(num)]
    logger.debug(rolls)
    return rolls


def roll_plus_mod(num: int, sides: int, mod: int) -> int:
    return sum(roll(num, sides)) + mod


def roll_plus_mod_crit(num_dice: int, sides: int, mod: int, adv_fn: Callable) -> Tuple[int, CriticalStatus]:
    nat_roll = adv_fn(roll(num_dice, sides))
    crit = (
        CriticalStatus.Success
        if (nat_roll == sides)
        else (
            CriticalStatus.Fail
            if (nat_roll == 1)
            else CriticalStatus.Empty
        )
    )
    return nat_roll + mod, crit


def d20(mod: int, can_crit: bool = False, advantage: Advantage = Advantage.Empty) -> Tuple[int, CriticalStatus]:
    num_dice = 2 if advantage != Advantage.Empty else 1
    adv_fn = min if advantage == Advantage.Disadvantage else max
    if can_crit:
        return roll_plus_mod_crit(num_dice, 20, mod, adv_fn)
    else:
        return roll_plus_mod(num_dice, 20, mod), CriticalStatus.Empty


def _2d10(mod: int, can_crit: bool, advantage: int) -> Tuple[int, CriticalStatus]:
    crit = CriticalStatus.Empty
    d10s = roll(2, 10)
    if d10s[0] == 1 and d10s[1] == 1:
        crit = CriticalStatus.Fail
    elif d10s[0] == d10s[1]:
        crit = CriticalStatus.Success

    return sum(d10s) + (advantage * 3) + mod, crit


def d6_pool(num: int, can_crit: bool = False) -> Tuple[int, CriticalStatus]:
    crit_status = CriticalStatus.Empty
    crit_hits = 0
    if can_crit:
        crit_dice = roll(min(2, num), 6)
        crit_hits = sum(HIT_MAP[v] for v in crit_dice)
        num -= 2

        if len(crit_dice) == 2 and all([HIT_MAP[v] > 0 for v in crit_dice]):
            crit_status = CriticalStatus.Success
        elif all([v == 1 for v in crit_dice]):
            crit_status = CriticalStatus.Fail

    remaining_rolls = roll(num, 6)
    return sum([HIT_MAP[v] for v in remaining_rolls]) + crit_hits, crit_status
