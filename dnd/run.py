import argparse
import logging
import sys

from dnd.char import read_characters
from dnd.sims import run_ac_sim
from dnd.sims import run_comparison
from dnd.sims import run_single_d20
from dnd.sims import run_single_pool
from dnd.sims import run_single_2d10

NUM_TRIALS = 10000


def main(args: argparse.Namespace) -> None:
    team1 = read_characters(args.team1)
    team2 = read_characters(args.team2)

    if args.sim == 'ac':
        results = run_ac_sim(team1, team2, args.iterations, args.output_dir)
        print(results)
    if args.sim == 'comparison':
        run_comparison(team1, team2, args.iterations)
    if args.sim == 'single-d20':
        run_single_d20(team1, team2)
    if args.sim == 'single-pool':
        run_single_pool(team1, team2)
    if args.sim == 'single-2d10':
        run_single_2d10(team1, team2)


def parse_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='dnd',
        description=description,
    )
    parser.add_argument(
        '--log-level',
        default='warning',
        choices=['debug', 'info', 'warning']
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=NUM_TRIALS,
    )
    parser.add_argument(
        '--output-dir',
        default='./output',
    )
    parser.add_argument(
        '--sim',
        default='single-d20',
        choices=['ac', 'comparison', 'single-d20', 'single-pool', 'single-2d10'],
    )
    parser.add_argument('team1')
    parser.add_argument('team2')

    return parser.parse_args(sys.argv[1:])


def setup_logging(log_level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logging.getLogger().addHandler(handler)

    log_level = getattr(logging, args.log_level.upper())
    logging.getLogger().setLevel(log_level)


if __name__ == '__main__':
    args = parse_args('DnD 5e Simulator')
    setup_logging(args.log_level)
    main(args)
