import mock
import pytest

from dnd.char import Action
from dnd.char import Character
from dnd.char import State
from dnd.dice import CriticalStatus


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
    assert char.select_target([], []) == (None, Action.Attack)


def test_select_target_all_dead(char, opponents):
    opponents[0].state = State.Dead
    opponents[1].state = State.Dead
    assert char.select_target([], opponents) == (None, Action.Attack)


def test_select_target(char, opponents):
    o, a = char.select_target([], opponents)
    assert o.name == 'Hurty Face'
    assert a == Action.Attack


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
