from enum import Enum


class Position(Enum):
    SmallBlind = 0
    BigBlind = 1
    UnderTheGun = 2
    Middle = 3
    Cutoff = 4
    Button = 5

    def __str__(self):
        return self.name


class BetTiming(Enum):
    """
    The position of a player in the game in terms of its strength:
    button | blind | early | middle | late.
    The later a player bets, the stronger its position.
    The button is always the last to act.
    """
    Button = 0
    Blind = 1
    Early = 2
    Middle = 3
    Late = 4

    @classmethod
    def get_list(cls, num_players):
        """
        Get the list of timings for the number of players in the game (starting with the Button).
        Canonical for a 10-player game, starting from the button:
        """

        if num_players < 2:
            raise ValueError(f"Not enough players ({num_players})")

        # Build a list starting from the button.
        # 2 players to button's left are always blinds.
        positions = [cls.Button, cls.Blind]
        if num_players == 2:
            return positions

        positions.append(cls.Blind)
        if num_players == 3:
            return positions

        # The last player in the list, the one to the button's right,
        # will be 'Late', so subtract 4 to calc # of early-middle.
        num_early_middle = num_players - 4

        # Assign up to 3 middle values next. The rest are early.
        # We favor middle over early because the number of players
        # acting behind determines the relative strength.
        num_middle = 3 if num_early_middle > 3 else num_early_middle
        num_early = num_early_middle - num_middle

        # my custom implementation to allow the 'Early' in 6-players game:
        if num_early_middle >= 2:
            if num_early == 0:
                num_early = 1
                num_middle -= 1

        return positions + [cls.Early] * num_early + [cls.Middle] * num_middle + [cls.Late]


def get_distance_from_button(pos, btn_pos, num_players):
    if pos >= btn_pos:
        return pos - btn_pos

    return pos + num_players - btn_pos
