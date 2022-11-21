import mock
import pytest

from dnd.dice import d6_pool
from dnd.dice import roll
from dnd.dice import roll_plus_mod
from dnd.dice import roll_plus_mod_crit
from dnd.dice import CriticalStatus
from dnd.dice import HIT_MAP


@pytest.mark.parametrize('num', [0, -1])
def test_roll_empty(num):
    assert roll(num, 30) == []


def test_roll_plus_mod():
    with mock.patch('dnd.dice.secrets.randbelow', side_effect=[7, 8]):
        assert roll_plus_mod(2, 20, 3) == 20


@pytest.mark.parametrize('roll_value,status', [
    (20, CriticalStatus.Success),
    (1, CriticalStatus.Fail),
    (5, CriticalStatus.Empty),
])
def test_roll_plus_mod_crit(roll_value, status):
    with mock.patch('dnd.dice.secrets.randbelow', return_value=roll_value-1):
        assert roll_plus_mod_crit(20, 3) == (roll_value + 3, status)


@pytest.mark.parametrize('roll_value,status', [
    (6, CriticalStatus.Empty),
    (5, CriticalStatus.Empty),
    (4, CriticalStatus.Empty),
    (1, CriticalStatus.Fail),
])
def test_d6_pool_one_die(roll_value, status):
    with mock.patch('dnd.dice.secrets.randbelow', return_value=roll_value-1):
        assert d6_pool(1, True) == (HIT_MAP[roll_value], status)


@pytest.mark.parametrize('c1,c2,status', [
    (6, 6, CriticalStatus.Success),
    (5, 6, CriticalStatus.Success),
    (6, 5, CriticalStatus.Success),
    (5, 5, CriticalStatus.Success),
    (4, 5, CriticalStatus.Empty),
    (1, 6, CriticalStatus.Empty),
    (1, 1, CriticalStatus.Fail),
])
def test_d6_pool_two_dice(c1, c2, status):
    with mock.patch('dnd.dice.secrets.randbelow', side_effect=[c1-1, c2-1]):
        assert d6_pool(2, True) == (HIT_MAP[c1] + HIT_MAP[c2], status)


@pytest.mark.parametrize('c1,c2,status', [
    (6, 6, CriticalStatus.Success),
    (5, 6, CriticalStatus.Success),
    (6, 5, CriticalStatus.Success),
    (5, 5, CriticalStatus.Success),
    (4, 5, CriticalStatus.Empty),
    (1, 6, CriticalStatus.Empty),
    (1, 1, CriticalStatus.Fail),
])
def test_d6_pool_four_dice(c1, c2, status):
    with mock.patch('dnd.dice.secrets.randbelow', side_effect=[c1-1, c2-1, 4-1, 5-1]):
        assert d6_pool(4, True) == (HIT_MAP[c1] + HIT_MAP[c2] + 1, status)
