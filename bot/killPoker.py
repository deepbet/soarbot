#!/usr/bin/python

import os, string

FILE_NAME = "killPoker.out"
os.system('ps -C "java poker.online.BotPlayer" > %s' % FILE_NAME)
f = open(FILE_NAME,'r')
l = f.readline() # headings
l = f.readline() # first data line
if l:
	pid, tty, time, cmd = string.split(l)
	killPid = "kill " + pid
	print("found poker @", pid, "- killing it")
	os.system(killPid)
else:
	print("poker not found")
f.close()
os.remove(FILE_NAME)


