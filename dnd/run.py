import logging
import sys

from bokeh.plotting import figure

from dnd.char import Character
from dnd.combat import fight
from dnd.combat import d20_attack
from dnd.combat import pool_attack

NUM_TRIALS = 10000


def main():
    char1_file = sys.argv[1]
    print(f'reading character 1 from {char1_file}')
    char1 = Character(char1_file)
    print(char1)

    char2_file = sys.argv[2]
    print(f'reading character 2 from {char2_file}')
    char2 = Character(char2_file)
    print(char2)

    results = [[], []]
    ac_list = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    for r_ind, attack_fn in enumerate([d20_attack, pool_attack]):
        for i in range(len(ac_list)):
            for j in range(i, len(ac_list)):
                char1.ac = ac_list[i]
                char2.ac = ac_list[j]
                print(f"{char1.name} ac: {char1.ac}; {char2.name} ac: {char2.ac}")

                rounds_accum = 0
                win_count = {1: 0, 2: 0}
                for _ in range(NUM_TRIALS):
                    char1.hp = char1.max_hp
                    char2.hp = char2.max_hp
                    rounds, winners = fight([char1], [char2], attack_fn)
                    rounds_accum += rounds
                    win_count[winners] += 1

                results[r_ind].append((
                    ac_list[i],
                    ac_list[j],
                    rounds_accum / NUM_TRIALS,
                    win_count[1],
                    win_count[2],
                ))

    print(results)


if __name__ == '__main__':
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.WARN)
    main()
