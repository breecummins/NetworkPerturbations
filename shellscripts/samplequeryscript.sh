#!/bin/bash

. shellscripts/querylibrary.sh # import custom functions

FPINPUT='{"SBF":[2,8],"HCM1":[1,8],"NDD1":[0,0],"SWI5":[0,0],"YOX1":[0,0]}'
python $DSGRN/software/FPQuery/FPQuery2.py $DATABASEFILE SingleFP $FPINPUT > $DATABASEDIR/query$NETWORKID.txt
NUMFP=`getcountuniquelines $DATABASEDIR/query$NETWORKID.txt`
rm $DATABASEDIR/query$NETWORKID.txt
printf "SingleFPQuery:$FPINPUT SingleFPQueryParameterCount:"$(($NUMFP-1)) # subtract 1 because first line of FPQuery2 is the FP