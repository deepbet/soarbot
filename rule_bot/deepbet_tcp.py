import json
import random
import logging
import socket
import sys
import io
import time
from contextlib import redirect_stdout
from threading import Thread

from mutf8 import encode_modified_utf8, decode_modified_utf8

from . import convert

import pypokerengine.utils.visualize_utils as U
from pypokerengine.players import BasePokerPlayer


TABLE_NAME = 'TestWithRuleBot'


class DeepBetPlayer(BasePokerPlayer):
    def __init__(self, addr, search_time_ms=None, out=sys.stdout):
        super().__init__()
        addr = addr.split(':', maxsplit=1)
        self.api = Api(addr, search_time_ms=search_time_ms, verbose=2)
        self.game_settings = None
        self.session_id = None
        self.game_id = None
        self.all_in_made = None
        self.all_in_sent = False
        self.out = out

    def declare_action(self, valid_actions, hole_card, round_state):
        current_round = round_state['street']
        actions = round_state['action_histories'].get(current_round, [])
        total_paid = 0
        for action in actions:
            if action['uuid'] == self.uuid:
                if 'BLIND' in action['action']:
                    total_paid += action['amount']
                else:
                    total_paid += action.get('paid', 0)

        print(U.visualize_declare_action(valid_actions, hole_card, round_state, self.uuid, show_round_state=False),
              file=self.out)
        action, amount, all_in = self.api.get_rts_action(self.game_id, valid_actions, total_paid, self.all_in_made is not None)
        if all_in is not None:
            logging.info("Received AllIn: %s", all_in)
            self.all_in_made = all_in
        return action, amount

    def receive_game_start_message(self, game_info):
        hero_name = "UNKNOWN"
        for p in game_info['seats']:
            if p['uuid'] == self.uuid:
                hero_name = p['name']

        players = [{'name': p['name'], 'id': i, 'stack': p['stack']}
                   for i, p in enumerate(game_info['seats'])]

        # rotate to make a Button the last in the list
        players = players[1:] + players[:1]

        self.game_settings = {
            'starting_stack': game_info['rule']['initial_stack'],
            'small_blind': game_info['rule']['small_blind_amount'],
            'players': players
        }

        if self.session_id is None:
            self.session_id = self.api.create_session(hero_name, len(players))

        print(U.visualize_game_start(game_info, self.uuid),
              file=self.out)

    def receive_round_start_message(self, round_count, hole_card, seats):
        ids = [p['uuid'] for p in seats]
        player_pos = ids.index(self.uuid)

        # if len(seats) == 2:
        #     order = ["BigBlind", "SmallBlind"]
        # else:
        #     order = ["Button", "SmallBlind", "BigBlind", "UnderTheGun", "Middle", "Cutoff"]

        hero_name = "UNKNOWN"
        for p in seats:
            if p['uuid'] == self.uuid:
                hero_name = p['name']

        private_info = [{"hole_cards": pp_to_array(hole_card), "position": player_pos + 1, "name": hero_name}]
        query = {'game_settings': self.game_settings, 'private_info': private_info}
        self.game_id = self.api.create_game(query)
        self.all_in_made = None
        self.all_in_sent = False
        print(U.visualize_round_start(round_count, hole_card, seats, self.uuid),
              file=self.out)

    def receive_street_start_message(self, street, round_state):
        if street == 'flop':
            cards = round_state['community_card'][:3]
        elif street == 'turn':
            cards = round_state['community_card'][3:4]
        elif street == 'river':
            cards = round_state['community_card'][4:5]
        else:
            cards = []

        logging.info("Dealing cards %r on %r (round=%r)", cards, self.game_id, street)

        if cards:
            if self.all_in_made is None:
                self.api.deal_board_cards(self.game_id, pp_to_array(cards), street)
            else:
                logging.warning("Ignore sending cards %s: AllIn was made", cards)

        print(U.visualize_street_start(street, round_state, self.uuid),
              file=self.out)

    def receive_game_update_message(self, new_action, round_state):
        last_action = round_state['action_histories'][round_state['street']][-1]
        logging.debug(round_state['action_histories'][round_state['street']])
        logging.debug(last_action)
        paid = last_action.get('paid', last_action.get('add_amount'))

        name = None
        stack = None
        uuid = new_action['player_uuid']
        for p in round_state['seats']:
            if p['uuid'] == uuid:
                name = p['name']
                stack = p['stack']

        action_made = {'action': new_action['action'], 'amount': new_action['amount']}

        if stack == 0:
            logging.info("Changing to AllIn: %s", action_made)
            action_made['action'] = 'all-in'

        if uuid == self.uuid:
            if self.all_in_sent:
                logging.warning("AllIn was sent already, the action %s will be ignored", new_action)
            else:
                if self.all_in_made is not None:
                    action_made = {'action': 'all-in', 'amount': self.all_in_made}
                    logging.warning("AllIn will be sent: %s, but all the following actions will be ignored", action_made)
                    self.all_in_sent = True

                self.api.register_action(self.game_id, action_made['action'], action_made['amount'], paid, name)
        else:
            self.api.register_action(self.game_id, action_made['action'], action_made['amount'], paid, name)

        print(U.visualize_game_update(new_action, round_state, self.uuid, show_round_state=False),
              file=self.out)

    def receive_round_result_message(self, winners, hand_info, round_state):
        print(U.visualize_round_result(winners, hand_info, round_state, self.uuid),
              file=self.out)
        self.send_history()
        self.api.delete_game(self.game_id)

    def send_history(self):
        if type(self.out) is io.StringIO:
            val = self.out.getvalue()
            print(val)
            with io.StringIO() as buf, redirect_stdout(buf):
                try:
                    lines = iter(val.splitlines())
                    convert.main(lines, TABLE_NAME, self.game_id)
                except Exception as exc:
                    logging.error("HH failed: %r", exc)
                else:
                    data = buf.getvalue()
                    self.api.send_history(data)

            # https://stackoverflow.com/a/4330829
            self.out.truncate(0)
            self.out.seek(0)


class Api:
    def __init__(self, addr, search_time_ms=None, verbose=0):
        self.server_host = addr[0]
        self.server_port = int(addr[1])

        self.search_time_ms = search_time_ms

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.verbose = verbose
        self.connect()
        self.ping()
        self.recv_thread = Thread(target=self.run_recv, daemon=True).start()
        self.responses = dict()

    def connect(self):
        self.socket.connect((self.server_host, self.server_port))

        if self.verbose > 0:
            print(f"Connecting to {self.server_host}:{self.server_port}...", file=sys.stderr)

    def ping(self):
        self._send_to_socket(command="PING")

    def _send_to_socket(self, **data):
        """
        Send the length of the data first, then the data itself
        """
        data = json.dumps(data)
        bytes_data = encode_modified_utf8(data)
        size = len(bytes_data).to_bytes(2, byteorder='big')
        self.socket.sendall(size)
        self.socket.sendall(bytes_data)

    def run_recv(self):
        while True:
            size = self.socket.recv(2)
            size = int.from_bytes(size, byteorder='big')
            logging.info(f'About to receive {size} bytes')
            if size == 0:
                time.sleep(0.1)
                continue
            data = self.socket.recv(size)
            assert len(data) == size
            data = decode_modified_utf8(data)
            for msg in data.splitlines(keepends=False):
                try:
                    msg = json.loads(msg)
                    if msg.get('command') == "ANSWER":
                        logging.warning("Received a response %r", msg)
                        self.responses[int(msg['id'])] = msg
                    else:
                        logging.warning("Received unknown response %r", msg)
                except ValueError:
                    if msg.startswith('ERROR'):
                        logging.error("Received a message %r", msg)
                    else:
                        logging.error("Received a message %r", msg)

    HAND_ID_START = 200_000_000

    def create_session(self, player_name, table_size):
        table_size = int(table_size)

        # blinds in 1/100 of chips
        # could be any placeholder for the session, but mandatory for the game
        # small_blind = int(small_blind)
        # if big_blind is None:
        #     big_blind = small_blind * 2
        # else:
        #     big_blind = int(big_blind)
        small_blind = 1
        big_blind = 2

        session_id = random.randrange(self.HAND_ID_START, self.HAND_ID_START * 2)
        session_id = f"Session{session_id}"
        table_id = random.randrange(self.HAND_ID_START, self.HAND_ID_START * 2)

        data = {
            'command': 'START SESSION',
            'sessionId': session_id,
            'gameType': 'NLH',
            'bb': big_blind,
            'sb': small_blind,
            'tableId': f"Table{table_id}",
            'tableSize': table_size,
            'accountId': TABLE_NAME,
            'accountScreenName': player_name,
        }
        self._send_to_socket(**data)
        return session_id

    def end_session(self):
        self._send_to_socket(command="END SESSION")

    def start_game(self, small_blind, big_blind=None):
        # blinds in chips
        small_blind = float(small_blind)
        if big_blind is None:
            big_blind = small_blind * 2
        else:
            big_blind = float(big_blind)

        game_id = str(random.randrange(self.HAND_ID_START, self.HAND_ID_START * 2))

        data = {
            'command': 'START GAME',
            'gameId': game_id,
            'gameType': 'NLH',
            'bb': big_blind,
            'sb': small_blind,
        }
        self._send_to_socket(**data)
        return game_id

    def send_history(self, data):
        self._send_to_socket(command="HAND HISTORY", hh=data)

    def end_game(self):
        self._send_to_socket(command="END GAME")

    def send_seat(self, seat, stack, name):
        self._send_to_socket(command="SEAT", seat=int(seat), stack=float(stack), accountScreenName=name)

    def send_dealer(self, seat):
        self._send_to_socket(command="DEALER", seat=int(seat))

    def send_event(self, action, name, seat=None, amount=None, **kwargs):
        data = {
            'command': "EVENT",
            'action': str(action).upper(),
            'accountScreenName': name,
        }
        data.update(kwargs)
        if seat is not None:
            data['seat'] = int(seat)

        if amount is not None:
            data['amount'] = float(amount)

        self._send_to_socket(**data)

    def send_cards(self, round_name, cards=()):
        data = {
            'command': "EVENT",
            'action': str(round_name).upper()
        }
        if cards:
            data['cards'] = ','.join(map(str, cards))

        self._send_to_socket(**data)

    def request_for_action(self):
        req_id = random.randrange(self.HAND_ID_START, self.HAND_ID_START * 2)
        data = {
            'command': "BUTTONS",
            'id': req_id,
            'buttons': "FKCBRA",
            'timeout': self.search_time_ms
        }

        self._send_to_socket(**data)
        return req_id

    MAX_WAIT_RESPONSE_SECONDS = 60

    def wait_response(self, req_id):
        start_waiting = time.time()
        while True:
            resp = self.responses.pop(req_id, None)
            if resp is not None:
                return resp
            if time.time() - start_waiting > self.MAX_WAIT_RESPONSE_SECONDS:
                raise TimeoutError(f"Waiting for {req_id} timed out ({self.MAX_WAIT_RESPONSE_SECONDS}s)")
            time.sleep(0.01)

    def get_response_action(self, req_id):
        resp = self.wait_response(req_id)
        # EXPECTED: {"amount":"-","delay":1531,"action":"F","id":57,"command":"ANSWER","quality":"Normal"}
        logging.info("Received response on %s: %r", req_id, resp)
        resp.pop('command', None)
        resp.pop('quality', None)
        resp.pop('delay', None)
        assert resp.pop('id') == req_id
        return resp

    def create_game(self, create_request):
        logging.info("Creating a game: %r", create_request)

        game_settings = create_request['game_settings']
        sb = game_settings['small_blind']
        players = game_settings['players']

        game_id = self.start_game(sb)
        for i, p in enumerate(players, 1):
            self.send_seat(i, p['stack'], p['name'])

        number_of_players = len(players)
        if number_of_players == 2:
            # Small Blind is the dealer
            dealer = 1
        else:
            # the last is the dealer
            dealer = number_of_players

        self.send_dealer(dealer)

        self.send_event("BLIND SB", players[0]['name'], seat=1, amount=sb)
        self.send_event("BLIND BB", players[1]['name'], seat=2, amount=sb * 2)
        self.send_cards("PREFLOP")

        private_info = create_request['private_info']
        assert len(private_info) == 1
        private_info = private_info[0]
        self.send_event("DEALT", private_info['name'], seat=private_info['position'],
                        holes=','.join(private_info['hole_cards']))

        logging.info("Game was created: %r", game_id)
        return game_id

    def delete_game(self, game_id):
        logging.info("Deleting a game: %r", game_id)
        self.end_game()

    @classmethod
    def _action_data(cls, action, _amount, paid):
        if action == "fold":
            return {'action': 'FOLD'}
        elif action == "call":
            if paid:
                paid = round(paid, 5)
                return {'action': 'CALL', 'amount': paid}
            else:
                return {'action': 'CHECK'}
        elif action == "raise":
            if paid is None:
                paid = 0
            else:
                round(paid, 5)
            return {'action': 'RAISE', 'amount': paid}
        elif action == "all-in":
            if paid is None:
                paid = 0
            else:
                round(paid, 5)
            return {'action': 'ALL-IN', 'amount': paid}

    def register_action(self, game_id, action, amount, paid, name):
        logging.debug("Register action %r(%s, paid=%s) on %r (player=%r)", action, amount, paid, game_id, name)

        data = self._action_data(action, amount, paid)
        data['name'] = name
        logging.info("The action data is %r", data)
        self.send_event(**data)

    def get_rts_action(self, game_id, valid_actions, total_paid, was_all_in_before=False):
        start = time.time()
        logging.info("Requesting strategy on %r", game_id)
        all_in = None

        [fold_action, call_action, raise_action] = valid_actions[:3]

        if was_all_in_before:
            logging.error("Bad python engine handling: selecting Call(%s)", call_action['amount'])
            resp = {'action': 'C', 'amount': call_action['amount']}
        else:
            req_id = self.request_for_action()
            resp = self.get_response_action(req_id)

        logging.info("Chosen action is %s (in %.3f s)", resp, time.time() - start)

        if resp['action'] == "F":
            return fold_action['action'], fold_action['amount'], all_in

        if resp['action'] in ('K', 'C'):
            total_call = total_paid + float(resp['amount'])
            assert abs(total_call - call_action['amount']) < 1e-7
            return call_action['action'], call_action['amount'], all_in

        max_raise = raise_action['amount']['max']
        if resp['action'] == "A":
            all_in = round(float(resp['amount']), 5)

            total = round(total_paid + all_in, 5)
            if max_raise > 0:
                total = min(max_raise, total)
                assert abs(total - max_raise) < 1e-7

            if abs(total - call_action['amount']) < 1e-7:
                action = call_action['action']
            else:
                action = raise_action['action']
            return action, total, all_in

        if resp['action'] in ('B', 'R'):
            bet = total_paid + float(resp['amount'])
            if max_raise > 0:
                return raise_action['action'], bet, all_in
            else:
                return call_action['action'], call_action['amount'], all_in

        raise ValueError(f"Invalid action: {resp}")

    def deal_board_cards(self, game_id, cards, round_name):
        logging.debug("Dealing cards %r on %r (round=%r)", cards, game_id, round_name)

        round_name = round_name.upper()

        if len(cards) == 3:
            assert round_name == 'FLOP'
        elif len(cards) == 1:
            assert round_name in ('TURN', 'RIVER')
        else:
            raise ValueError(f"Bad number of cards: {len(cards)}")

        self.send_cards(round_name, cards)

    def __del__(self):
        self.end_session()


def pp_to_array(hand):
    return [card[1] + card[0].lower() for card in hand]
