/* -------------------------------------------------------------------
 * SoarBot.java
 *
 * Bob Follek 
 * Thesis I Fall 2002
 * bob@codeblitz.com
 *
 * -----------------------------------------------------------------*/

/* -------------------------------------------------------------------
 * NOTES ON TERMINOLOGY
 *
 * BETS AND RAISES: The Alberta poker server doesn't distinguish
 * between bets and raises, and it refers to all bets as raises. 
 * I find this confusing, so I refer to all bets as bets.
 * -----------------------------------------------------------------*/

import java.text.*;
import java.util.*;

import nist.feather.*;
import poker.*;
import poker.ai.*;
import poker.online.*;
import poker.util.*;

// -------------------------------------------------------------------

public class SoarBot extends Player {

	public SoarBot() {

		super();

		final String INCREASE_MAX_CHUNKS = "max-chunks 200";

		writeHeading();
		try {
			m_ss = new SoarSession(PROPERTIES);
			//m_ss.setPrintCommandBeforeEval(true);
			m_ss.eval(INCREASE_MAX_CHUNKS);
			setSimulation();
			m_ss.loadAgent(POKER_AGENT);
		}
		catch (Exception e) {
			System.out.println(e);
		}
		initNumFormatter();
		initHandEvaluator();
		m_potential = new HandPotential();
	}

// -------------------------------------------------------------------

	public void newGame(GameInfo gInfo, Card c1, Card c2, int ID) { 

		final String KEY_BUTTON = "button";
		final String KEY_GAME_NUM = "gameNum";
		final String KEY_MAX_BETS = "maxBets";
		final String KEY_NEW_GAME = "newGame";
		final String KEY_NUM_PLAYERS = "numPlayers";
		final String KEY_POSITION = "position";

		m_gameInfo = gInfo;
		m_position = ID;
		m_lastStage = UNKNOWN_STAGE; // Force a break
		m_holeCard1 = c1;
		m_holeCard2 = c2;

		// Pass new game data to Tcl
		setGameInfo(KEY_NEW_GAME, "1");
		setGameInfo(KEY_GAME_NUM, m_gameInfo.getID());
		// See NOTES ON TERMINOLOGY/BETS AND RAISES up top
		setGameInfo(KEY_MAX_BETS, Holdem.MAX_RAISES);
		setGameInfo(KEY_NUM_PLAYERS, m_gameInfo.getNumPlayers());
		setGameInfo(KEY_BUTTON, m_gameInfo.getButton());
		setGameInfo(KEY_POSITION, ID);
		setGameInfo(KEY_CHECK_RAISE_USED, "no");
	}

// -------------------------------------------------------------------

	public int action() {

		final int DEFAULT_ACTION = PokerConsts.FOLD;
		// Tcl syntax - "set x" returns value of x
		final String GET_BET_ACTION = "set g_betAction;";
		final String CALL_STRING = "call";
		final String FOLD_STRING = "fold";
		final String RAISE_STRING = "raise";
		final String CHECK_RAISE_STRING = "check-raise";
		final String KEY_AMOUNT_SOARBOT_HAS_IN_POT = "amountSoarBotHasInPot";
		final String KEY_BETS_TO_CALL = "betsToCall";
		final String KEY_NUM_ACTIVE_PLAYERS = "numActivePlayers";
		final String KEY_NUM_BETS = "numBets";
		final String KEY_POT = "pot";
		final String KEY_POT_ODDS = "potOdds";
		final String KEY_UNACTED = "unacted";

		// Update game info
		setStage();
		setGameInfo(KEY_BETS_TO_CALL, m_gameInfo.getBetsToCall(m_position)); 
		// See NOTES ON TERMINOLOGY/BETS AND RAISES up top
		setGameInfo(KEY_NUM_BETS, m_gameInfo.getNumRaises());
		setGameInfo(KEY_NUM_ACTIVE_PLAYERS, m_gameInfo.getNumActivePlayers());
		setGameInfo(KEY_POT, m_gameInfo.getPot());
		setGameInfo(KEY_POT_ODDS, calcPotOdds());
		setGameInfo(KEY_AMOUNT_SOARBOT_HAS_IN_POT, getAmountSoarBotHasInPot());
		setGameInfo(KEY_UNACTED, m_gameInfo.getUnacted());
	
		if (m_pendingCheckRaise) {
			return finishCheckRaise();
		}
		else {
			try {
				m_ss.runTillOutput();
				String s = m_ss.eval(GET_BET_ACTION);
				if (s.equals(CALL_STRING)) {
					return PokerConsts.CALL;
				}
				else if (s.equals(FOLD_STRING)) {
					return PokerConsts.FOLD;
				}
				else if (s.equals(RAISE_STRING)) {
					return PokerConsts.RAISE;
				}
				else if (s.equals(CHECK_RAISE_STRING)) {
					// Start check-raise: set flag and check.
					m_pendingCheckRaise = true;
					return PokerConsts.CALL;
				}
				else {
					System.out.println("action() error: Unexpected fallthru.");
					return DEFAULT_ACTION;
				}
			}
			catch (TclEvalException tee) {
				System.out.println("action() error: " + tee);
				return DEFAULT_ACTION;
			}
		}
 	}

// -------------------------------------------------------------------

	// Skip the SOAR level - handle this here.
	private int finishCheckRaise() {

		// Clear flag
		m_pendingCheckRaise = false; 
		// If there's a raise left, make it, else call.
		if (m_gameInfo.getNumRaises() < Holdem.MAX_RAISES) {
			// Set game flag
			setGameInfo(KEY_CHECK_RAISE_USED, "yes");
			return PokerConsts.RAISE;
		}
		else {
			return PokerConsts.CALL;
		}
	}

// -------------------------------------------------------------------

	public void init(Preferences prefs) {

		// Not used
	}

// -------------------------------------------------------------------

	public void update(int action, int code) {

		// Return immediately
	}

// -------------------------------------------------------------------

	public void finalize() {

		System.out.println("SoarBot finalize() running");
		try {
			m_ss.stop();
		}
		catch (TclEvalException tee) {
			// ignore it
		}
	}

// -------------------------------------------------------------------

	private void setCard(String key, Card c, String type, int num) { 

		final String[] SUIT_CHARS = {"c", "d", "h", "s"};
		final String SET_CARD = "set g_gameInfo({0}) [list {1} {2} {3} {4}];";

		String rank = ("" + Card.getRankChar(c.getRank())).toLowerCase();
		String suit = SUIT_CHARS[c.getSuit()];
		String[] args = {key, rank, suit, type, Integer.toString(num)};
		String cmd = MessageFormat.format(SET_CARD, args); 
		try {
			m_ss.eval(cmd);
		}
		catch (TclEvalException tee) {
			System.out.println("setCard() error: " + tee);
		}
	}

// -------------------------------------------------------------------

	private void setStage() {

		final String PREFLOP_STRING = "preflop";
		final String FLOP_STRING = "flop";
		final String TURN_STRING = "turn";
		final String RIVER_STRING = "river";
		final String SHOWDOWN_STRING = "showdown";
		final String UNKNOWN_STAGE_STRING = "unknownStage";
		final String KEY_NEW_STAGE = "newStage";
		final String KEY_STAGE = "stage";
		final String KEY_BEST_HAND_PROBABILITY = "bestHandProbability";
		final String KEY_POTENTIAL = "potential";
		final String KEY_NEGATIVE_POTENTIAL = "negativePotential";
		final String KEY_BET_SIZE = "betSize";
	
		int currentStage = m_gameInfo.getStage();
		if (m_lastStage == currentStage) {
			return; // Nothing to do
		}
		
		m_lastStage = currentStage;
		m_pendingCheckRaise = false;
		String stageString;
		switch (currentStage) {
		case PokerConsts.PREFLOP:
			stageString = PREFLOP_STRING;
			setCard(KEY_PREFLOP_CARD_1, m_holeCard1, TYPE_HOLE_CARD, 
					1);
			setCard(KEY_PREFLOP_CARD_2, m_holeCard2, TYPE_HOLE_CARD, 
					2);
			break;
		case PokerConsts.FLOP:
			stageString = FLOP_STRING;
			setCard(KEY_FLOP_CARD_1, m_gameInfo.getBoardCard(0), TYPE_BOARD_CARD, 
					3);
			setCard(KEY_FLOP_CARD_2, m_gameInfo.getBoardCard(1), TYPE_BOARD_CARD, 
					4);
			setCard(KEY_FLOP_CARD_3, m_gameInfo.getBoardCard(2), TYPE_BOARD_CARD, 
					5);
			break;
		case PokerConsts.TURN:
			stageString = TURN_STRING;
			setCard(KEY_TURN_CARD, m_gameInfo.getBoardCard(3), TYPE_BOARD_CARD, 
					6);
			break;
		case PokerConsts.RIVER:
			stageString = RIVER_STRING;
			setCard(KEY_RIVER_CARD, m_gameInfo.getBoardCard(4), TYPE_BOARD_CARD, 
					7);
			break;
		case PokerConsts.SHOWDOWN:
			// Should not happen
			stageString = SHOWDOWN_STRING;
			break;
		default:
			// Should not happen
			stageString = UNKNOWN_STAGE_STRING;
			break;
		}
		setGameInfo(KEY_NEW_STAGE, "1");
		setGameInfo(KEY_STAGE, stageString);
		// Probability and potentials change when board changes. 
		// Board changes when stage changes. Bet size may change.
		setGameInfo(KEY_BEST_HAND_PROBABILITY, 
					getBestHandProbability(currentStage));
		setGameInfo(KEY_POTENTIAL, getPotential(currentStage));
		setGameInfo(KEY_NEGATIVE_POTENTIAL, getNegativePotential(currentStage));
		setGameInfo(KEY_BET_SIZE, m_gameInfo.getBetSize());
	}

// -------------------------------------------------------------------

	private void setGameInfo(String key, int i) {

		String value = Integer.toString(i);
		setGameInfo(key, value);
	}

// -------------------------------------------------------------------

	private void setGameInfo(String key, double d) {

		String value = Double.toString(d);
		setGameInfo(key, value);
	}

// -------------------------------------------------------------------

	private void setGameInfo(String key, String value) {

		final String SET_GAME_INFO = "set g_gameInfo({0}) {1};";
		final String ERR = 
			"setGameInfo error for key == {0}, value == {1}: {2}";

		String cmd = MessageFormat.format(SET_GAME_INFO, 
										  new String[] {key, value});
		try {
			m_ss.eval(cmd);
		}
		catch (TclEvalException tee) {
			String msg = 
				MessageFormat.format(ERR, 
									 new String[] {key, value, tee.toString()});
			System.out.println(msg);
		}
	}

// -------------------------------------------------------------------

	// So that Tcl/Soar code can distinguish between simulation and
	// interactive testing.
	private void setSimulation() {

		final String SET_SIMULATION = "set g_simulation 1;";

		try {
			m_ss.eval(SET_SIMULATION);
		}
		catch (TclEvalException tee) {
			System.out.println("setSimulation() error: " + tee);
		}
	}

// -------------------------------------------------------------------

	// Best at *this* moment. Ignores future potential, e.g.
	// a 4-flush may turn into a flush.
	private String getBestHandProbability(int currentStage) {

		double d;

		if (currentStage == PokerConsts.PREFLOP) {
			// Probability not defined till there are board cards
			d = 0.0; 	
		}
		else {
			Hand boardCards = m_gameInfo.getBoard();
			int numActivePlayers = m_gameInfo.getNumActivePlayers();
			if (numActivePlayers == 2) { // Just 1 opponent
				d = m_evaluator.handRank(m_holeCard1, m_holeCard2, boardCards);
			}
			else {
				d = m_evaluator.handRank(m_holeCard1, m_holeCard2, boardCards,
										 numActivePlayers);
			}
		}

		return m_numFormat.format(d);
	}

// -------------------------------------------------------------------

	// Potential that the hand will improve.
	private String getPotential(int currentStage) {

		final boolean LOOK_AHEAD_1_CARD = false;
		final boolean LOOK_AHEAD_2_CARDS = true; // Takes much longer

		double d;
		Hand boardCards;

		switch (currentStage) {
		case PokerConsts.PREFLOP:
			// Potential not defined till there are board cards
			d = 0.0; 	
			break;
		case PokerConsts.FLOP:
			boardCards = m_gameInfo.getBoard();
			d = m_potential.ppot_raw(m_holeCard1, m_holeCard2, boardCards, 
									 LOOK_AHEAD_1_CARD);
									 //LOOK_AHEAD_2_CARDS);
			break;
		case PokerConsts.TURN:
			boardCards = m_gameInfo.getBoard();
			d = m_potential.ppot_raw(m_holeCard1, m_holeCard2, boardCards, 
									LOOK_AHEAD_1_CARD);
			break;
		default:
			// river - no more potential
			d = 0.0;
			break;
		}

		return m_numFormat.format(d);
	}

// -------------------------------------------------------------------

	// Potential that the hand will get worse.
	// Call getPotential() first!
	private String getNegativePotential(int currentStage) {

		double d;

		switch (currentStage) {
		case PokerConsts.PREFLOP:
			// Potential not defined till there are board cards
			d = 0.0; 	
			break;
		case PokerConsts.FLOP:
			d = m_potential.getLastNPot();
			break;
		case PokerConsts.TURN:
			d = m_potential.getLastNPot();
			break;
		default:
			// river - no more potential
			d = 0.0;
			break;
		}

		return m_numFormat.format(d);
	}

// -------------------------------------------------------------------

	/* -------------------------------------------------------------------
	 * pot odds - ratio between what it costs to call && size of bot,
	 *  e.g. $10 to call, $50 in pot, potOdds = 5.
	 * -----------------------------------------------------------------*/

	private String calcPotOdds() {

		double d;
		double amountToCall =  m_gameInfo.getAmountToCall(m_position);
		if (amountToCall > 0.0) {
			d = m_gameInfo.getPot() / amountToCall;
		}
		else {
			d = INFINITE_POT_ODDS;
		}
		return m_numFormat.format(d);
	}

// -------------------------------------------------------------------

	private void initNumFormatter() {

		m_numFormat = NumberFormat.getInstance();
		m_numFormat.setMaximumFractionDigits(2); // 2 decimal places
		m_numFormat.setGroupingUsed(false); // No commas in 1,234, e.g.
	}

// -------------------------------------------------------------------

	private void initHandEvaluator() {

		String msg;
		m_evaluator = new HandEvaluator();
		if (m_evaluator.isNative()) {
			msg = "Native HandEvaluator library loaded.";
		} 
		else {
			msg = "WARNING! The native HandEvaluator library is faster! Use it!";
		}
		System.out.println('\n' + msg);
	}

// -------------------------------------------------------------------

	private void writeHeading() {

		final String LINE =
"-------------------------------------------------------------------------------";

		System.out.println(LINE);
		System.out.println(LINE);
		System.out.println("SoarBot starting at " + new Date());
		System.out.println(LINE);
		System.out.println(LINE);
	}

// -------------------------------------------------------------------

	private int getAmountSoarBotHasInPot() {

		PlayerInfo pi = m_gameInfo.getPlayerInfo(m_position);
		return pi.getAmountInPot();
	}

// -------------------------------------------------------------------

	private SoarSession m_ss;
	private GameInfo m_gameInfo;
	private int m_position;
	private int m_lastStage;
	private Card m_holeCard1;
	private Card m_holeCard2;
	private HandEvaluator m_evaluator;
	private HandPotential m_potential;
	private NumberFormat m_numFormat;
	private boolean m_pendingCheckRaise;

// -------------------------------------------------------------------

	static private final String PROPERTIES = "SoarBot.ini";
	static private final String POKER_AGENT = "poker.soar";
	static private final int    UNKNOWN_STAGE = PokerConsts.SHOWDOWN + 9999;
	static private final double INFINITE_POT_ODDS = 9999.00;

	static private final String TYPE_HOLE_CARD = "hole";
	static private final String TYPE_BOARD_CARD = "board";
	static private final String KEY_PREFLOP_CARD_1 = "preflopCard1";
	static private final String KEY_PREFLOP_CARD_2 = "preflopCard2";
	static private final String KEY_FLOP_CARD_1    = "flopCard1";
	static private final String KEY_FLOP_CARD_2    = "flopCard2";
	static private final String KEY_FLOP_CARD_3    = "flopCard3";
	static private final String KEY_TURN_CARD      = "turnCard1";
	static private final String KEY_RIVER_CARD     = "riverCard1";
	static private final String KEY_CHECK_RAISE_USED = "checkRaiseUsed";


// -------------------------------------------------------------------

}
