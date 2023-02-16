#!/bin/bash

# EXAMPLE: ./convert.sh game.?.log > games.total


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
TABLE_NAME=test-tcp

for file in $@; do
  echo $file 1>&2

  # uncomment to start with the $pattern
  line_no=0  #$(grep -nm1 $pattern $file | cut -f1 -d:)

  # remove what is left of unfinished game
  python $SCRIPT_DIR/convert.py \
    <(awk 'NR==FNR{if (/small_blind_amount/) hit=NR; next} {print} FNR==hit{exit}' <(tail -n+$line_no $file) <(tail -n+$line_no $file)| sed '$d') $TABLE_NAME
done

total=$(grep Hold games.total | wc -l)
echo "Total games: $total" 1>&2
