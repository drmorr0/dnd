import logging
import random
from enum import Enum
from typing import List
from typing import Tuple

logger = logging.getLogger(__name__)
HIT_MAP = [0, 0, 0, 0, 0, 1, 2]


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


def roll_plus_mod_crit(num_dice: int, sides: int, mod: int) -> Tuple[int, CriticalStatus]:
    nat_roll = max(roll(num_dice, sides))
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


def d20(mod: int, can_crit: bool = False, advantage: bool = False) -> Tuple[int, CriticalStatus]:
    num_dice = 2 if advantage else 1
    if can_crit:
        return roll_plus_mod_crit(num_dice, 20, mod)
    else:
        return roll_plus_mod(num_dice, 20, mod), CriticalStatus.Empty


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
