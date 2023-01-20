from random import random
from enum import Enum

from .cards import Card


class Round(Enum):
    PreFlop = 1
    Flop = 2
    Turn = 3
    River = 4


# TODO: more info could be acquired from the Java API
# https://www.poker-genius.com/api.php

class Game:
    """
    A game has 4 stages:
        preflop - Each player receives 2 hole cards. Nothing on board.
        flop - First 3 common cards on board.
        turn - Next common card on board.
        river - Last common card on board.
    A game can end at any stage.

    Within each stage, there are up to 4 bets.

    Bets to call ==

    """

    def __init__(self, small_blind, num_players, position, hole_cards):
        self.small_blind = small_blind
        self.board = []
        self.round = Round.PreFlop
        self.actions = []

        self.position = position
        assert len(hole_cards) == 2
        self.hole_cards = hole_cards

        self.our_chips_in_pot = 0
        self.check_raise_used = False

        # The number of chips the player has to call to stay in.
        # The type is float, not integer, because the small blind often has
        # 0.5 BB to call in the preflop betting.
        self.amount_to_call_in_bb = 0.0

        self.num_active_players = num_players
        self.number_of_unacted_players = 0

        self.max_bets = self.MAX_RAISES
        # number of bets so far in round
        self.num_bets = 0

        self.pot = 0
        self.pot_odds = 0
        self.bluff = random() < self.BLUFF_PROBABILITY

        # sets on every round
        self.best_hand_probability = None
        self.bet_size = None  # minBetSize on PreFlop, 1/2 Pot or MinBetSize on Flop, Turn, River
        self.negative_potential = None
        self.potential = None
        self.evaluator = None

    BLUFF_PROBABILITY = 0.2
    MAX_RAISES = 4  # Holdem.MAX_RAISES

    def _switch_round(self):
        # noinspection PyTypeChecker
        self.round = Round(self.round.value + 1)
        self.actions = []

    def deal_flop(self, c1, c2, c3):
        assert self.round == Round.PreFlop
        self.board = [c1, c2, c3]
        self._switch_round()

    def deal_turn(self, card):
        assert self.round == Round.Flop, self.round
        self.board.append(card)
        assert len(self.board) == 4
        self._switch_round()

    def deal_river(self, card):
        assert self.round == Round.Turn
        self.board.append(card)
        assert len(self.board) == 5
        self._switch_round()

    # private int finishCheckRaise() {
    #
    # 		// Clear flag
    # 		m_pendingCheckRaise = false;
    # 		// If there's a raise left, make it, else call.
    # 		if (m_gameInfo.getNumRaises() < Holdem.MAX_RAISES) {
    # 			// Set game flag
    # 			setGameInfo(KEY_CHECK_RAISE_USED, "yes");
    # 			return PokerConsts.RAISE;
    # 		}
    # 		else {
    # 			return PokerConsts.CALL;
    # 		}
    # 	}
    #

    def get_best_hand_probability(self):
        """
        Best at *this* moment. Ignores future potential, e.g.
        a 4-flush may turn into a flush.
        """
        if self.round == Round.PreFlop:
            # Probability not defined till there are board cards
            return 0.0

        if self.num_active_players == 2:
            # just 1 opponent
            return self.evaluator(self.hole_cards, self.board)

        return self.evaluator(self.hole_cards, self.board, self.num_active_players)

    def get_potential(self, looh_ahead_1_card=False):
        """
        Potential that the hand will improve.
        """
        if self.round == Round.PreFlop:
            # Potential not defined till there are board cards
            return 0.0

        if self.round == Round.Flop:
            return self.potential.ppot_raw(self.hole_cards, self.board, looh_ahead_1_card,
                                           # True  # Takes much longer
                                           )
        if self.round == Round.Turn:
            return self.potential.ppot_raw(self.hole_cards, self.board, looh_ahead_1_card)

        # river - no more potential
        return 0.0

    def get_negative_potential(self):
        """
        Potential that the hand will get worse.

        Call `get_potential()` first!
        """
        if self.round == Round.PreFlop:
            # Potential not defined till there are board cards
            return 0.0

        if self.round in [Round.Flop, Round.Turn]:
            return self.potential.getLastNPot()

        # river - no more potential
        return 0.0

    def get_pot_odds(self):
        """
        Ratio between what it costs to call and size of pot,

        E.g. $10 to call, $50 in pot, potOdds = 5.
        """

        return self.get_amount_to_call() / self.get_pot()

    def adjusted_probability(self):
        """
        adjusted-probability = best-hand-probability + potential - negative-potential.
        (How good the hand is now + its chances of getting better - its
        chances of getting worse.)
        """
        return self.best_hand_probability + self.potential - self.negative_potential

    def adjusted_odds(self):
        """
        adjusted-odds - adjusted-probability * pot-odds.

        Anything > 1 is a good bet.
        For example, if adjusted-probability is 0.33 and pot-odds are 4, we're getting good odds (1.33)
        If pot-odds are 2, we're getting poor odds (0.66).
        """
        return self.pot_odds * self.adjusted_probability()


def test():
    g = Game(1, 1, 2, [Card.parse('2h'), Card.parse('Jc')])
    g.deal_flop(*map(Card.parse, ['Qs', 'Td', '8d']))
    g.deal_turn(Card.parse('6h'))
    g.deal_river(Card.parse('Th'))
    for b in g.board:
        print(b)


if __name__ == '__main__':
    test()
