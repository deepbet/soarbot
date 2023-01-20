import pytest

from .analyze import PocketAnalyzer, CardsAnalyzer
from .cards import Suit, Rank, Card


def generate_all_cards():
    for s in Suit:
        for r in Rank:
            yield Card(r, s)


class TestCards:
    def test_parse(self):
        for card in generate_all_cards():
            print(card, card.rank.next(), card.rank.prev())
            assert card == Card.parse(f'{card}')

    def test_max_rank_for_straight(self):
        for r in Rank:
            if r == Rank.Jack:
                break
            next_4 = r.next().next().next().next()
            assert r.covered_straight_max_rank() == next_4

        for r in [Rank.Jack, Rank.Queen, Rank.King]:
            assert r.covered_straight_max_rank() == Rank.Ace

        assert Rank.Ace.covered_straight_max_rank() == Rank.Five


class TestPockets:
    def test_preflop_strength(self):
        for c1 in generate_all_cards():
            for c2 in generate_all_cards():
                if c1 != c2:
                    pa = PocketAnalyzer(c1, c2)
                    strength = pa.preflop_strength()
                    assert strength > 0
                    print(c1, c2, strength)

                    if c1.rank == c2.rank:
                        assert pa.is_pair()
                    else:
                        assert not pa.is_pair()
                else:
                    try:
                        PocketAnalyzer(c1, c2)
                    except AssertionError:
                        continue
                    else:
                        raise ValueError("The same cards are accepted as pocket")


def analyzer_from_strs(*cards):
    return CardsAnalyzer(*list(map(Card.parse, cards)))


class TestFullCardsSet:
    def test_invalid_round_init(self):
        pocket = ['Jd', '7h']
        with pytest.raises(AssertionError):
            analyzer_from_strs(*pocket)

        with pytest.raises(AssertionError):
            analyzer_from_strs(*pocket, 'Kd')

        with pytest.raises(AssertionError):
            analyzer_from_strs(*pocket, 'Kd', 'Ts')

    def test_repeating_cards_init(self):
        pocket = ['Jd', '7h']
        analyzer_from_strs(*pocket, 'Kd', 'Ts', '6s')

        with pytest.raises(AssertionError):
            analyzer_from_strs(*pocket, 'Kd', 'Ts', '7h')

        with pytest.raises(AssertionError):
            analyzer_from_strs(*pocket, 'Kd', 'Ts', '6s', 'Jd')

    def test_repeating_board_cards_init(self):
        pocket = ['Jd', '7h']
        with pytest.raises(AssertionError):
            analyzer_from_strs(*pocket, 'Kd', 'Ts', '6s', 'Kd')

    def test_all_cards(self):
        pocket = ['Jd', '7h']
        ca = analyzer_from_strs(*pocket, 'Kd', 'Ts', '6s')

        assert ca.top_board_rank() == Rank.King
        assert ca.all_cards() == list(map(Card.parse, ['Jd', '7h', 'Kd', 'Ts', '6s']))


class TestWithHoleCombinations:
    def test_overcards(self):
        ca = analyzer_from_strs('Ts', '9d', '8h', '5c', '8c')
        assert ca.is_2_overcards()

    def test_not_overcards(self):
        ca = analyzer_from_strs('Ts', '9d', '8h', 'Jc', '8c')
        assert not ca.is_2_overcards()

    def test_not_overcards_as_pair_found(self):
        ca = analyzer_from_strs('Ts', '9d', '8h', 'Jc', '9c')
        assert not ca.is_2_overcards()

    def test_all_pocket_pairs(self):
        ca = analyzer_from_strs('Ts', '9d', '8h', 'Jc', '9c')
        assert ca.find_pairs_with_hole() == [Rank.Nine]
        assert ca.find_low_pair() == Rank.Nine
        assert ca.find_high_pair() == Rank.Nine

        ca = analyzer_from_strs('Ts', '9d', '8h', 'Td', '9c')
        assert ca.find_pairs_with_hole() == [Rank.Nine, Rank.Ten]
        assert ca.find_low_pair() == Rank.Nine
        assert ca.find_high_pair() == Rank.Ten

    def test_pair_with_overcard(self):
        ca = analyzer_from_strs('As', '4d', '4h', 'Kc', '7c')
        assert not ca.is_2_overcards()
        assert ca.is_pair_with_overcard()
        assert not ca.is_high_pair()

    def test_not_pair_with_overcard_as_another_pair_found(self):
        ca = analyzer_from_strs('As', '4d', '4h', 'Kc', 'Ac')
        assert not ca.is_2_overcards()
        assert not ca.is_pair_with_overcard()

    def test_high_pair(self):
        ca = analyzer_from_strs('As', '4d', '3h', 'Kc', 'Ac')
        assert ca.is_high_pair()
        assert ca.is_top_pair()

    def test_two_pairs(self):
        ca = analyzer_from_strs('Ks', '4d', '4h', 'Kc', 'Ac')
        assert ca.is_2_pair()

    def test_two_pairs_with_top_hole(self):
        ca = analyzer_from_strs('As', '4d', '4h', 'Kc', 'Ac')
        assert ca.is_top_2_pair()

    def test_trips(self):
        ca = analyzer_from_strs('As', '4d', '4h', 'Kc', '4c')
        assert ca.is_trips_with_hole_card()

    def test_4_cards_forming_straight(self):
        ca = analyzer_from_strs('7s', '8d', '9h', 'Kc', 'Jc')
        assert ca.is_inside_straight()

        ca = analyzer_from_strs('3s', '5d', 'Ah', 'Kc', '4c')
        assert ca.is_inside_straight()

    def test_4_cards_bobtail_straight(self):
        ca = analyzer_from_strs('Jc', '2s', '3d', '5c', '4h')
        assert not ca.is_inside_straight()
        assert ca.is_bobtail_straight()
        assert ca.is_4_straight()

    def test_4_cards_not_bobtail_straight_because_of_ace(self):
        ca = analyzer_from_strs('Jc', '2s', '3d', '5c', 'Ah')
        assert ca.is_inside_straight()
        assert not ca.is_bobtail_straight()

    def test_4_cards_bobtail_straight_with_board(self):
        ca = analyzer_from_strs('Jc', 'Th', '2s', '3d', '5c', '4h')
        assert not ca.is_inside_straight()
        assert ca.is_bobtail_straight()
        assert ca.is_4_straight_on_board()

    def test_double_inside_straight(self):
        ca = analyzer_from_strs('2c', '8h', '5s', '6d', 'Qc', '4h')
        assert not ca.is_inside_straight()
        assert not ca.is_bobtail_straight()
        assert ca.is_double_inside_straight()
        assert ca.is_4_straight()

    def test_straight_with_board(self):
        ca = analyzer_from_strs('Jc', 'Th', '2s', '3d', '5c', '4h', 'Ad')
        assert not ca.is_inside_straight()
        assert ca.is_straight()
        assert ca.is_straight_on_board()

    def test_3_flush_with_hole(self):
        ca = analyzer_from_strs('Jc', 'Th', '2c', '3d', '5c', '4h', 'Ad')
        assert ca.is_3_flush_with_hole_card()
        assert not ca.is_3_flush_on_board()

    def test_4_flush_with_hole(self):
        ca = analyzer_from_strs('Jc', 'Th', '2c', '3d', '5c', '4h', 'Ac')
        assert ca.is_4_flush_with_hole_card()
        assert not ca.is_4_flush_on_board()

    def test_flush_with_hole(self):
        ca = analyzer_from_strs('Jc', 'Th', '2c', 'Qc', '5c', '4h', 'Ac')
        assert ca.is_flush_with_hole_card()
        assert not ca.is_flush_on_board()

    def test_full_house_with_pair_hole(self):
        ca = analyzer_from_strs('As', '4d', 'Qh', 'Ac', '8s', 'Qc', 'Qd')
        assert not super(CardsAnalyzer, ca).is_pair()
        assert ca.is_pair()
        assert not ca.is_trips_with_hole_card()
        assert ca.is_full_house_with_pair_hole_cards()
        assert ca.is_full_house_with_hole_card()

    def test_full_house_with_triple_hole(self):
        ca = analyzer_from_strs('As', '4d', '4h', 'Kc', '4c', 'Qc', 'Qd')
        assert not super(CardsAnalyzer, ca).is_pair()
        assert ca.is_pair()
        assert not ca.is_trips_with_hole_card()
        assert ca.is_full_house_with_triple_hole_cards()
        assert ca.is_full_house_with_hole_card()

    def test_full_house_with_both_hole_cards(self):
        ca = analyzer_from_strs('As', '4d', '4h', 'Kc', '4c', 'Qc', 'Ad')
        assert not super(CardsAnalyzer, ca).is_pair()
        assert ca.is_pair()
        assert not ca.is_trips_with_hole_card()
        assert ca.is_full_house_with_pair_hole_cards()
        assert ca.is_full_house_with_triple_hole_cards()
        assert ca.is_full_house_with_hole_card()

    def test_4_kind_with_hole(self):
        ca = analyzer_from_strs('As', '4d', '4h', 'Kc', '4c', 'Qc', '4s')
        assert not super(CardsAnalyzer, ca).is_pair()
        assert ca.is_pair()
        assert not ca.is_trips_with_hole_card()
        assert not ca.is_full_house_with_hole_card()
        assert ca.is_4_of_a_kind_with_hole_card()

    def test_4_kind_with_both_holes(self):
        ca = analyzer_from_strs('4s', '4d', '4h', 'Kc', '4c', 'Qc', 'Ad')
        assert not ca.is_trips_with_hole_card()
        assert not ca.is_full_house_with_hole_card()
        assert ca.is_4_of_a_kind_with_hole_card()


class TestOnlyBoardCombinations:
    def test_blank(self):
        ca = analyzer_from_strs('Jc', 'Th', '3h', '9d', 'Qs')
        assert ca.is_blank_on_board()

        ca = analyzer_from_strs('Jc', 'Th', '3h', '9d', 'Qs', '4h')
        assert ca.is_blank_on_board()

    def test_pair(self):
        ca = analyzer_from_strs('Jc', 'Th', '3h', '9d', 'Qs', '3d')
        assert ca.is_pair_on_board()

    def test_pair_with_hole_only(self):
        ca = analyzer_from_strs('Ts', '9d', '8h', 'Jc', '9c')
        assert ca.find_pairs_with_hole()
        assert not ca.is_pair_on_board()

    def test_2_pairs(self):
        ca = analyzer_from_strs('Jc', 'Th', '3h', '9d', 'Qs', '3d', 'Qh')
        assert not ca.is_pair_on_board()
        assert ca.is_2_pair_on_board()

    def test_trips(self):
        ca = analyzer_from_strs('Jc', 'Th', '3h', '9d', '3s', '3d', 'Qh')
        assert not ca.is_pair_on_board()
        assert ca.is_trips_on_board()

    def test_3_straight(self):
        ca = analyzer_from_strs('Jd', 'Jh', '3s', '5d', 'Ac')
        assert ca.is_3_straight_on_board()

    def test_4_straight(self):
        ca = analyzer_from_strs('2d', '2h', '7s', '8d', '9h', 'Kc', 'Jc')
        assert ca.is_4_straight_on_board()

    def test_4_straight_with_ace(self):
        ca = analyzer_from_strs('2d', '2h', '5s', '3d', '4h', 'Kc', 'Ac')
        assert not ca.is_3_straight_on_board()
        assert ca.is_4_straight_on_board()

    def test_not_4_straight_with_king(self):
        ca = analyzer_from_strs('2d', '2h', '7s', '3d', '4h', 'Kc', 'Ac')
        assert ca.is_3_straight_on_board()
        assert not ca.is_4_straight_on_board()

    def test_straight(self):
        ca = analyzer_from_strs('2d', '2h', '7s', '8d', '9h', 'Tc', 'Jc')
        assert ca.is_straight_on_board()

    def test_3_flush(self):
        ca = analyzer_from_strs('2d', '2h', 'Qs', '4d', '5s', 'Ts')
        assert ca.is_3_flush_on_board()
        assert not ca.is_4_flush_on_board()
        assert not ca.is_flush_on_board()

    def test_4_flush(self):
        ca = analyzer_from_strs('2d', '2h', 'Qs', '4d', '5s', 'Ts', 'As')
        assert not ca.is_3_flush_on_board()
        assert ca.is_4_flush_on_board()
        assert not ca.is_flush_on_board()

    def test_flush(self):
        ca = analyzer_from_strs('2d', '2h', 'Qs', '4s', '5s', 'Ts', 'As')
        assert not ca.is_3_flush_on_board()
        assert not ca.is_4_flush_on_board()
        assert ca.is_flush_on_board()

    def test_full_house(self):
        ca = analyzer_from_strs('2d', '2h', '5s', '8d', '5h', '8c', '5c')
        assert not ca.is_pair_on_board()
        assert not ca.is_trips_on_board()
        assert ca.is_full_house_on_board()

    def test_4_kind_with_hole(self):
        ca = analyzer_from_strs('2d', '2h', '5s', '5d', '5h', '8c', '5c')
        assert not ca.is_pair_on_board()
        assert not ca.is_trips_on_board()
        assert ca.is_4_of_a_kind_on_board()
