
package require Soar
source pokerLib.tcl

# --------------------------------------------------------------------

proc iProc {mode} {

	switch $mode {
		top-state-just-created {
			topStateJustCreated
		}
		normal-input-cycle {
			normalInputCycle
		}
		top-state-just-removed {
			# No action
		}
	}
}

# --------------------------------------------------------------------

proc topStateJustCreated {} {

	global g_clock g_clockLast g_inputLinkId g_timeTags

	setInputLinkId
	set g_clock 1
	set g_clockLast $g_clock

    # Add the clock wme to the input link. Save the timetag of 
	# the clock wme so we can update during normal input cycles.
	scan [add-wme $g_inputLinkId ^clock $g_clock] "%d" g_timeTags(clock)
}

# --------------------------------------------------------------------

proc normalInputCycle {} {

	global g_clock g_clockLast g_gameId g_gameInfo g_inputLinkId g_timeTags

    # The output proc increments g_clock. If g_clock and
    # g_clockLast are different, make the clock tick:
	# Remove the old clock wme and add the new clock wme.
    if {$g_clock != $g_clockLast} {
		remove-wme $g_timeTags(clock)
		scan [add-wme $g_inputLinkId ^clock $g_clock] "%d" g_timeTags(clock)
		set g_clockLast $g_clock
    }

	# ----------------------------------------------------------------
	# Games, Stages, and Bets:
	#
	# A game has 4 stages: 
	#    preflop - Each player receives 2 hole cards. Nothing on board.
	#    flop - First 3 common cards on board.
	#    turn - Next common card on board.
	#    river - Last common card on board.
	# A game can end at any stage. 
	#
	# Within each stage, there are up to 4 bets.
    #
    # Bets to call == the number of bets the player has to call to stay in.
	#   Type is float, not integer, because the small blind often has
	#   0.5 bets to call in the preflop betting. 
    #
    # Num bets == number of bets so far in stage. 
	# ----------------------------------------------------------------

	# ----------------------------------------------------------------
    # As the game continues, things like the pot, the number of active 
	# players, etc., change. Update their wme's. If we're within a game 
	# (not newGame), remove the old wme's first. If we're starting 
	# a new game, the wme's don't yet exist, so nothing to remove.
	# ----------------------------------------------------------------

	checkNewGame
	checkNewStage
	updateGameWme amountSoarBotHasInPot amount-soarbot-has-in-pot
	updateGameWme checkRaiseUsed        check-raise-used
	updateGameWme betsToCall            bets-to-call
	updateGameWme numActivePlayers      num-active-players
	updateGameWme numBets               num-bets
	updateGameWme pot                   pot
	updateGameWme potOdds               pot-odds
	updateGameWme unacted               unacted
}

# --------------------------------------------------------------------

proc checkNewGame {} {

	global g_gameId g_gameInfo g_inputLinkId g_timeTags

	# Java side sets new game flag
	if {! $g_gameInfo(newGame)} {
		return 0
	}

	echo "\n============================================================="
    echo "NEW GAME $g_gameInfo(gameNum) @ [clock format [clock seconds]]"
	echo "============================================================="

	# Clear the flag
	set g_gameInfo(newGame) 0

	# If there's an old game, remove it.
	removeWmeIfExists g_timeTags(game)

	# These globals stored time tags from the old game. The old game
	# is gone, so the time tags are invalid. So unset the globals.
	unsetGameTimeTags

	# Create the new game wme. Save its timetag and id.
	set tmp [add-wme-and-get-timetag-and-id $g_inputLinkId ^game]
	set g_timeTags(game) [lindex $tmp 0]
	set g_gameId [lindex $tmp 1]

	setNewGameData

	return 1
}

# --------------------------------------------------------------------

proc checkNewStage {} {

	global g_gameId g_gameInfo g_timeTags

	# Java side sets new stage flag
	if {! $g_gameInfo(newStage)} {
		return 0
	}

	echo "============================================================="
    echo "NEW STAGE $g_gameInfo(stage) ($g_gameInfo(gameNum)) @ [clock format [clock seconds]]"
	echo "============================================================="

	# Clear the flag
	set g_gameInfo(newStage) 0

	updateGameWme stage stage

	# New cards
	switch $g_gameInfo(stage) {
		preflop {
			setCard preflopCard1
			setCard preflopCard2
		}
		flop { 
			setCard flopCard1
			setCard flopCard2
			setCard flopCard3
		}
		turn { 
			setCard turnCard1
		}
		river { 
			setCard riverCard1
		}
		default { 
			debug "Unexpected stage value: $g_gameInfo(stage)"
		}
	}

	# Update data that change when stage changes
	updateGameWme bestHandProbability best-hand-probability
	updateGameWme betSize             bet-size
	updateGameWme negativePotential   negative-potential
	updateGameWme potential           potential

	# Clear analysis attribute. Elaborations will set it.
	updateGameWmeValue analysis analysis *

	return 1
}

# --------------------------------------------------------------------

proc setNewGameData {} {

	global g_gameId g_gameInfo

	# ----------------------------------------------------------------
	# Button: In a casino poker game, the casino supplies the dealer.
	# Because position is so important, the dealer acts as a surrogate
	# for each player in turn, and s/he uses a large plastic button
	# to show which player is the notional dealer. The simulation
	# software follows this terminology. Hence the button.
	#
	# Blinds: The player to the button's right must ante half the 
	# normal bet amount. He's betting blind, so he's the small blind.
	# The player to the small blind's right must ante the full
	# normal bet amount, so he's the big blind. The blind bets
	# get the pot started.
	# ----------------------------------------------------------------

	add-wme $g_gameId ^game-num $g_gameInfo(gameNum)
	add-wme $g_gameId ^max-bets $g_gameInfo(maxBets)
	add-wme $g_gameId ^num-players $g_gameInfo(numPlayers)
	add-wme $g_gameId ^button $g_gameInfo(button)
	add-wme $g_gameId ^position $g_gameInfo(position)
	set dist [pLdistanceFromButton $g_gameInfo(numPlayers) \
				  $g_gameInfo(button) $g_gameInfo(position)]
	add-wme $g_gameId ^distance-from-button $dist
	add-wme $g_gameId ^bet-timing \
		[pLbetTiming $g_gameInfo(numPlayers) $dist]
	# big blind, small blind, or no blind?
	switch $dist {
		1 { set blind small }
		2 { set blind big }
		default { set blind no }
	}
	add-wme $g_gameId ^blind $blind
	add-wme $g_gameId ^bluff [setBluff]

	# create some game info entries that the java layer doesn't know about
	set g_gameInfo(topBoardRankNum) 0
}

# --------------------------------------------------------------------

proc setBluff {} {

	set x [expr (rand())]
	# Set flag frequently because we don't always bluff when the 
	# flag is set - the flag makes bluffing possible, not guaranteed.
	if {$x <= 0.2} { ; 
		#debug "Potential bluff on this hand"
		return yes
	} else {
		return no
	}
}

# --------------------------------------------------------------------

proc setCard {key} {

	global g_gameId g_gameInfo

	# list is [rank, suit, type, num]
	set cardAttribList $g_gameInfo($key)
	set cardId [add-wme-and-get-id $g_gameId ^card]
	set rank [lindex $cardAttribList 0] 
	add-wme $cardId ^rank $rank
	add-wme $cardId ^suit [lindex $cardAttribList 1]
	set type [lindex $cardAttribList 2]
	add-wme $cardId ^type $type 
	add-wme $cardId ^num [lindex $cardAttribList 3]
	
	# rank-num so we can test for high card
	set rankNum [rankNum $rank]
	add-wme $cardId ^rank-num $rankNum

	# track highest board rank-num
	if {[string compare $type board] == 0} {
		if {$rankNum > $g_gameInfo(topBoardRankNum)} {
			set g_gameInfo(topBoardRankNum) $rankNum
			updateGameWmeValue topBoardRankNum top-board-rank-num $rankNum
		}
	}

	# so we can test for straights
	set nextRank [nextRank $rank]
	add-wme $cardId ^next-rank $nextRank
	add-wme $cardId ^next-next-rank [nextRank $nextRank]
	# rank-nums of cards that could be in a straight with this card
	add-wme $cardId ^max-straight-rank-num [maxStraightRankNum $rankNum]
}

# --------------------------------------------------------------------

# Numeric value for the rank, for comparisons

proc rankNum {rank} {

	switch $rank {
		t {set rv 10}
		j {set rv 11}
		q {set rv 12}
		k {set rv 13}
		a {set rv 14} 
		default {set rv $rank}
	}
	return $rv
}

# --------------------------------------------------------------------

proc nextRank {rank} {

	switch $rank {
		9 {set rv t}
		t {set rv j}
		j {set rv q}
		q {set rv k}
		k {set rv a}
		a {set rv 2} ; # ace as low card
		default {set rv [expr ($rank + 1)]}
	}
	return $rv
}

# --------------------------------------------------------------------

proc maxStraightRankNum {rankNum} {

	switch $rankNum {
		11 {set rv 14}
		12 {set rv 14}
		13 {set rv 14}
		14 {set rv 5} ; # ace as low card - 1...5
		default {set rv [expr ($rankNum + 4)]}
	}
	return $rv
}
# --------------------------------------------------------------------

proc oProc {mode outputs} {	

	switch $mode {
		added-output-command {
			addedOrModifiedOutput $outputs
		}
		modified-output-command {
			addedOrModifiedOutput $outputs
		}
		removed-output-command {
			# No action
		}
	}
}

# --------------------------------------------------------------------

proc addedOrModifiedOutput {outputs} {

	global g_betAction g_clock

	# Get the output list for the bet.action wme.
	set actionList [getAttributeList $outputs action]
	if { ! [string match $actionList {}] } {
		set g_betAction [lindex $actionList 2]
		debug "Setting g_betAction to $g_betAction @ clock == $g_clock"
		# Create bet.status wme with a value of complete. 
		add-wme [lindex $actionList 0] ^status complete 
		incr g_clock
	} else {
		set g_betAction {}
	}
}

# --------------------------------------------------------------------

# outputs is a list of wme lists. Each wme list consists of:
#     parent identifier, attribute, value.
# Find the list for the target attribute and return it.
# If not found, return {}.

proc getAttributeList {outputs target} {

	foreach wme $outputs {
		set nxt [lindex $wme 1]
		if {[string match $nxt $target]} {
			return $wme
		}
	}
	return {}
}

# --------------------------------------------------------------------

proc add-wme-and-get-id {obj attr} {

    scan [add-wme $obj $attr *] "%d: %s %s %s" \
	    timetag object attribute id
    return $id
}

# --------------------------------------------------------------------

proc add-wme-and-get-timetag-and-id {obj attr} {

    scan [add-wme $obj $attr *] "%d: %s %s %s" \
	    timetag object attribute id
    return [list $timetag $id]
}

# --------------------------------------------------------------------
proc setInputLinkId {} {

	global g_inputLinkId

	# Set the global input link id

	# Find the identifier for the root of I/O activity.  On the 
    # top-state this identifier is the value of the "io" attribute.
    # We use the command "output-strings-destination" to return the
    # results of the wmes command rather than printing the information
    # to the screen.

	# First, find the top state id:

	output-strings-destination -push -append-to-result
	scan [print -internal {(* ^superstate nil)}] "(%d: %s" timetag top_state_id
    set top_wmes [print -internal $top_state_id]
    output-strings-destination -pop

	# Now find the io header id within the top state wmes.  We
    # cannot use "wmes" here because although the addition of the 
    # "io" link has just been made in the agent, the WME additions 
    # are buffered until all the input functions have been processed.

	set io_header_part [lindex $top_wmes [expr [lsearch $top_wmes "^io"] + 1]]
	set ioId [string trimright $io_header_part ")"]

	# Get the input link id

	output-strings-destination -push -append-to-result
	set io_wmes [print -internal $ioId]
  	output-strings-destination -pop
	set input_header [lindex $io_wmes [expr [lsearch $io_wmes "^input-link"] + 1]]
    set g_inputLinkId [string trimright $input_header ")"]
}

# --------------------------------------------------------------------

proc unsetIfExists {varName} {

	upvar $varName var
	if {[info exists var]} {
		#debug "Unsetting $varName"
		unset var
	}
}

# --------------------------------------------------------------------

# If var exists, it's the value of a wme. Remove the wme.

proc removeWmeIfExists {varName} {

	upvar $varName var
	if {[info exists var]} {
		remove-wme $var
	}
}

# --------------------------------------------------------------------

# Combines the wme remove/add.

proc updateGameWme {key wme} {

	global g_gameId g_gameInfo g_timeTags

	removeWmeIfExists g_timeTags($key)
	scan [add-wme $g_gameId ^$wme $g_gameInfo($key)] "%d" g_timeTags($key)
}

# --------------------------------------------------------------------

# Combines the wme remove/add.

proc updateGameWmeValue {key wme value} {

	global g_gameId g_timeTags

	removeWmeIfExists g_timeTags($key)
	scan [add-wme $g_gameId ^$wme $value] "%d" g_timeTags($key)
}

# --------------------------------------------------------------------

# Unset existing game time tags - go through g_timeTags, and skip
# the special cases. This way, any time tags we add are unset
# automatically.

proc unsetGameTimeTags {} {

	global g_timeTags

	foreach timeTag [array names g_timeTags] {
		switch $timeTag {
			clock   { continue }
			game    { continue }
			default {unsetIfExists g_timeTags($timeTag) }
		}
	}
}

# --------------------------------------------------------------------

proc debug {msg} {

	echo "\ndebug {pokerIo}: $msg"
}

# --------------------------------------------------------------------

# Add i/o routines to Soar just once.

if {[info exists g_pokerIoAdded] == 0} {
	set g_pokerIoAdded 1
	io -add -input iProc input-link
	io -add -output oProc output-link
}

# --------------------------------------------------------------------
