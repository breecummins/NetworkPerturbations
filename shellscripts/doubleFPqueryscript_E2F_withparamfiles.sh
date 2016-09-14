#!/bin/bash

. shellscripts/querylibrary.sh # import custom functions

FP1='{"E2F":[0,0],"E2F_Rb":[1,1]}' 
FP2='{"E2F":[1,8],"E2F_Rb":[0,0]}'
python $DSGRN/software/FPQuery/FPQuery2.py $DATABASEFILE DoubleFP $FP1 $FP2 > $DATABASEDIR/bistability_net4_$NETWORKID.txt
NUMFP=`getcountuniquelines $DATABASEDIR/bistability_net4_$NETWORKID.txt`
echo  "DoubleFPQuery:$FP1 $FP2 ** DoubleFPQueryParameterCount:"$NUMFP #split entries by **