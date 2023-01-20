
set tmp [clock format [clock seconds] -format "%Y-%m-%d"]
set g_logFile [open "SoarBot-$tmp.log" a]
unset tmp
output-strings-destination -push -channel $g_logFile