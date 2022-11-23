import logging
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import yaml

from dnd.dice import CriticalStatus
from dnd.dice import roll_plus_mod

logger = logging.getLogger(__name__)


class Character:
    def __init__(self, obj: Dict[str, Any]) -> None:
        self.name = obj.get('name')
        self.init_mod = obj.get('initiative', 0)
        attack = obj.get('attack', {})
        self.num_attacks = attack.get('num')
        self.attack_bonus = attack.get('bonus')

        m = re.match(r'(\d+)d(\d+)((\+|-)\d+)', attack.get('dmg', ''))
        if m is not None:
            self.dmg_numd = int(m.group(1))
            self.dmg_sized = int(m.group(2))
            self.dmg_mod = int(m.group(3))
        self.ac = obj.get('ac')
        self.hp = obj.get('hp', 0)
        self.max_hp = obj.get('hp')

    # Default behaviour is to just select the target with the lowest hit points;
    # this can be overriden by subclasses to change target selection behaviour
    def select_target(
        self,
        allies: List['Character'],
        opponents: List['Character'],
    ) -> Optional['Character']:
        target = None
        lowest_hp = 10000000
        for c in opponents:
            if c.hp > 0 and c.hp < lowest_hp:
                target = c
        return target

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
        logger.info(f'{self.name} hits and deals {dmg} points of damage!')
        return dmg

    def __str__(self) -> str:
        ab_str = f'+{self.attack_bonus}' if self.attack_bonus >= 0 else str(self.attack_bonus)
        mod_str = f'+{self.dmg_mod}' if self.dmg_mod >= 0 else str(self.dmg_mod)
        s = f'\nName: {self.name}\n'
        s += f'Attack: {self.num_attacks}x {ab_str} {self.dmg_numd}d{self.dmg_sized}{mod_str}\n'
        s += f'AC: {self.ac}\n'
        s += f'HP: {self.hp}\n'
        s += f'Init mod: {self.init_mod}\n'

        return s


def read_characters(filename: str) -> List[Character]:
    with open(filename) as f:
        char_objs = yaml.safe_load(f)

    return [Character(c) for c in char_objs]
