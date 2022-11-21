import yaml
import re


class Character:
    def __init__(self, filename: str) -> None:
        with open(filename) as f:
            attrs = yaml.safe_load(f)

        self.name = attrs.get('name')
        self.init_mod = attrs.get('initiative')
        attack = attrs.get('attack')
        self.num_attacks = attack.get('num')
        self.attack_bonus = attack.get('bonus')

        m = re.match('(\d+)d(\d+)((\+|-)\d+)', attack.get('dmg'))

        self.dmg_numd = int(m.group(1))
        self.dmg_sized = int(m.group(2))
        self.dmg_mod = int(m.group(3))
        self.ac = attrs.get('ac')
        self.hp = attrs.get('hp')
        self.max_hp = attrs.get('hp')

    def __str__(self) -> str:
        ab_str = f'+{self.attack_bonus}' if self.attack_bonus >= 0 else str(self.attack_bonus)
        mod_str = f'+{self.dmg_mod}' if self.dmg_mod >= 0 else str(self.dmg_mod)
        s = f'\nName: {self.name}\n'
        s += f'Attack: {self.num_attacks}x {ab_str} {self.dmg_numd}d{self.dmg_sized}{mod_str}\n'
        s += f'AC: {self.ac}\n'
        s += f'HP: {self.hp}\n'
        s += f'Init mod: {self.init_mod}\n'

        return s
