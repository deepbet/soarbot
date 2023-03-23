from .cards import Card, Rank
from .pos import BetTiming


class PocketAnalyzer:
    def __init__(self, h1, h2):
        assert h1 != h2, f"Bad pocket: {[h1, h2]} are same cards"
        self.high, self.low = Card.sort_by_rank_desc([h1, h2])

    def is_pair(self):
        r1 = self.high.rank
        r2 = self.low.rank
        if r1 == r2:
            return r1
        return None

    def preflop_strength(self):
        r1 = self.high.rank
        r2 = self.low.rank
        # pairs
        if r1 == r2:
            if r1 == Rank.Ace:
                # pair-aces
                return 1

            if Rank.Ten <= r1 <= Rank.King:
                # strong-pairs
                return 2

            if r1 < Rank.Ten:
                # weak-pairs
                return 3

        # Suited cards - both hole cards are the same suit.
        if self.high.same_suit(self.low):
            if r1 == Rank.Ace and r2 == Rank.King:
                # ace-king-suited
                return 1
            if Rank.Jack <= r1 <= Rank.Ace:
                if Rank.Jack <= r2 <= Rank.Ace:
                    # 2-high-cards-suited
                    return 2
                else:
                    # high-card-suited
                    return 3

            # Extra value because the cards are connected (possible straight).
            if r2.next() == r1:
                return 3

            # Extra value because the cards are connected (possible straight).
            if r2.next().next() == r1:
                return 4

        # Unpaired, unsuited
        assert self.is_pair() is None, "Pairs should be handled before"
        # assert self.high.off_suit(self.low), \
        #     f"Suited should be handled before, [{self.high}, {self.low}]"

        if r1 == Rank.Ace:
            if r2 == Rank.King:
                # ace-king
                return 2
            if r2 in (Rank.Ten, Rank.Nine, Rank.Eight, Rank.Seven):
                return 3

        if r1 == Rank.King:
            if r2 in (Rank.Ten, Rank.Nine):
                return 3

        if r1 == Rank.Queen:
            if r2 == Rank.Ten:
                return 3

        if Rank.Jack <= r1 <= Rank.Ace:
            if Rank.Jack <= r2 <= Rank.Ace:
                # 2-high-cards
                return 3
            else:
                return 4

        # all the left cards are pretty-useless to go further
        return 100

    def is_strong_for_check(self, bet_timing: BetTiming, is_small_blind=False):
        high_r, low_r = self.high.rank, self.low.rank
        suited = self.high.same_suit(self.low)
        pair_r = self.is_pair()

        if bet_timing == BetTiming.Blind:
            if pair_r is not None and pair_r >= Rank.Seven:
                return True
            if is_small_blind:
                if suited:
                    if high_r == Rank.Ace:
                        return True
                    if high_r == Rank.King and low_r >= Rank.Six:
                        return True
                    if high_r >= Rank.Ten and low_r >= Rank.Eight:
                        return True
                    if high_r in (Rank.Nine, Rank.Eight) and low_r in (Rank.Eight, Rank.Seven):
                        return True
                    if high_r >= Rank.Five:
                        if high_r == low_r.next():
                            return True
                else:
                    if high_r >= Rank.Jack and low_r >= Rank.Ten:
                        return True
            else:
                if suited:
                    if high_r >= Rank.King and low_r >= Rank.Five:
                        return True

                    if high_r >= Rank.Ten and low_r >= Rank.Eight:
                        return True

                    if high_r >= Rank.Four:
                        if high_r == low_r.next():
                            return True

                    if Rank.Five <= high_r <= Rank.Seven:
                        if high_r == low_r.next().next():
                            return True

                else:
                    if high_r >= Rank.Jack and low_r >= Rank.Ten:
                        return True

        elif bet_timing == BetTiming.Early:
            if pair_r is not None and pair_r >= Rank.Six:
                return True
            if suited:
                if high_r == Rank.Ace:
                    return True
                if high_r == Rank.King and low_r >= Rank.Six:
                    return True
                if high_r >= Rank.Ten and low_r >= Rank.Seven:
                    return True
                if high_r >= Rank.Five:
                    if high_r == low_r.next():
                        return True
                if high_r >= Rank.Six:
                    if high_r == low_r.next().next():
                        return True
                if high_r >= Rank.Eight:
                    if high_r == low_r.next().next().next():
                        return True
            else:
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True

                if high_r == Rank.Ace and low_r >= Rank.Nine:
                    return True

        elif bet_timing == BetTiming.Middle:
            if pair_r is not None and pair_r >= Rank.Six:
                return True
            if suited:
                if high_r == Rank.Ace:
                    return True
                if high_r == Rank.King and low_r >= Rank.Five:
                    return True
                if high_r >= Rank.Ten and low_r >= Rank.Seven:
                    return True
                if high_r >= Rank.Five:
                    if high_r == low_r.next():
                        return True
                if high_r >= Rank.Seven:
                    if high_r == low_r.next().next():
                        return True
                if high_r >= Rank.Nine:
                    if high_r == low_r.next().next().next():
                        return True
                if high_r == Rank.Ten and low_r == Rank.Six:
                    return True
            else:
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True

                if high_r == Rank.Ace and low_r >= Rank.Eight:
                    return True

        elif bet_timing == BetTiming.Late:
            if pair_r is not None and pair_r >= Rank.Six:
                return True
            if suited:
                if high_r == Rank.Ace:
                    return True
                if high_r == Rank.King and low_r >= Rank.Eight:
                    return True
                if high_r >= Rank.Jack and low_r >= Rank.Nine:
                    return True
                if high_r >= Rank.Five:
                    if high_r == low_r.next():
                        return True
                if high_r >= Rank.Seven:
                    if high_r == low_r.next().next():
                        return True
            else:
                if high_r >= Rank.Queen and low_r >= Rank.Jack:
                    return True

                if high_r == Rank.Ace and low_r >= Rank.Ten:
                    return True

        elif bet_timing == BetTiming.Button:
            if pair_r is not None and pair_r >= Rank.Six:
                return True
            if suited:
                if high_r == Rank.Ace:
                    return True
                if high_r == Rank.King and low_r >= Rank.Four:
                    return True
                if high_r >= Rank.Jack and low_r >= Rank.Eight:
                    return True
                if high_r >= Rank.Five:
                    if high_r == low_r.next():
                        return True
                if high_r >= Rank.Seven:
                    if high_r == low_r.next().next():
                        return True
                if high_r == Rank.Eight and low_r == Rank.Five:
                    return True
            else:
                if high_r >= Rank.Queen and low_r >= Rank.Jack:
                    return True

                if high_r == Rank.Ace and low_r >= Rank.Nine:
                    return True

        return False

    def is_strong_for_first_raise(self, bet_timing: BetTiming, is_small_blind=False):
        high_r, low_r = self.high.rank, self.low.rank
        suited = self.high.same_suit(self.low)
        pair_r = self.is_pair()

        if bet_timing == BetTiming.Blind:
            if is_small_blind:
                if pair_r is not None and pair_r >= Rank.Seven:
                    return True
                if suited:
                    if high_r >= Rank.Jack and low_r >= Rank.Ten:
                        return True
                    if high_r in (Rank.Nine, Rank.Eight) and low_r in (Rank.Eight, Rank.Seven):
                        return True
                    if high_r >= Rank.Six:
                        if high_r == low_r.next():
                            return True
                    if high_r >= Rank.Seven:
                        if high_r == low_r.next().next():
                            return True
                    if high_r == Rank.Queen and low_r == Rank.Nine:
                        return True
                    if high_r == Rank.Ten and low_r == Rank.Seven:
                        return True
                else:
                    if high_r >= Rank.Ten and low_r >= Rank.Nine:
                        return True

                    if high_r >= Rank.Eight:
                        if high_r == low_r.next():
                            return True
            else:
                if pair_r is not None and pair_r >= Rank.Nine:
                    return True
                if suited:
                    if high_r == Rank.King and low_r >= Rank.Four:
                        return True
                    if high_r >= Rank.Nine and low_r >= Rank.Eight:
                        return True
                    if high_r >= Rank.Six:
                        if high_r == low_r.next():
                            return True
                    if high_r in (Rank.Six, Rank.Seven, Rank.Nine):
                        if high_r == low_r.next().next():
                            return True
                else:
                    if high_r >= Rank.Ten and low_r >= Rank.Nine:
                        return True

        elif bet_timing == BetTiming.Early:
            if pair_r is not None and pair_r >= Rank.Nine:
                return True
            if suited:
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True
                if high_r in (Rank.Eight, Rank.Nine):
                    if high_r == low_r.next():
                        return True
            else:
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True
        else:
            if pair_r is not None and pair_r >= Rank.Eight:
                return True
            if suited:
                if high_r >= Rank.Ten and low_r >= Rank.Nine:
                    return True
                if high_r >= Rank.Eight:
                    if high_r == low_r.next():
                        return True
                if Rank.Six <= high_r <= Rank.Nine:
                    if high_r == low_r.next().next():
                        return True
                if high_r in (Rank.Eight, Rank.Nine):
                    if high_r == low_r.next().next().next():
                        return True
            else:
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True

    def is_strong_for_second_raise(self, bet_timing: BetTiming, is_small_blind=False):
        high_r, low_r = self.high.rank, self.low.rank
        suited = self.high.same_suit(self.low)
        pair_r = self.is_pair()

        if bet_timing == BetTiming.Blind:
            if is_small_blind:
                if pair_r is not None and pair_r >= Rank.Eight:
                    return True

                if suited:
                    if high_r in (Rank.King, Rank.Ace):
                        if low_r >= Rank.Seven:
                            return True
                    if high_r == Rank.Queen:
                        if low_r >= Rank.Eight:
                            return True
                    if high_r == Rank.Jack:
                        if low_r >= Rank.Nine:
                            return True

                    if high_r in (Rank.Nine, Rank.Ten):
                        if high_r in (low_r.next(), low_r.next().next()):
                            return True
                else:
                    if high_r >= Rank.Queen and low_r >= Rank.Jack:
                        return True
            else:
                if pair_r is not None and pair_r >= Rank.Nine:
                    return True
                if suited:
                    if high_r >= Rank.Jack and low_r >= Rank.Ten:
                        return True
                else:
                    if high_r >= Rank.Queen and low_r >= Rank.Jack:
                        return True

        elif bet_timing == BetTiming.Early:
            if pair_r is not None and pair_r >= Rank.Eight:
                return True
            if suited:
                if high_r == Rank.Ace:
                    return True
                if high_r == Rank.King and low_r >= Rank.Six:
                    return True
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True
                if high_r >= Rank.Eight:
                    if high_r == low_r.next():
                        return True
            else:
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True

        elif BetTiming == BetTiming.Middle:
            if pair_r is not None and pair_r >= Rank.Seven:
                return True
            if suited:
                if high_r == Rank.Ace:
                    return True
                if high_r == Rank.King and low_r >= Rank.Five:
                    return True
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True
                if high_r == Rank.Nine:
                    if high_r == low_r.next():
                        return True
            else:
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True

        elif BetTiming == BetTiming.Late:
            if pair_r is not None and pair_r >= Rank.Seven:
                return True
            if suited:
                if high_r == Rank.Ace:
                    return True
                if high_r == Rank.King and low_r >= Rank.Four:
                    return True
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True
                if high_r == Rank.Nine:
                    if high_r == low_r.next():
                        return True
            else:
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True

        elif BetTiming == BetTiming.Button:
            if pair_r is not None and pair_r >= Rank.Seven:
                return True
            if suited:
                if high_r == Rank.Ace:
                    return True
                if high_r == Rank.King and low_r >= Rank.Four:
                    return True
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True
            else:
                if high_r >= Rank.Jack and low_r >= Rank.Ten:
                    return True

        return False


class CardsAnalyzer(PocketAnalyzer):
    def __init__(self, h1, h2, *board):
        super().__init__(h1, h2)
        assert len(board) in (3, 4, 5), f"Bad board: len({board}) is invalid"

        assert h1 not in board, f"Repeating {h1} in pocket and board"
        assert h2 not in board, f"Repeating {h2} in pocket and board"
        assert len(set(board)) == len(board), f"Repeating cards in board {board}"

        self.board = board

    def top_board_rank(self):
        return max(c.rank for c in self.board)

    def all_cards(self):
        return [self.high, self.low] + list(self.board)

    def is_2_overcards(self):
        """
        2-overcards - Both hole cards are higher than anything on board.
        """
        tbr = self.top_board_rank()
        if self.high.rank > tbr and self.low.rank > tbr:
            # But don't set this if we've also set...
            return not any([
                self.is_pair(),
                self.is_top_2_pair(),
                self.is_trips_with_hole_card(),
                self.is_full_house_with_hole_card(),
                self.is_4_of_a_kind_with_hole_card(),
            ])

        return False

    def find_pair_only_in_hole(self):
        """
        We have a pair using both hole cards.
        """
        return super(CardsAnalyzer, self).is_pair()

    def find_pairs_with_hole(self):
        """
        Return all pairs using a hole card.
        """
        pair_rank = self.find_pair_only_in_hole()
        if pair_rank:
            return [pair_rank]

        pairs = []
        board_ranks = [b.rank for b in self.board]
        for hole in [self.low.rank, self.high.rank]:
            if hole in board_ranks:
                pairs.append(hole)

        return pairs

    def is_pair(self):
        """
        We have a pair using a hole card. Set this even when we set
        other pair-related augmentations.
        """
        return bool(self.find_pairs_with_hole())

    def find_low_pair(self):
        """
        We have a pair using a hole card.
        """
        pairs = self.find_pairs_with_hole()
        if pairs:
            return pairs[0]

    def find_high_pair(self):
        """
        We have a pair using a hole card.
        """
        pairs = self.find_pairs_with_hole()
        if pairs:
            return pairs[-1]

    def is_pair_with_overcard(self):
        """
        We have a pair using a hole card, and our other
        hole card is as high as any board card.
        So if we pair up the overcard, we'll have a strong 2 pair.
        Example: we have a-4 in the hole, and the board is 4-k-7.
        """
        pair_rank = self.find_low_pair()
        # strict pair, using a single pocket card
        if pair_rank and self.find_pair_only_in_hole() is None:
            if pair_rank == self.high.rank:
                other_pocket_rank = self.low.rank
            else:
                assert pair_rank == self.low.rank
                other_pocket_rank = self.high.rank

            if other_pocket_rank >= self.top_board_rank():
                # But don't set this if we've also set...
                return not any([
                    self.is_top_pair(),
                    self.is_top_2_pair(),
                    self.is_trips_with_hole_card(),
                    self.is_full_house_with_hole_card(),
                    self.is_4_of_a_kind_with_hole_card(),
                ])

        return False

    def is_high_pair(self):
        """
        We have a high pair using a hole card.
        Not necessarily top pair.
        """
        pair_rank = self.find_high_pair()
        if pair_rank is None:
            return False

        return Rank.Ten <= pair_rank <= Rank.Ace

    def is_top_pair(self):
        """
        We have a pair using a hole card,
        and it's as high as any pair possible
        given what's on board.
        We have a strong pair.
        """
        pair_rank = self.find_high_pair()
        if pair_rank is None:
            return False

        if pair_rank >= self.top_board_rank():
            # But don't set this if we've also set...
            return not any([
                self.is_top_2_pair(),
                self.is_trips_with_hole_card(),
                self.is_full_house_with_hole_card(),
                self.is_4_of_a_kind_with_hole_card(),
            ])

    def find_pair_on_board(self):
        """
        We have a pair in the board cards alone
        """
        for i, b1 in enumerate(self.board):
            for b2 in self.board[i + 1:]:
                if b1.rank == b2.rank:
                    return b1.rank
        return None

    def find_2_pairs(self):
        """
        At least one pair should use a hole card.
        """
        pair_rank_high = self.find_high_pair()
        if pair_rank_high is None:
            return None

        pair_rank_low = self.find_low_pair()
        assert pair_rank_low is not None, \
            "Should exist and be at least the same as high"

        if pair_rank_low != pair_rank_high:
            return pair_rank_high, pair_rank_low

        # try to find another with the board cards only
        board_pair_rank = self.find_pair_on_board()
        if board_pair_rank is None:
            # just one pair
            return None

        if board_pair_rank == pair_rank_high:
            # it is not a pair, but rather triple (at least)
            return None

        return pair_rank_high, board_pair_rank

    def is_2_pair(self):
        """
        2-pair - We have 2 pair, and at least 1 pair uses a hole card.
        """
        pairs = self.find_2_pairs()
        if pairs is None:
            return False

        hole_high, hole_low_or_board = pairs
        assert hole_high != hole_low_or_board

        return not any([
            self.is_top_2_pair(),
            self.is_trips_with_hole_card(),
            self.is_full_house_with_hole_card(),
            self.is_4_of_a_kind_with_hole_card(),
        ])

    def is_top_2_pair(self):
        """
        We have 2 pair, and the higher pair uses a hole card.
        It's as high as any 2 pair possible given what's on board.
        """
        pairs = self.find_2_pairs()
        if pairs is None:
            return False

        hole_high, hole_low_or_board = pairs
        assert hole_high != hole_low_or_board
        if hole_high >= self.top_board_rank():
            # But don't set this if we've also set...
            return not any([
                self.is_trips_with_hole_card(),
                self.is_full_house_with_hole_card(),
                self.is_4_of_a_kind_with_hole_card(),
            ])

        return False

    def is_trips_with_hole_card(self):
        """
        3-of-a-kind with one of them in the hole.
        Distinct from (much stronger than)
        3 of a kind on board, which means
        everybody has 3 of a kind.
        """
        for pair_rank in self.find_pairs_with_hole():
            num_of_same_rank = sum(
                1 for c in self.all_cards() if c.rank == pair_rank)
            if num_of_same_rank == 3:
                # But don't set this if we've also set...
                return not any([
                    self.is_full_house_with_hole_card(),
                    self.is_4_of_a_kind_with_hole_card(),
                ])

        return False

    # TODO - straights are not tied to hole cards. They should be.

    def is_inside_straight(self):
        """
        4 cards that are be part of a straight. Only one
        way to make the straight, e.g. 7-8-9-jack v. 7-8-9-10.
        """
        sorted_all_cards = [c.rank for c in Card.sort_by_rank(self.all_cards())]
        if Rank.Ace in sorted_all_cards:
            sorted_all_cards.insert(0, Rank.Ace)
        for i, first_in_straight in enumerate(sorted_all_cards):
            max_straight_rank = first_in_straight.covered_straight_max_rank()
            # print(first_in_straight, max_straight_rank)

            covered_with_c1_as_lowest_in_straight = [first_in_straight]
            for r2 in sorted_all_cards[i + 1:]:
                base = covered_with_c1_as_lowest_in_straight[-1]
                if base == Rank.Ace:
                    # special case for the starting Ace
                    if r2 <= max_straight_rank and r2 != Rank.Ace:
                        covered_with_c1_as_lowest_in_straight.append(r2)
                elif base < r2 <= max_straight_rank:
                    covered_with_c1_as_lowest_in_straight.append(r2)

            # print(covered_with_c1_as_lowest_in_straight)
            if len(covered_with_c1_as_lowest_in_straight) == 4:
                # But don't set this if we've also set...
                return not self.is_4_straight()

        return False

    def is_bobtail_straight(self):
        """
        4 cards in sequence that can improve at either end,
        so no aces in the sequence.
        For example, 2-3-4-5 is good because
        an ace or a 6 makes the straight,
        but not ace-2-3-4 because only a 5 makes the straight,
        and not j-q-k-ace because only a 10 makes it.
        """
        sorted_all_cards = [c.rank for c in Card.sort_by_rank(self.all_cards())]
        for i, first_in_straight in enumerate(sorted_all_cards):
            seq = [first_in_straight]

            for r2 in sorted_all_cards[i + 1:]:
                if r2 == seq[-1]:
                    # skip the pairs
                    continue

                if r2 == seq[-1].next():
                    seq.append(r2)
                else:
                    break

            if len(seq) == 4 and Rank.Ace not in seq:
                return True

        return False

    def is_double_inside_straight(self):
        """
        3 cards in sequence and a one-off at either end,
        e.g. 2-4-5-6-8, where a 3 or a 7 makes the straight.
        Should be close to a bobtail in value.
        Ace at either end is okay here.
        """
        sorted_all_cards = [c.rank for c in Card.sort_by_rank(self.all_cards())]
        for i, first_in_straight in enumerate(sorted_all_cards):
            seq = [first_in_straight]

            for r2 in sorted_all_cards[i + 1:]:
                if r2 == seq[-1]:
                    # skip the pairs
                    continue

                if len(seq) in [1, 4]:
                    next_rank = seq[-1].next().next()
                else:
                    next_rank = seq[-1].next()

                if r2 == next_rank:
                    seq.append(r2)
                else:
                    break

            if len(seq) == 5 and Rank.Ace not in seq[1:4]:
                return True

        return False

    def is_4_straight(self):
        """
        One card is missing to make the hole straight
        """
        return self.is_bobtail_straight() or self.is_double_inside_straight()

    def is_straight(self):
        """5 in a row."""
        sorted_all_cards = [c.rank for c in Card.sort_by_rank(self.all_cards())]
        if Rank.Ace in sorted_all_cards:
            sorted_all_cards.insert(0, Rank.Ace)
        for i, first_in_straight in enumerate(sorted_all_cards):
            seq = [first_in_straight]

            for r2 in sorted_all_cards[i + 1:]:
                if r2 == seq[-1]:
                    # skip the pairs
                    continue

                if r2 == seq[-1].next():
                    seq.append(r2)
                else:
                    break

            if len(seq) == 5 and Rank.Ace not in seq[1:4]:
                return True

        return False

    def is_n_flush_with_hole_card(self, n):
        """N cards of the same suit."""
        pocket = [self.low, self.high]
        all_cards = self.all_cards()
        for first_in_flush in pocket:
            seq = [first_in_flush]

            for c2 in all_cards:
                if c2 == first_in_flush:
                    continue

                if c2.suit == seq[-1].suit:
                    seq.append(c2)

            if len(seq) == n:
                return True

        return False

    def is_3_flush_with_hole_card(self):
        """3 cards in the same suit."""
        return self.is_n_flush_with_hole_card(3)

    def is_4_flush_with_hole_card(self):
        """4 cards in the same suit."""
        return self.is_n_flush_with_hole_card(4)

    def is_flush_with_hole_card(self):
        """5 cards in the same suit."""
        return self.is_n_flush_with_hole_card(5)

    def is_full_house_with_pair_hole_cards(self):
        pairs = self.find_pairs_with_hole()
        if not pairs:
            return False

        all_cards = [c.rank for c in self.all_cards()]
        for pair_rank in pairs:
            for r1 in all_cards:
                if r1 == pair_rank:
                    # skip the pocket pair's rank
                    continue

                same_rank = sum(1 for r2 in all_cards if r2 == r1)
                if same_rank == 3:
                    # found triple with the rank other than pair's one

                    # But don't set this if we've also set...
                    return not self.is_4_of_a_kind_with_hole_card()

        return False

    def is_full_house_with_triple_hole_cards(self):
        pairs = self.find_pairs_with_hole()
        if not pairs:
            return False

        all_cards = [c.rank for c in self.all_cards()]
        for pair_rank in pairs:
            same_rank = sum(1 for r2 in all_cards if r2 == pair_rank)
            if same_rank != 3:
                # if the pair cannot complete to triple,
                # or it is 4-of-a-kind, skip it
                continue

            for r1 in all_cards:
                if r1 == pair_rank:
                    continue

                same_rank = sum(1 for r2 in all_cards if r2 == r1)
                if same_rank == 2:
                    # found pair with the rank other than triple's one

                    # But don't set this if we've also set...
                    return not self.is_4_of_a_kind_with_hole_card()

        return False

    def is_full_house_with_hole_card(self):
        """3 of a kind and a pair."""
        return self.is_full_house_with_pair_hole_cards() or \
               self.is_full_house_with_triple_hole_cards()

    def is_4_of_a_kind_with_hole_card(self):
        """
        4-of-a-kind with one of them in the hole.
        Distinct from (much stronger than)
        4 of a kind on board, which means
        everybody has 4 of a kind.
        """
        pairs = self.find_pairs_with_hole()
        if not pairs:
            return False

        all_cards = [c.rank for c in self.all_cards()]
        for pair_rank in pairs:
            same_rank = sum(1 for r2 in all_cards if r2 == pair_rank)
            if same_rank == 4:
                return True

        return False

    # board elaborations

    def is_blank_on_board(self):
        """
        A blank is a board card that doesn't seem to help anyone,
        i.e. it doesn't make a pair or a piece of a straight or a flush.
        Significant on the turn and the river,
        when the board cards show up one at a time.

        Example:
            The flop is 3h 9d qs.
            The turn is 4h. The 4h is a blank.
            It probably didn't improve anyone.
        """
        # Set this only if we haven't set anything else for the board.
        return not any([
            self.is_pair_on_board(),
            self.is_2_pair_on_board(),
            self.is_trips_on_board(),
            self.is_3_straight_on_board(),
            self.is_4_straight_on_board(),
            self.is_straight_on_board(),
            self.is_3_flush_on_board(),
            self.is_4_flush_on_board(),
            self.is_flush_on_board(),
            self.is_full_house_on_board(),
            self.is_4_of_a_kind_on_board()
        ])

    def is_pair_on_board(self):
        """2 of a kind on board"""
        board_pair_rank = self.find_pair_on_board()
        if board_pair_rank is None:
            return None

        return not any([
            self.is_2_pair_on_board(),
            self.is_trips_on_board(),
            self.is_full_house_on_board(),
            self.is_4_of_a_kind_on_board(),
        ])

    def is_2_pair_on_board(self):
        """2 pairs on board."""
        board_pair_rank = self.find_pair_on_board()
        if board_pair_rank is None:
            return None

        board_cards = [c.rank for c in self.board]
        for r1 in board_cards:
            if r1 == board_pair_rank:
                # skip the already found pair's rank
                continue

            same_rank = sum(1 for r2 in board_cards if r2 == r1)
            if same_rank == 2:
                # But don't set this if we've also set...
                return not any([
                    self.is_trips_on_board(),
                    self.is_full_house_on_board(),
                    self.is_4_of_a_kind_on_board()
                ])

        return False

    def is_trips_on_board(self):
        """3 of a kind on board."""
        board_cards = [c.rank for c in self.board]
        for r1 in board_cards:
            same_rank = sum(1 for r2 in board_cards if r2 == r1)
            if same_rank == 3:
                # But don't set this if we've also set...
                return not any([
                    self.is_full_house_on_board(),
                    self.is_4_of_a_kind_on_board()
                ])
        return False

    def is_3_straight_on_board(self):
        """
        3 cards on board that could be part of a straight.
        """
        sorted_board_cards = [c.rank for c in Card.sort_by_rank(self.board)]
        if Rank.Ace in sorted_board_cards:
            sorted_board_cards.insert(0, Rank.Ace)
        for i, first_in_straight in enumerate(sorted_board_cards):
            max_straight_rank = first_in_straight.covered_straight_max_rank()

            seq = [first_in_straight]
            for r2 in sorted_board_cards[i + 1:]:
                base = seq[-1]
                if base == Rank.Ace:
                    # special case for the starting Ace
                    if r2 <= max_straight_rank and r2 != Rank.Ace:
                        seq.append(r2)
                elif base < r2 <= max_straight_rank:
                    seq.append(r2)

            if len(seq) == 3:
                # Middle rank can't be ace
                if seq[1] != Rank.Ace:
                    # But don't set this if we've also set...
                    return not any([
                        self.is_4_straight_on_board(),
                        self.is_straight_on_board()
                    ])

        return False

    def is_4_straight_on_board(self):
        """
        4 cards on board that could be part of a straight.
        """
        sorted_board_cards = [c.rank for c in Card.sort_by_rank(self.board)]
        if Rank.Ace in sorted_board_cards:
            sorted_board_cards.insert(0, Rank.Ace)
        for i, first_in_straight in enumerate(sorted_board_cards):
            max_straight_rank = first_in_straight.covered_straight_max_rank()

            seq = [first_in_straight]
            for r2 in sorted_board_cards[i + 1:]:
                base = seq[-1]
                if base == Rank.Ace:
                    # special case for the starting Ace
                    if r2 <= max_straight_rank and r2 != Rank.Ace:
                        seq.append(r2)
                elif base < r2 <= max_straight_rank:
                    seq.append(r2)

            if len(seq) == 4:
                # Middle ranks can't be ace
                if Rank.Ace not in seq[1:3]:
                    # But don't set this if we've also set...
                    return not any([
                        self.is_straight_on_board()
                    ])

        return False

    def is_straight_on_board(self):
        """5 in a row on board."""
        sorted_board_cards = [c.rank for c in Card.sort_by_rank(self.board)]
        if Rank.Ace in sorted_board_cards:
            sorted_board_cards.insert(0, Rank.Ace)
        for first_in_straight in sorted_board_cards:

            seq = [first_in_straight]
            for r2 in sorted_board_cards:
                if r2 == seq[-1].next():
                    seq.append(r2)

            if len(seq) == 5:
                # Middle ranks can't be ace
                if Rank.Ace not in seq[1:4]:
                    return True

        return False

    def is_n_flush_on_board(self, n):
        """N cards of the same suit."""
        for first_in_flush in self.board:
            seq = [first_in_flush]

            for c2 in self.board:
                if c2 == first_in_flush:
                    continue

                if c2.suit == seq[-1].suit:
                    seq.append(c2)

            if len(seq) == n:
                return True

        return False

    def is_3_flush_on_board(self):
        """3 cards of the same suit on board"""
        return self.is_n_flush_on_board(3)

    def is_4_flush_on_board(self):
        """4 cards of the same suit on board"""
        return self.is_n_flush_on_board(4)

    def is_flush_on_board(self):
        """5 cards of the same suit on board"""
        return self.is_n_flush_on_board(5)

    def is_full_house_on_board(self):
        """A triple and a pair on board"""

        board_cards = [c.rank for c in self.board]
        for triple_rank in board_cards:
            same_rank = sum(1 for r2 in board_cards if r2 == triple_rank)
            if same_rank == 3:
                for pair_rank in board_cards:
                    if pair_rank == triple_rank:
                        # skip the rank matching the triple's rank
                        continue

                    same_rank = sum(1 for r2 in board_cards if r2 == pair_rank)
                    if same_rank == 2:
                        return not self.is_4_of_a_kind_on_board()

        return False

    def is_4_of_a_kind_on_board(self):
        """4 of a kind on board."""
        board_cards = [c.rank for c in self.board]
        for r1 in board_cards:
            same_rank = sum(1 for r2 in board_cards if r2 == r1)
            if same_rank == 4:
                return True
        return False

    def flop_strength(self):
        """
        Elaborate flop-strength based on analysis.
        """
        assert len(self.all_cards()) == 5
        if self.is_trips_with_hole_card():
            return 1

        # At this stage, 4 of a kind must use hole card.
        if self.is_4_of_a_kind_with_hole_card():
            return 1

        # At this stage straight must use hole cards.
        if self.is_straight():
            return 1

        # At this stage flush must use hole cards.
        if self.is_flush_with_hole_card():
            return 1

        # At this stage 4-flush must use hole cards.
        if self.is_4_straight() and self.is_4_flush_with_hole_card():
            # 4-flush-and-4-straight
            return 1

        # At this stage, full house must use hole cards.
        if self.is_full_house_with_hole_card():
            return 1

        if self.is_top_2_pair():
            return 2

        if self.is_top_pair():
            return 3

        # TODO: fix the rule in the flop.soar
        if self.is_2_pair():
            return 3

        # --------------------------------------------------------------------
        # Semibluff - as per Sklansky and Malmuth, p. 33. Hands where we may
        # drive everyone out, and, if we don't, we have a good chance to improve.
        # --------------------------------------------------------------------

        if self.is_inside_straight():
            if self.is_pair_with_overcard() or self.is_2_overcards():
                return 3.5

        if self.is_4_straight():
            if self.is_pair() or self.is_2_overcards():
                return 3.5

        if self.is_4_flush_with_hole_card():
            if self.is_pair() or self.is_2_overcards():
                return 3.5

        if self.is_3_flush_with_hole_card():
            if self.is_pair_with_overcard() or self.is_2_overcards():
                return 3.5

        # At this stage, 4-straight must use hole cards.
        if self.is_4_straight():
            return 4

        # At this stage 4-flush must use hole cards.
        if self.is_4_flush_with_hole_card():
            return 4

        if self.is_pair_with_overcard():
            return 5

        if self.is_2_overcards():
            return 6

        if self.find_pair_only_in_hole():
            return 6

        if self.is_pair():
            return 7

        # nothing special
        return 100

    def is_board_very_danger(self):
        # Any obvious dangers?
        return any([
            self.is_4_flush_on_board(),
            self.is_flush_on_board(),
            self.is_full_house_on_board(),
            self.is_4_of_a_kind_on_board()
        ])

    def turn_strength(self, pot_odds):
        """
        Elaborate turn-strength based on analysis.
        """
        assert len(self.all_cards()) == 6

        if self.is_trips_with_hole_card():
            # Any obvious dangers?
            if not any([
                self.is_4_straight_on_board(),
                self.is_straight_on_board(),
                self.is_board_very_danger(),
            ]):
                return 1

        if self.is_straight():
            # Any obvious dangers?
            if not any([
                self.is_straight_on_board(),
                self.is_board_very_danger(),
            ]):
                return 1

        if self.is_flush_with_hole_card():
            # Any obvious dangers?
            if not any([
                self.is_2_pair_on_board(),
                self.is_board_very_danger(),
            ]):
                return 1

        # 4-flush-and-4-straight
        if self.is_4_straight() \
                and self.is_4_flush_with_hole_card() \
                and pot_odds >= 3:
            # Any obvious dangers?
            if not any([
                self.is_2_pair_on_board(),
                self.is_4_straight_on_board(),
                self.is_straight_on_board(),
                self.is_board_very_danger(),
            ]):
                return 1

        if self.is_full_house_with_hole_card():
            # Any obvious dangers?
            if not any([
                self.is_full_house_on_board(),
                self.is_4_of_a_kind_on_board()
            ]):
                return 1

        if self.is_4_of_a_kind_with_hole_card():
            return 1

        if self.is_top_2_pair():
            # Any obvious dangers?
            if not any([
                self.is_trips_on_board(),
                self.is_4_straight_on_board(),
                self.is_straight_on_board(),
                self.is_board_very_danger(),
            ]):
                return 2

        if self.is_trips_with_hole_card():
            return 2

        # --------------------------------------------------------------------
        # Semibluff - as per Sklansky and Malmuth, p. 35. Hands where we may
        # drive everyone out, and, if we don't, we have a good chance to improve.
        # --------------------------------------------------------------------
        if self.is_pair():
            if self.is_4_straight():
                # semibluff*straight
                return 2.5
            if self.is_4_flush_with_hole_card():
                # semibluff*flush
                return 2.5

        if self.is_top_pair():
            # Any obvious dangers?
            if not any([
                self.is_pair_on_board(),
                self.is_2_pair_on_board(),
                self.is_trips_on_board(),
                self.is_4_straight_on_board(),
                self.is_straight_on_board(),
                self.is_board_very_danger(),
            ]):
                return 3

        if self.is_2_pair():
            # Any obvious dangers?
            if not any([
                self.is_trips_on_board(),
                self.is_4_straight_on_board(),
                self.is_straight_on_board(),
                self.is_board_very_danger(),
            ]):
                return 3

        if self.is_4_straight() and pot_odds >= 5:
            # Any obvious dangers?
            if not any([
                self.is_4_straight_on_board(),
                self.is_straight_on_board(),
                self.is_board_very_danger(),
            ]):
                return 3

        if self.is_flush_with_hole_card():
            return 3

        if self.is_4_flush_with_hole_card() and pot_odds >= 4:
            # Any obvious dangers?
            if not any([
                self.is_2_pair_on_board(),
                self.is_board_very_danger(),
            ]):
                return 3

        if self.is_4_flush_with_hole_card() \
                and self.is_4_straight() \
                and pot_odds >= 3:
            return 3

        if self.is_full_house_with_hole_card():
            return 3

        if self.is_pair_with_overcard() \
                and pot_odds >= 5:
            # Any obvious dangers?
            if not any([
                self.is_pair_on_board(),
                self.is_2_pair_on_board(),
                self.is_trips_on_board(),
                self.is_4_straight_on_board(),
                self.is_straight_on_board(),
                self.is_board_very_danger(),
            ]):
                return 4

        if self.is_straight():
            return 4

        if self.is_top_2_pair() and pot_odds >= 3:
            return 5

        if self.is_top_pair() and pot_odds >= 5:
            return 6

        if self.is_2_pair() and pot_odds >= 3:
            return 6

        if self.is_4_straight() and pot_odds >= 5:
            return 6

        if self.is_4_flush_with_hole_card() and pot_odds >= 4:
            return 6

        if self.is_pair_with_overcard() and pot_odds >= 5:
            return 7

        if self.is_high_pair() and pot_odds >= 5:
            return 7

        # nothing special
        return 100
