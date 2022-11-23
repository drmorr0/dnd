import argparse
import logging
import sys

from dnd.char import read_characters
from dnd.sims.ac import run_ac_sim

NUM_TRIALS = 10000


def main(args: argparse.Namespace) -> None:
    team1 = read_characters(args.team1)
    team2 = read_characters(args.team2)

    results = run_ac_sim(team1, team2, args.iterations, args.output_dir)
    print(results)


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
