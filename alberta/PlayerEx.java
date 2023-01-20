/* -------------------------------------------------------------------
 * PlayerEx.java
 *
 * Bob Follek
 * Thesis II Spring 2003
 * bob@codeblitz.com
 *
 * -----------------------------------------------------------------*/

/* -------------------------------------------------------------------
 * PlayerEx extends the Alberta Player class so that
 * SoarBot's shutdown() method gets a callback at shutdown time.
 *
 * Put PlayerEx.java in the same directory as Player:
 * /your/alberta/poki/poker
 * Then run make from /your/alberta/poki.
 * -----------------------------------------------------------------*/

package poker;

public abstract class PlayerEx extends Player {

	public abstract void shutdown();

}