import concurrent.futures
import logging
import os
from copy import copy
from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple

from bokeh.layouts import grid
from bokeh.plotting import save

from dnd.char import Character
from dnd.combat import _2d10_attack
from dnd.combat import d20_attack
from dnd.combat import fight
from dnd.combat import pool_attack
from dnd.plot import plot_ac

logger = logging.getLogger(__name__)
AC_LIST = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]


def do_sim(
    team1: List[Character],
    team2: List[Character],
    iterations: int,
    attack_fn: Callable,
) -> Dict[Tuple[int, int], Tuple[float, int, int]]:
    char1 = team1[0]
    char2 = team2[0]
    results = {}
    for i in range(len(AC_LIST)):
        for j in range(len(AC_LIST)):
            ac_pair = (AC_LIST[i], AC_LIST[j])
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

            results[ac_pair] = (
                rounds_accum / iterations,
                win_count[1],
                win_count[2],
            )
    return results


def run_ac_sim(
    team1: List[Character],
    team2: List[Character],
    iterations: int,
    output_dir: str,
) -> List[Dict]:
    assert len(team1) == 1
    assert len(team2) == 1

    with concurrent.futures.ProcessPoolExecutor() as executor:
        fs = [
            executor.submit(do_sim, [copy(team1[0])], [copy(team2[0])], iterations, fn)
            for fn in (d20_attack, pool_attack, _2d10_attack)
        ]
        concurrent.futures.wait(fs)
        results = [f.result() for f in fs]

    rounds_plots, win_ratio_plots = [], []
    for i in AC_LIST:
        d20_rounds = [results[0][(i, j)][0] for j in AC_LIST]
        pool_rounds = [results[1][(i, j)][0] for j in AC_LIST]
        _2d10_rounds = [results[2][(i, j)][0] for j in AC_LIST]
        d20_win_ratio = [
            results[0][(i, j)][1] / iterations
            for j in AC_LIST
        ]
        pool_win_ratio = [
            results[1][(i, j)][1] / iterations
            for j in AC_LIST
        ]
        _2d10_win_ratio = [
            results[2][(i, j)][1] / iterations
            for j in AC_LIST
        ]
        rounds_plots.append(plot_ac(
            AC_LIST,
            d20_rounds,
            pool_rounds,
            _2d10_rounds,
            f'Average Combat Rounds (AC = {i})',
            (0, 10),
        ))
        win_ratio_plots.append(plot_ac(
            AC_LIST,
            d20_win_ratio,
            pool_win_ratio,
            _2d10_win_ratio,
            f'Average Win % (AC = {i})',
            (0, 1),
        ))

    g1 = grid(rounds_plots, ncols=3)  # type: ignore
    save(g1, filename=os.path.join(output_dir, 'rounds.html'))

    g2 = grid(win_ratio_plots, ncols=3)  # type: ignore
    save(g2, filename=os.path.join(output_dir, 'win_ratio.html'))
    return results
