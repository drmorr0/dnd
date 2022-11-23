import pytest

from dnd.char import Character


@pytest.fixture
def char():
    return Character({
        'name': 'Johnny McFighter',
        'hp': 10,
        'max_hp': 10,
        'ac': 19,
        'attack': {
            'bonus': 42,
            'dmg': '1d6+3',
        },
    })
