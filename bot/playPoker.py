#!/usr/bin/python

import getopt, os, sys, time

TRUE = 1
FALSE = 0

# --------------------------------------------------------------------

def usage():
	print(r"""
Usage error!

Usage: playPoker [-b|f] [-pNNNNN] userName

Options:

b|f    - Run mode: background or foreground. Background logs all
         output to a file, alberta-yyyy-mm-dd.log. Optional; default
		 is background.

pNNNNN - Port. Optional; default is 55000. Values as of 10/2002:
         55000 - Bots & Humans
         55001 - Bots & Humans ELITE
         55002 - Humans Heads-Up
         55003 - Pokibrat Heads-Up
		 
""")
	sys.exit(1)

# --------------------------------------------------------------------

def processArgs(commandLine):
	try:
		opts, args = getopt.getopt(commandLine, "bfp:")
	except getopt.error:
		usage()
	port = 55000
	background = TRUE
	for o, a in opts:
		if o == "-b":
			background = TRUE
		elif o == "-f":
			background = FALSE
		elif o == "-p":
			port = a
		else:
			usage()
	if len(args) == 1:
		userName = args[0]
	else:
		usage()
	return port, background, userName

# --------------------------------------------------------------------

if __name__ == "__main__":
	port, background, userName = processArgs(sys.argv[1:])
	if background:
		mode = '&'
		now = time.localtime(time.time())
		log = time.strftime(">> alberta-%Y-%m-%d.log", now)
	else:
		mode = ''
		log = ''
	cmd = "java poker.online.BotPlayer SoarBot.pd games.cs.ualberta.ca"
	cmd = cmd + (" %s %s %s %s %s" % (port, userName, userName, log, mode))
	#print(cmd)
	os.system(cmd)




