import logging
import sys
from typing import Dict
from typing import List

from bokeh.layouts import grid
from bokeh.plotting import save

from dnd.char import Character
from dnd.combat import fight
from dnd.combat import d20_attack
from dnd.combat import pool_attack
from dnd.plot import plot_ac

NUM_TRIALS = 10000


def main() -> None:
    char1_file = sys.argv[1]
    print(f'reading character 1 from {char1_file}')
    char1 = Character(char1_file)
    print(char1)

    char2_file = sys.argv[2]
    print(f'reading character 2 from {char2_file}')
    char2 = Character(char2_file)
    print(char2)

    results: List[Dict] = [{}, {}]
    ac_list = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    for r_ind, attack_fn in enumerate([d20_attack, pool_attack]):
        for i in range(len(ac_list)):
            for j in range(i, len(ac_list)):
                char1.ac = ac_list[i]
                char2.ac = ac_list[j]
                print(f'{char1.name} ac: {char1.ac}; {char2.name} ac: {char2.ac}')

                rounds_accum = 0
                win_count = {1: 0, 2: 0}
                for _ in range(NUM_TRIALS):
                    char1.hp = char1.max_hp
                    char2.hp = char2.max_hp
                    rounds, winners = fight([char1], [char2], attack_fn)
                    rounds_accum += rounds
                    win_count[winners] += 1

                results[r_ind][(ac_list[i], ac_list[j])] = (
                    rounds_accum / NUM_TRIALS,
                    win_count[1],
                    win_count[2],
                )
                results[r_ind][(ac_list[j], ac_list[i])] = (
                    rounds_accum / NUM_TRIALS,
                    win_count[2],
                    win_count[1],
                )

    rounds_plots, win_ratio_plots = [], []
    for i in ac_list:
        d20_rounds = [results[0][(i, j)][0] for j in ac_list]
        pool_rounds = [results[1][(i, j)][0] for j in ac_list]
        d20_win_ratio = [
            results[0][(i, j)][1] / NUM_TRIALS
            for j in ac_list
        ]
        pool_win_ratio = [
            results[1][(i, j)][1] / NUM_TRIALS
            for j in ac_list
        ]
        rounds_plots.append(plot_ac(
            ac_list,
            d20_rounds,
            pool_rounds,
            f'Average Combat Rounds (AC = {i})',
            (0, 10),
        ))
        win_ratio_plots.append(plot_ac(
            ac_list,
            d20_win_ratio,
            pool_win_ratio,
            f'Average Win % (AC = {i})',
            (0, 1),
        ))

    
    g1 = grid(rounds_plots, ncols=3)  #type: ignore
    save(g1, filename='rounds.html')
    
    g2 = grid(win_ratio_plots, ncols=3)  #type: ignore
    save(g2, filename='win_ratio.html')
    print(results)



if __name__ == '__main__':
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.WARN)
    main()
