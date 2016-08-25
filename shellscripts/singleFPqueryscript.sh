#!/bin/bash

. shellscripts/querylibrary.sh # import custom functions

FPINPUT='{"SBF":[2,8],"HCM1":[1,8],"NDD1":[0,0],"SWI5":[0,0],"YOX1":[0,0]}'
python $DSGRN/software/FPQuery/FPQuery2.py $DATABASEFILE SingleFP $FPINPUT > $DATABASEDIR/query$NETWORKID.txt
NUMFP=`getcountuniquelines $DATABASEDIR/query$NETWORKID.txt`
rm $DATABASEDIR/query$NETWORKID.txt
echo "SingleFPQuery:$FPINPUT ** SingleFPQueryParameterCount:"$NUMFP #split entries by **