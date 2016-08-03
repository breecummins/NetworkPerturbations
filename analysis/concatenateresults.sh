#!/bin/bash

# creates json array of dictionaries from individual results files

SAVEFILE=$1 #json
OUTPUTDIR=$2 #results dir

printf "[" > $SAVEFILE #write to file

for i in $(ls $OUTPUTDIR/*); do
	cat $i >> $SAVEFILE; #append to file
	printf ',' >> $SAVEFILE;
done

sed -i '$ s/.$/]/' $SAVEFILE #replace last comma with closing bracket

