import mock
import pytest

from dnd.char import Character
from dnd.dice import CriticalStatus


@pytest.fixture
def char():
    return Character({
        'name': 'Johnny McFighter',
        'hp': 10,
        'max_hp': 10,
        'attack': {
            'dmg': '1d6+3',
        },
    })


@pytest.fixture
def opponents():
    return [
        Character({
            'name': 'Healthy Dude',
            'hp': 10,
            'max_hp': 10,
        }),
        Character({
            'name': 'Hurty Face',
            'hp': 1,
            'max_hp': 10,
        }),
    ]


def test_select_target_empty(char):
    assert char.select_target([], []) is None


def test_select_target_all_dead(char, opponents):
    opponents[0].hp = -1
    opponents[1].hp = -1
    assert char.select_target([], opponents) is None


def test_select_target(char, opponents):
    assert char.select_target([], opponents).name == 'Hurty Face'


@pytest.mark.parametrize('hit,crit,dmg', [
    (False, CriticalStatus.Fail, 0),
    (False, CriticalStatus.Empty, 0),
    (False, CriticalStatus.Success, 8),
    (True, CriticalStatus.Fail, 0),
    (True, CriticalStatus.Empty, 8),
    (True, CriticalStatus.Success, 8),
])
def test_compute_damage(char, hit, crit, dmg):
    with mock.patch('dnd.char.roll_plus_mod', return_value=8) as mock_roller:
        assert char.compute_damage(hit, crit) == dmg
        if crit == CriticalStatus.Success:
            assert mock_roller.call_args_list == [mock.call(2, 6, 3)]
        elif hit and crit != CriticalStatus.Fail:
            assert mock_roller.call_args_list == [mock.call(1, 6, 3)]
