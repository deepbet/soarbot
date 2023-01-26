import sys
from os import path
import logging

from .state import Game
from .cards import Card
from .rules import RuleHolder

THIS_FILE = __file__
GEN_LIB_PATH = path.join(path.dirname(path.dirname(THIS_FILE)), 'genetic', 'Poker Genetic Algorithms')
sys.path.insert(0, GEN_LIB_PATH)

from pypokerengine.api.game import BasePokerPlayer  # noqa: E402
import pypokerengine.utils.visualize_utils as U  # noqa: E402


class RuleBasedPlayer(BasePokerPlayer):
    def __init__(self, verbose=False):
        super().__init__()
        self.small_blind = None
        self.game_state = None
        self.verbose = verbose

    def declare_action(self, valid_actions, hole_card, round_state):
        if self.verbose:
            # print("*******************", valid_actions, hole_card, round_state)
            print(U.visualize_declare_action(valid_actions, hole_card, round_state, self.uuid, show_round_state=False))
        action, amount = RuleHolder(self.game_state, valid_actions).determine_action(self.uuid)
        return action, amount

    def receive_game_start_message(self, game_info):
        self.small_blind = game_info['rule']['small_blind_amount']
        if self.verbose:
            print(U.visualize_game_start(game_info, self.uuid))

    def receive_round_start_message(self, round_count, hole_card, seats):
        # print("++++++++++++++++++", round_count, hole_card, seats)

        ids = [p['uuid'] for p in seats]
        player_pos = ids.index(self.uuid)

        hole_cards = [Card.parse(c[1] + c[0]) for c in hole_card]
        self.game_state = Game(self.small_blind, ids, player_pos, hole_cards)
        if self.verbose:
            # for c in hole_cards: print(c)
            print(U.visualize_round_start(round_count, hole_card, seats, self.uuid))

    def receive_street_start_message(self, street, round_state):
        # print("%%%%%%%%%%%%%%%%%%%%%%%", street, round_state)
        if street == 'preflop':
            assert len(round_state['action_histories']) == 1
            blinds = round_state['action_histories']['preflop']
            assert len(blinds) == 2

            logging.debug(blinds)
            last_action = blinds[-1]
            logging.debug(last_action)
            paid = last_action.get('paid', last_action.get('add_amount'))
            self.game_state.set_blinds(last_action['action'], last_action['amount'], paid)
            self.game_state.set_pot(round_state['pot']['main']['amount'])

        if street == 'flop':
            cards = round_state['community_card'][:3]
            cards = [Card.parse(c[1] + c[0]) for c in cards]
            self.game_state.deal_flop(*cards)
        elif street == 'turn':
            cards = round_state['community_card'][3:4]
            cards = [Card.parse(c[1] + c[0]) for c in cards]
            self.game_state.deal_turn(*cards)
        elif street == 'river':
            cards = round_state['community_card'][4:5]
            cards = [Card.parse(c[1] + c[0]) for c in cards]
            self.game_state.deal_river(*cards)

        if self.verbose:
            print(U.visualize_street_start(street, round_state, self.uuid))

    def receive_game_update_message(self, new_action, round_state):
        # print("=========================", new_action, round_state)
        last_action = round_state['action_histories'][round_state['street']][-1]
        logging.debug(round_state['action_histories'][round_state['street']])
        logging.debug(last_action)
        paid = last_action.get('paid', last_action.get('add_amount'))
        player = new_action['player_uuid']
        self.game_state.register_action(player, new_action['action'], new_action['amount'], paid)
        self.game_state.set_pot(round_state['pot']['main']['amount'])

        if self.verbose:
            # do not print the round state
            print(U.visualize_game_update(new_action, round_state, self.uuid, show_round_state=False))

    def receive_round_result_message(self, winners, hand_info, round_state):
        if self.verbose:
            print(U.visualize_round_result(winners, hand_info, round_state, self.uuid))
