/* -------------------------------------------------------------------
 * BotPlayerEx.java
 *
 * Bob Follek
 * Thesis II Spring 2003
 * bob@codeblitz.com
 *
 * -----------------------------------------------------------------*/

/* -------------------------------------------------------------------
 * BotPlayerEx extends the Alberta BotPlayer class so that
 * SoarBot's shutdown() method gets a callback at shutdown time.
 *
 * Put BotPlayerEx.java in the same directory as BotPlayer:
 * /your/alberta/poki/poker/online
 * Then run make from /your/alberta/poki.
 * -----------------------------------------------------------------*/

package poker.online;

import poker.*;
import poker.online.*;

class BotPlayerEx extends BotPlayer {

/*
 * Have to code constructors because they're not default -
 * they have args.
 */

    public BotPlayerEx(String pfile) {
		super(pfile);
	}

    public BotPlayerEx(Player p, String server, int port, String nick, String pwd) {
        super(p, server, port, nick, pwd);
	}

/*
 * Have to override main() to get a BotPlayerEx instead of a BotPlayer.
 */

    static public void main(String[] args) {
		new BotPlayerEx(Player.loadPlayer(args[0]),
				args[1], Integer.decode(args[2]).intValue(), args[3], args[4]);
	}

/*
 * This is what we're here for: give SoarBot's shutdown a chance to run.
 */
    public void shutdown() {
        PlayerEx pe = (PlayerEx) bot;
        println("Calling PlayerEx shutdown...");
        pe.shutdown();
        super.shutdown();
    }
}
