import mock
import pytest

from dnd.char import Character
from dnd.char import State
from dnd.combat import d20_attack


@pytest.fixture
def target():
    return Character({
        'name': 'Derpy McDerp',
        'hp': 10,
        'max_hp': 10,
        'ac': 14,
    })


@pytest.mark.parametrize('adv', [True, False])
def test_d20_attack(char, target, adv):
    target.state = State.Stunned if adv else State.Alive
    with mock.patch('dnd.combat.d20', return_value=(17, True)) as mock_d20:
        hit, crit = d20_attack(char, target)
        assert hit
        assert crit
        assert mock_d20.call_args_list == [
            mock.call(42, can_crit=True, advantage=adv)
        ]
