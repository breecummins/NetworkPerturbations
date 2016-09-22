#!/bin/bash

# main script for constructing and analyzing network perturbations
# dependencies: bash 4 (associative arrays), dsgrn installed on path (get number of parameters -- see querylibrary.sh), DSGRN dependencies, mpiexec, python 2.7, sqlite3

# get paths
PATH_TO_DSGRN=$1
NETWORKDIR=$2
PATTERNDIR=$3
DATABASEDIR=$4
RESULTSDIR=$5
# note the following commands are insecure, since they will be evaluated and could potentially cause damage
QUERYFILE=$6 # name of a shell script that performs an FP Query and summary stats on query; returns string of items "name:value" that will be saved into a json dictionary
HELPER_SCRIPT_CMD=$7
RUN_TYPE=$8
RMDB=$9
RMNF=$10

# for each perturbation, start a scheduled job for analysis
for NETWORKFILE in $NETWORKDIR/*; do
	# strip the uniquely identifying number off of the filename
	bname=`basename $NETWORKFILE`
	netid=${bname%%.*}
	NETWORKID=${netid##network} 
	# start a scheduled job
	if [[ $RUN_TYPE = "qsub" ]]; then
		qsub $HELPER_SCRIPT_CMD $PATH_TO_DSGRN $NETWORKFILE $PATTERNDIR $DATABASEDIR $RESULTSDIR $NETWORKID $QUERYFILE $RMDB $RMNF
	elif [[ $RUN_TYPE = "sbatch" ]]; then
		sbatch $HELPER_SCRIPT_CMD $PATH_TO_DSGRN $NETWORKFILE $PATTERNDIR $DATABASEDIR $RESULTSDIR $NETWORKID $QUERYFILE $RMDB $RMNF
	elif [[ $RUN_TYPE = "local" ]]; then
		. $HELPER_SCRIPT_CMD $PATH_TO_DSGRN $NETWORKFILE $PATTERNDIR $DATABASEDIR $RESULTSDIR $NETWORKID $QUERYFILE $RMDB $RMNF
	fi
done

