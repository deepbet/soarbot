# --------------------------------------------------------------------
# pokerLib.tcl
#
# Tcl commands for poker.
#
# Bob Follek
# Thesis I Fall 2002
# bob@codeblitz.com
#
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# Return bot's bet timing value in the game: button | blind | early |
# middle | late. The later a player bets, the stronger its position.
# The button is always the last to act.
#
# Adjust for the number of players in the game.
# Canonical for a 10-player game, starting from the button:
# {button blind blind early early early middle middle middle late}

proc pLbetTiming {numPlayers distanceFromButton} {

	# Build a list starting from the button. 2 players to
	# button's left are always blinds.
	set lst {button blind blind}

	# The last player in the list, the one to the button's right,
	# will be late, so subtract 4 to calc # of early-middle.
	set numEarlyMiddle [expr {$numPlayers - 4}]

	# Assign up to 3 middle values next. The rest are early.
	# We favor middle over early because the number of players
	# acting behind determines the relative strength.
	if {$numEarlyMiddle > 3} {
		set numMiddle 3
		set numEarly [expr {$numEarlyMiddle - 3}]
	} else {
		set numMiddle $numEarlyMiddle
		set numEarly 0
	}
	for {set i 0} {$i < $numEarly} {incr i} {
		lappend lst early
	}
	for {set i 0} {$i < $numMiddle} {incr i} {
		lappend lst middle
	}
	# Now the last player, the one to the button's right - late.
	lappend lst late

	# Now index into the list to get the bot's timing.
	return [lindex $lst $distanceFromButton]
}

# --------------------------------------------------------------------

proc pLdistanceFromButton {numPlayers button position} {

    if {$position >= $button} {
        return [expr {$position - $button}]
    } else {
        return [expr {$position + $numPlayers - $button}]
    }
}

# --------------------------------------------------------------------
