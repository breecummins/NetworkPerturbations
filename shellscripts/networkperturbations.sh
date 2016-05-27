#!/bin/bash

# main script for constructing and analyzing network perturbations

# get commands
# note this is insecure, since these commands will be evaluated and could potentially cause damage
NETWORK_PERTURBATIONS_CMD=$1
HELPER_SCRIPT_CMD=$2

# # get variable numbers of sql queries (need later when db calculations happen here)
# num=3
# while [ $num -le $# ]
# do
#     QUERY_CMD_${!num}=$num
#     (( num++ ))
# done

DATETIME=`date +%Y_%m_%d_%H_%M_%S`
NETWORKDIR=./computations$DATETIME/networks
PATTERNDIR=./computations$DATETIME/patterns
DATABASEDIR=./computations$DATETIME/databases
RESULTSDIR=./computations$DATETIME/results

mkdir -p $NETWORKDIR/ $PATTERNDIR/ $DATABASEDIR/ $RESULTSDIR

`$NETWORK_PERTURBATIONS_CMD $NETWORKDIR $PATTERNDIR`

for NETWORKFILE in $( echo $INPUTDIR/* | xargs ls ); do
	bname=`basename $NETWORKFILE`
	netid=${bname%%.*}
	NETWORKID=${netid##network}
	`$HELPER_SCRIPT_CMD $NETWORKFILE $PATTERNDIR $DATABASEDIR $RESULTSDIR $NETWORKID`
done

