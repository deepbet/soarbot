import sys

from .state import Round
from .pos import BetTiming


class RuleHolder:
    def __init__(self, game_state, valid_actions):
        self.game_state = game_state
        self.valid_actions = valid_actions

    def valid_fold_action(self):
        action = self.valid_actions[0]
        assert action['action'] == 'fold'
        assert action['amount'] == 0
        return action

    def valid_call_action(self):
        action = self.valid_actions[1]
        assert action['action'] == 'call'
        return action

    def valid_raise_action(self):
        action = self.valid_actions[2]
        assert action['action'] == 'raise'
        return action

    def default_actions(self):
        """
        Should be run on every round
        """
        actions = []

        call_action = self.valid_call_action()
        if call_action['amount'] == 0:
            # If there's no cost to staying in the game, check.
            actions.append((call_action, 20))

        # Always propose fold.
        actions.append((self.valid_fold_action(), 10))
        return actions

    def raise_amount(self, pot_multiplier=1):  # TODO: change to dynamic pot size
        call_action = self.valid_call_action()
        raise_action = self.valid_raise_action()
        max_raise = raise_action['amount']['max']
        if max_raise > 0:
            # put a predetermined multiplier of the current pot
            pot_bet = self.game_state.pot * pot_multiplier
            # ensure the raise is valid in the given range
            raise_amount = max(pot_bet, raise_action['amount']['min'])
            raise_amount = min(raise_amount, max_raise)
            return raise_action['action'], raise_amount
        else:
            return call_action['action'], call_action['amount']

    def determine_action(self, our_id):
        # print(our_id, file=sys.stderr)
        # print(self.game_state.players_history[our_id], file=sys.stderr)
        current_round = self.game_state.round
        if current_round == Round.PreFlop:
            actions = self.determine_preflop()
        elif current_round == Round.Flop:
            actions = self.determine_flop()
        elif current_round == Round.Turn:
            actions = self.determine_turn()
        elif current_round == Round.River:
            actions = self.determine_river()
        else:
            raise NotImplementedError(f"Bad round {current_round}")

        # choose the action with the maximum priority
        the_action, _priority = max(actions, key=lambda x: x[1])
        # print(the_action, _priority, our_id, file=sys.stderr)
        if type(the_action) is dict:
            return the_action['action'], the_action['amount']
        else:
            assert len(the_action) == 2
            return the_action[0], the_action[1]

    def determine_preflop(self):
        actions = self.default_actions()

        for action in [
                self.preflop_check_raise(),
                self.preflop_call(),
                self.preflop_raise()]:
            if action:
                actions.append(action)

        return actions

    def continue_check_raise(self):
        """The second phase of the check-raise action: the raise"""
        call_action = self.valid_call_action()

        # was previously set (we already checked in this round)
        if self.game_state.check_raise_in_progress:
            assert len(self.game_state.actions) >= 1
            finish_status = self.game_state.finish_check_raise()
            if finish_status == 'call':
                return call_action, 40
            else:
                assert finish_status == 'raise'
                raise_action = self.raise_amount()
                if raise_action[0] == 'call':
                    return raise_action, 100

                assert raise_action[0] == 'raise'
                return raise_action, 40

    def preflop_check_raise(self):
        """
        If we've got the best cards, early position,
        and no bets yet, check-raise.
        """
        cont = self.continue_check_raise()
        if cont:
            return cont

        call_action = self.valid_call_action()
        strength = self.game_state.get_pocket_strength()

        # There’s always at least one bet in the preflop stage, because of the big blind.
        if self.game_state.num_bets() <= 1 \
                and self.game_state.get_bet_timing() == BetTiming.Early \
                and strength == 1:
            self.game_state.set_check_raise_in_progress()
            return call_action, 40

    def preflop_raise(self):
        raise_action = self.raise_amount()
        if raise_action[0] == 'call':
            return raise_action, 100

        assert raise_action[0] == 'raise'

        strength = self.game_state.get_pocket_strength()

        # If we've got the best cards, bet-raise as much as possible.
        if self.game_state.num_bets() < self.game_state.max_bets \
                and strength == 1:
            # bet-raise*always
            return raise_action, 30

        # If we've got excellent cards and excellent position, bet-raise as
        # much as possible.
        if self.game_state.num_bets() < self.game_state.max_bets \
                and self.game_state.get_bet_timing() == BetTiming.Blind \
                and strength <= 2:
            # bet-raise*excellent-both
            return raise_action, 30

        # If we've got excellent cards and excellent position, bet-raise as
        # much as possible.
        if self.game_state.num_bets() < self.game_state.max_bets \
                and self.game_state.get_bet_timing() in [BetTiming.Late, BetTiming.Button] \
                and strength <= 3:
            # bet-raise*excellent-both
            return raise_action, 30

        # If we've got excellent cards, bet-raise once.
        if self.game_state.num_bets() <= 1 \
                and strength <= 4:
            # bet-raise*excellent-cards
            return raise_action, 30

        # If we've got decent cards and excellent position, bet-raise once.
        if self.game_state.num_bets() <= 1 \
                and self.game_state.get_bet_timing() in [BetTiming.Late, BetTiming.Button, BetTiming.Blind] \
                and strength <= 5:
            # bet-raise*excellent-both
            return raise_action, 30

    def preflop_call(self):
        call_action = self.valid_call_action()

        strength = self.game_state.get_pocket_strength()

        if strength <= 3:
            # Decent cards - worth seeing the flop.
            return call_action, 20

        # If bluff flag is set, and we have good position, call.
        # The idea is to be less predictable by playing some cards we would
        # normally toss.
        if self.game_state.bluff \
                and self.game_state.get_bet_timing() in [BetTiming.Late, BetTiming.Button]:
            # call*bluff
            return call_action, 20

        if self.game_state.num_bets() == 1 \
                and self.game_state.get_bet_timing() in [BetTiming.Late, BetTiming.Button] \
                and strength <= 5:
            # Weak pairs, strong position, low cost - try to hit trips.
            return call_action, 20

        # small blind
        if self.game_state.position == 1 \
                and call_action['amount'] == self.game_state.small_blind \
                and strength <= 5:
            # Weak pairs, small blind, half a bet - try to hit trips.
            return call_action, 20

    def determine_flop(self):
        actions = self.default_actions()
        for action in [
                self.flop_call(),
                self.flop_raise()]:
            if action:
                actions.append(action)

        return actions

    def flop_raise(self):
        raise_action = self.raise_amount()
        if raise_action[0] == 'call':
            return raise_action, 100

        assert raise_action[0] == 'raise'

        strength = self.game_state.get_flop_strength()

        # If there's a bet or raise available to make.
        # Strongest hands, whenever possible.
        if self.game_state.num_bets() < self.game_state.max_bets \
                and strength == 1:
            # bet-raise*always
            return raise_action, 30

        # If no one else has raised yet, bet or raise.
        # We have a moderately strong hand, and we want to drive people out.
        if self.game_state.num_bets() <= 1 \
                and strength <= 3:
            # raise*first
            return raise_action, 30

        # If no one else has bet yet, bet for hands that have a chance to improve.
        # Make sure there's money in the pot, and no free rides.
        if self.game_state.num_bets() == 0 \
                and strength <= 4:
            # bet*first
            return raise_action, 30

    def flop_call(self):
        call_action = self.valid_call_action()

        strength = self.game_state.get_flop_strength()

        if strength <= 5:
            # stay in with good cards.
            return call_action, 20

        if self.game_state.num_bets() <= 1 \
                and strength <= 6:
            # stay in for 1 bet with cards that have some potential.
            return call_action, 20

        # Against just 1 player, stay in with almost anything.
        # This will help in cases where we're heads-up on the flop, and we're
        # getting driven out. This won't cost us more than 1 bet.
        if self.game_state.num_active_players() == 2 \
                and strength <= 7:
            return call_action, 20

    def determine_turn(self):
        actions = self.default_actions()
        for action in [
                self.turn_check_raise(),
                self.turn_raise(),
                self.turn_call()]:
            if action:
                actions.append(action)

        return actions

    def get_turn_strength(self):
        call_action = self.valid_call_action()
        return self.game_state.get_turn_strength(call_action['amount'])

    def turn_check_raise(self):
        """
        If we've got the best cards, early position,
        and no bets yet, check-raise.
        """
        cont = self.continue_check_raise()
        if cont:
            return cont

        call_action = self.valid_call_action()
        strength = self.get_turn_strength()

        if not self.game_state.check_raise_used:  # Just once per game
            # Strongest hands, no bets yet,
            # enough players after us for someone to make the first bet.

            if self.game_state.num_bets() == 0 \
                    and self.game_state.num_unacted_players() >= 4 \
                    and strength == 1:
                self.game_state.set_check_raise_in_progress()
                return call_action, 40

    def turn_raise(self):
        raise_action = self.raise_amount()
        if raise_action[0] == 'call':
            return raise_action, 100

        assert raise_action[0] == 'raise'

        strength = self.get_turn_strength()

        # If there's a bet or raise available to make.
        # Strongest hands, whenever possible.
        if self.game_state.num_bets() < self.game_state.max_bets \
                and strength == 1:
            # bet-raise*always
            return raise_action, 30

        # If there's just 1 bet, and we have a very good hand, raise.
        if self.game_state.num_bets() == 1 \
                and strength <= 2:
            # bet-raise*1-bet
            return raise_action, 30

        # Bet-first (semibluff included).
        if self.game_state.num_bets() == 0 \
                and strength <= 2.5:
            # bet-first*semibluff
            return raise_action, 30

        # If no one else has bet yet, and we're in good
        # position, and the game is short-handed, bet. We have a hand
        # we would normally call with, and we may be able to drive people out.
        if self.game_state.num_bets() == 0 \
                and strength <= 4 \
                and self.game_state.num_active_players() <= 3 \
                and self.game_state.num_unacted_players() <= 2:  # No more than 1 player behind us

            # bet-first*late*short-handed
            return raise_action, 30

        ca = self.game_state.get_cards_analyzer()
        has_blank_card = ca.is_blank_on_board()
        # If no one else has bet yet, and we're in last position,
        # and the turn was a blank (no-help card), bet with mediocre cards.
        # We may be able to drive people out, and the blank reduces the
        # chance of a check-raise.
        if self.game_state.num_bets() == 0 \
                and has_blank_card \
                and strength <= 7 \
                and self.game_state.num_unacted_players() == 1:  # We're last

            # bet-first*blank-on-board
            return raise_action, 30

    def turn_call(self):
        call_action = self.valid_call_action()

        strength = self.get_turn_strength()

        if strength <= 4:
            # stay in with good cards.
            return call_action, 20

        ca = self.game_state.get_cards_analyzer()
        has_blank_card = ca.is_blank_on_board()
        # Mediocre cards, but turn card was a blank (no help).
        # Defend against attempts to steal the pot.
        if has_blank_card and strength <= 7:
            # call*blank-on-board
            return call_action, 20

        # Mediocre cards, but just 1 player. Defend against
        # attempts to steal the pot.
        if self.game_state.num_active_players() == 2 \
                and strength <= 7:

            # call*just-1-player
            return call_action, 20

    def determine_river(self):
        strength = self.game_state.get_best_hand_probability()
        cards = list(map(str, self.game_state.get_cards_analyzer().all_cards()))
        print(f"HS for {cards}: {strength}", file=sys.stderr)

        actions = self.default_actions()
        for action in [
            self.river_check_raise(strength),
            self.river_raise(strength),
            self.river_call(strength)]:
            if action:
                actions.append(action)

        return actions

    def river_check_raise(self, hand_strength):
        """
        If we've got the best cards, early position,
        and no bets yet, check-raise.
        """
        cont = self.continue_check_raise()
        if cont:
            return cont

        call_action = self.valid_call_action()

        if not self.game_state.check_raise_used:  # Just once per game
            # Strongest hands, no bets yet,
            # enough players after us for someone to make the first bet.
            if self.game_state.num_bets() == 0 \
                    and self.game_state.num_unacted_players() >= 4 \
                    and hand_strength >= 0.9:
                self.game_state.set_check_raise_in_progress()
                return call_action, 40

    def river_raise(self, hand_strength):
        raise_action = self.raise_amount()
        if raise_action[0] == 'call':
            return raise_action, 100

        assert raise_action[0] == 'raise'

        # If we have a strong hand, bet or raise.
        if hand_strength >= 0.9:
            # bet-raise*based-on-probability
            return raise_action, 30

    def river_call(self, hand_strength):
        call_action = self.valid_call_action()
        pot_odds = self.game_state.get_pot_odds(call_action['amount'])
        strength = pot_odds * hand_strength
        print(f"Adjusted odds is {strength}", file=sys.stderr)

        if strength > 1.0:
            # If we like the odds, call.
            return call_action, 20
