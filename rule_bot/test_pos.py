from .pos import BetTiming


def test_2_3_4_5_6():
    assert BetTiming.get_list(2) == [BetTiming.Button, BetTiming.Blind]
    assert BetTiming.get_list(3) == [BetTiming.Button, BetTiming.Blind, BetTiming.Blind]
    assert BetTiming.get_list(4) == [BetTiming.Button, BetTiming.Blind, BetTiming.Blind, BetTiming.Late]
    assert BetTiming.get_list(5) == [BetTiming.Button, BetTiming.Blind, BetTiming.Blind,
                                     BetTiming.Middle, BetTiming.Late]
    assert BetTiming.get_list(6) == [BetTiming.Button, BetTiming.Blind, BetTiming.Blind,
                                     BetTiming.Early, BetTiming.Middle, BetTiming.Late]


def test_with_early():
    assert BetTiming.get_list(7) == [BetTiming.Button, BetTiming.Blind, BetTiming.Blind,
                                     BetTiming.Early, BetTiming.Middle, BetTiming.Middle, BetTiming.Late]
    assert BetTiming.get_list(8) == [BetTiming.Button, BetTiming.Blind, BetTiming.Blind,
                                     BetTiming.Early,
                                     BetTiming.Middle, BetTiming.Middle, BetTiming.Middle, BetTiming.Late]
    assert BetTiming.get_list(9) == [BetTiming.Button, BetTiming.Blind, BetTiming.Blind,
                                     BetTiming.Early, BetTiming.Early,
                                     BetTiming.Middle, BetTiming.Middle, BetTiming.Middle, BetTiming.Late]

    assert BetTiming.get_list(10) == [BetTiming.Button, BetTiming.Blind, BetTiming.Blind,
                                      BetTiming.Early, BetTiming.Early, BetTiming.Early,
                                      BetTiming.Middle, BetTiming.Middle, BetTiming.Middle,
                                      BetTiming.Late]
