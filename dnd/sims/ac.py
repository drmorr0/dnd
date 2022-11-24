import logging
import os
from typing import Dict
from typing import List

from bokeh.layouts import grid
from bokeh.plotting import save

from dnd.char import Character
from dnd.combat import d20_attack
from dnd.combat import fight
from dnd.combat import pool_attack
from dnd.plot import plot_ac

logger = logging.getLogger(__name__)


def run_ac_sim(
    team1: List[Character],
    team2: List[Character],
    iterations: int,
    output_dir: str,
) -> List[Dict]:
    assert len(team1) == 1
    assert len(team2) == 1
    char1 = team1[0]
    char2 = team2[0]

    results: List[Dict] = [{}, {}]
    ac_list = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    for r_ind, attack_fn in enumerate([d20_attack, pool_attack]):
        for i in range(len(ac_list)):
            for j in range(i, len(ac_list)):
                ac_pair = (ac_list[i], ac_list[j])
                rev_ac_pair = (ac_list[j], ac_list[i])
                logger.warning(f"Running sim with AC = {ac_pair}")
                char1.ac, char2.ac = ac_pair

                rounds_accum = 0
                win_count = {1: 0, 2: 0}
                for _ in range(iterations):
                    char1.reset()
                    char2.reset()
                    rounds, winners = fight(team1, team2, attack_fn)
                    rounds_accum += rounds
                    win_count[winners] += 1

                results[r_ind][ac_pair] = (
                    rounds_accum / iterations,
                    win_count[1],
                    win_count[2],
                )
                results[r_ind][rev_ac_pair] = (
                    rounds_accum / iterations,
                    win_count[2],
                    win_count[1],
                )

    rounds_plots, win_ratio_plots = [], []
    for i in ac_list:
        d20_rounds = [results[0][(i, j)][0] for j in ac_list]
        pool_rounds = [results[1][(i, j)][0] for j in ac_list]
        d20_win_ratio = [
            results[0][(i, j)][1] / iterations
            for j in ac_list
        ]
        pool_win_ratio = [
            results[1][(i, j)][1] / iterations
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

    g1 = grid(rounds_plots, ncols=3)  # type: ignore
    save(g1, filename=os.path.join(output_dir, 'rounds.html'))

    g2 = grid(win_ratio_plots, ncols=3)  # type: ignore
    save(g2, filename=os.path.join(output_dir, 'win_ratio.html'))
    return results
