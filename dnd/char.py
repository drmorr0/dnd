import logging
import random
import re
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import yaml

from dnd.dice import CriticalStatus
from dnd.dice import roll_plus_mod

logger = logging.getLogger(__name__)


class Action(Enum):
    Attack = 1
    Heal = 2
    Stun = 3


class State(Enum):
    Alive = 1
    Stunned = 2
    Dead = 3


class Character:
    def __init__(self, obj: Dict[str, Any]) -> None:
        self.name = obj.get('name')
        self.init_mod = obj.get('initiative', 0)
        attack = obj.get('attack', {})
        self.num_attacks = attack.get('num')
        self.attack_bonus = attack.get('bonus')

        self.dmg_numd, self.dmg_sized, self.dmg_mod = parse_dice(attack.get('dmg', ''))
        self.ac = obj.get('ac')
        self.max_hp = obj.get('hp', 0)
        self.special = obj.get('special')
        if self.special and self.special.get('dice'):
            self.spec_numd, self.spec_sized, self.spec_mod = parse_dice(attack.get('dmg', ''))

        self.hp = self.max_hp
        self.state = State.Alive
        self.stunned_target: Optional['Character'] = None

    def select_target(
        self,
        allies: List['Character'],
        opponents: List['Character'],
    ) -> Tuple[Optional['Character'], Action]:
        if self.special:
            if self.special['type'] == 'heal':
                target = select_least_hp_active_char(allies, False)
                if target is not None:
                    return target, Action.Heal
            elif self.special['type'] == 'stun':
                # Can only use specials 1-in-4 times, and only if we haven't stunned something else
                if not self.stunned_target and random.random() < 0.25:
                    return (
                        random.choice([o for o in opponents if o.state != State.Dead]),
                        Action.Stun,
                    )
            else:
                raise ValueError('unknown special: {self.special["type"]}')

        target = select_least_hp_active_char(opponents)
        return target, Action.Attack

    def compute_damage(self, hit: bool, crit: CriticalStatus) -> int:
        dmg_dice = self.dmg_numd
        if crit == CriticalStatus.Fail:
            logger.info('Critical failure!')
            return 0
        elif crit == CriticalStatus.Empty and not hit:
            return 0
        elif crit == CriticalStatus.Success:
            dmg_dice *= 2
            logger.info('Critical hit!  Rolling double damage dice')
        dmg = roll_plus_mod(dmg_dice, self.dmg_sized, self.dmg_mod)
        return dmg

    def apply_dmg(self, dmg: int) -> None:
        self.hp -= dmg
        if self.hp <= 0:
            self.state = State.Dead

    def compute_special_damage(self) -> int:
        return roll_plus_mod(self.spec_numd, self.spec_sized, self.spec_mod)

    def reset(self) -> None:
        self.hp = self.max_hp
        self.state = State.Alive
        self.stunned_target = None

    def __str__(self) -> str:
        ab_str = f'+{self.attack_bonus}' if self.attack_bonus >= 0 else str(self.attack_bonus)
        mod_str = f'+{self.dmg_mod}' if self.dmg_mod >= 0 else str(self.dmg_mod)
        s = f'\nName: {self.name}\n'
        s += f'Attack: {self.num_attacks}x {ab_str} {self.dmg_numd}d{self.dmg_sized}{mod_str}\n'
        s += f'AC: {self.ac}\n'
        s += f'HP: {self.hp}\n'
        s += f'Init mod: {self.init_mod}\n'

        return s


def parse_dice(s: str) -> Tuple[int, int, int]:
    if s == '':
        return 0, 0, 0

    m = re.match(r'(\d+)d(\d+)((\+|-)\d+)?', s)
    if m is not None:
        return int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    else:
        raise ValueError(f'could not parse dice expression "{s}"')


def select_least_hp_active_char(
    chars: List[Character],
    include_full_health=True,
) -> Optional[Character]:
    target = None
    lowest_hp = 10000000
    # Immutably shuffle chars
    for c in random.sample(chars, k=len(chars)):
        if (
            c.state != State.Dead and
            c.hp < lowest_hp and
            (c.hp != c.max_hp or include_full_health)
        ):
            target = c
    return target


def read_characters(filename: str) -> List[Character]:
    with open(filename) as f:
        char_objs = yaml.safe_load(f)

    return [Character(c) for c in char_objs]
