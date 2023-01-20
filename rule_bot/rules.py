
# check-raise proposals
# If we've got the best cards, early position, and no bets yet,
# check-raise.
if game.num-bets <= 1 && game.bet-timing=='early' && preflop-strength == 1:
    # There’s always at least one bet in the preflop stage, because of the big blind.
    bet.action='check-raise'
    score = 40

# raise proposals
# If we've got the best cards, bet-raise as much as possible.
if game.num-bets < game.max-bets && preflop-strength == 1:
    # bet-raise*always
    bet.action='raise'
    score = 30

# If we've got excellent cards and excellent position, bet-raise as
# much as possible.
if game.num-bets < game.max-bets && game.bet-timing in ['late', 'button'] && preflop-strength <= 2:
    # bet-raise*excellent-both
    bet.action='raise'
    score = 30

# If we've got excellent cards, bet-raise once.
if game.num-bets <= 1 && preflop-strength <= 2:
    # bet-raise*excellent-cards
    bet.action='raise'
    score = 30

# If we've got decent cards and excellent position, bet-raise once.
if game.num-bets <= 1 && game.bet-timing in ['late', 'button'] && preflop-strength <= 3:
    # raise*excellent-position
    bet.action='raise'
    score = 30


# call proposals
# Decent cards - worth seeing the flop.
if preflop-strength <= 3:
    # call
    bet.action = 'call'
    score = 20

# If bluff flag is set and we have good position, call.
# The idea is to be less predictable by playing some cards we would
# normally toss.
if game.bet-timing in ['late', 'button'] && bluff:
    # call*bluff
    bet.action = 'call'
    score = 20

# Weak pairs, strong position, low cost - try to hit trips.
if game.num-bets == 1 && game.bet-timing in ['late', 'button'] && preflop-strength <= 5:
    # call*weak-pairs
    bet.action = 'call'
    score = 20

# Weak pairs, small blind, half a bet - try to hit trips.
if game.bets-to-call == 0.5 && blind == 'small' && preflop-strength <= 5:
    # call*weak-pairs*small-blind
    bet.action = 'call'
    score = 20
