
		Bob Follek
		bob@codeblitz.com
		Thesis I Fall 2002

						SoarBot Installation Instructions

----------------------------------------------------------------------

		0. Requirements

		* Linux

		* A working version of SoarSession.

		* A network connection.

		* Python (for the startup/shutdown scripts).

----------------------------------------------------------------------

		1. Installing the Alberta Poker Client Framework

		* The Alberta poker client Java framework is available at
		http://spaz.ca/aaron/poker/src/index.html. 
		 
		* Download poki.tar.gz and untar it someplace.
		
		* make to build everything fresh on your system.

		* Add /your/path/to/poki/classes to CLASSPATH.

----------------------------------------------------------------------

		2. Installing the Hand Evaluator Library

		The Alberta software wraps an open-source native-mode hand
		evaluator library. Install the native-mode library because it
		runs faster.

		* The native-mode hand evaluator library is available at
		http://spaz.ca/aaron/poker/src/eval.html

		* Download libeval_linux.so.gz and gunzip it someplace.

		* Add /your/path/to/libeval_linux.so to LD_LIBRARY_PATH.

		If all is well, the alberta log file (see below) will display
		this message up top:

			 Native HandEvaluator library loaded.

		If something is wrong, the program will run with the slower Java
		version of the hand evaluator, and the log will display:

			WARNING! The native HandEvaluator library is faster! Use it!

----------------------------------------------------------------------

		3. Installing My Program, SoarBot

		* untar SoarBot.tgz into one directory.

		* Edit SoarBot.ini and set TCL_DIR and SOAR_DIR to the correct
        values for your system.

----------------------------------------------------------------------

		4. Running SoarBot

		* cd to /your/SoarBot/directory

		* playPoker is a Python script that handles the startup
		details. By default, it runs SoarBot as a background task,
		with output to log files. To use it,

			 playPoker SoarBot02

		SoarBot02 will be your name in the game. I use other SoarBot* 
		names, so we won't trip over each other.

		* To stop playing, use the Python script

			 killPoker

		You can run this at any time without disrupting a game in
		progress. If you're in the middle of a hand, the server will 
		fold your hand politely before it disconnects you.

----------------------------------------------------------------------

		5. Log Files

		Output from the alberta poker server goes to a daily log file
		in /your/SoarBot/directory named

			   alberta-yyyy-mm-dd.log

	    This is the file that shows the poker game action. Multiple
	    poker sessions in a day are appended to the day's log file.

		Debugging output from the Soar level goes to

			   SoarBot-yyyy-mm-dd.log

	    There's enough info in the SoarBot log file so that you can
	    cross-reference between game action and Soar output using game numbers.

----------------------------------------------------------------------

		6. Main Files

		SoarBot.java - My Java program that extends the Alberta
		framework. 

		pokerIo.tcl - The input/output link.

		poker.soar - The main Soar file.