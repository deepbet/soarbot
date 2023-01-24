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

    def raise_amount(self, pot_multiplier=1):   # TODO: change to dynamic pot size
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

    def determine_action(self):
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
        the_action, _ = max(actions, key=lambda x: x[1])
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
                and self.game_state.get_pocket_strength() == 1:
            self.game_state.check_raise_in_progress = True
            return call_action, 40

    def preflop_raise(self):
        raise_action = self.raise_amount()
        if raise_action[0] == 'call':
            return raise_action, 100

        assert raise_action[0] == 'raise'

        # If we've got the best cards, bet-raise as much as possible.
        if self.game_state.num_bets() < self.game_state.max_bets \
                and self.game_state.get_pocket_strength() == 1:
            # bet-raise*always
            return raise_action, 30

        # If we've got excellent cards and excellent position, bet-raise as
        # much as possible.
        if self.game_state.num_bets() < self.game_state.max_bets \
                and self.game_state.get_bet_timing() in [BetTiming.Late, BetTiming.Button] \
                and self.game_state.get_pocket_strength() <= 2:
            # bet-raise*excellent-both
            return raise_action, 30

        # If we've got excellent cards, bet-raise once.
        if self.game_state.num_bets() <= 1 \
                and self.game_state.get_pocket_strength() <= 2:
            # bet-raise*excellent-cards
            return raise_action, 30

        # If we've got decent cards and excellent position, bet-raise once.
        if self.game_state.num_bets() <= 1 \
                and self.game_state.get_bet_timing() in [BetTiming.Late, BetTiming.Button] \
                and self.game_state.get_pocket_strength() <= 3:
            # bet-raise*excellent-both
            return raise_action, 30

    def preflop_call(self):
        call_action = self.valid_call_action()

        if self.game_state.get_pocket_strength() <= 3:
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
                and self.game_state.get_pocket_strength() <= 5:
            # Weak pairs, strong position, low cost - try to hit trips.
            return call_action, 20

        # small blind
        if self.game_state.position == 1 \
                and call_action['amount'] == self.game_state.small_blind \
                and self.game_state.get_pocket_strength() <= 5:
            # Weak pairs, small blind, half a bet - try to hit trips.
            return call_action, 20

    def determine_flop(self):
        actions = self.default_actions()
        # TODO (flop.soar)
        return actions

    def determine_turn(self):
        actions = self.default_actions()
        # TODO (turn.soar)
        return actions

    def determine_river(self):
        actions = self.default_actions()
        # TODO (river.soar)
        return actions
