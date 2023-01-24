import argparse
import logging
import sys
from os import path

from . import RuleBasedPlayer

THIS_FILE = __file__
GEN_LIB_PATH = path.join(path.dirname(path.dirname(THIS_FILE)), 'genetic', 'Poker Genetic Algorithms')
sys.path.append(GEN_LIB_PATH)

from deepbet import DeepBetPlayer  # noqa: E402
from pypokerengine.api.game import setup_config, start_poker  # noqa: E402


def define_players(deepbet_url):
    return [
        {'name': "Rule1", 'algorithm': RuleBasedPlayer()},
        {'name': "Rule2", 'algorithm': RuleBasedPlayer()},
        {'name': "DeepBet", 'algorithm': DeepBetPlayer(deepbet_url, search_threads=128,
                                                       off_tree_actions_search_time_ms=10_000)},
        {'name': "Rule3", 'algorithm': RuleBasedPlayer()},
        {'name': "Rule4", 'algorithm': RuleBasedPlayer()},
        {'name': "Rule5", 'algorithm': RuleBasedPlayer()},
    ]


def players_shifted_button(deepbet_url, hand_number):
    players = define_players(deepbet_url)
    shift = hand_number % len(players)
    return players[shift:] + players[:shift]


def main():
    parser = argparse.ArgumentParser(description='Run this bot against the DeepBet')
    parser.add_argument('deepbet_url',
                        help="the base URL to connect to server (e.g. http://localhost:8080)")
    parser.add_argument('--iterations', '-i', required=True, type=int,
                        help='How many hands to play')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='show more verbose output')
    args = parser.parse_args()

    if args.verbose == 0:
        level = logging.WARNING
    elif args.verbose == 1:
        level = logging.INFO
    else:
        assert args.verbose >= 2
        level = logging.DEBUG
    logging.basicConfig(level=level,
                        format="[%(asctime)s] %(name)s:%(levelname)-8s %(filename)s:%(lineno)d -> %(message)s")

    for hand in range(args.iterations):
        config = setup_config(max_round=1, initial_stack=200, small_blind_amount=1)
        for p in players_shifted_button(args.deepbet_url, hand):
            config.register_player(**p)
        game_result = start_poker(config, verbose=1)
        print(game_result)


if __name__ == '__main__':
    main()
