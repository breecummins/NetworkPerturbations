#!/bin/bash

# main script for constructing and analyzing network perturbations
# dependencies: bash 4 (associative arrays), dsgrn installed on path (get number of parameters -- see querylibrary.sh), DSGRN dependencies, mpiexec, python 2.7, sqlite3

# get paths
PATH_TO_DSGRN=$1
NETWORKDIR=$2
PATTERNDIR=$3
DATABASEDIR=$4
RESULTSDIR=$5
# get commands
# note this is insecure, since these commands will be evaluated and could potentially cause damage
HELPER_SCRIPT_CMD=$6
QSUB=$7
# QUERIES=$7 # QUERIES is an associative array of elements (key, query_cmd, query_arg, summary_cmd)

# for each perturbation, start a scheduled job for analysis
for NETWORKFILE in $NETWORKDIR/*; do
	# strip the uniquely identifying number off of the filename
	bname=`basename $NETWORKFILE`
	netid=${bname%%.*}
	NETWORKID=${netid##network} 
	# start a scheduled job
	if [[ $QSUB == "True" ]]; then
		qsub $HELPER_SCRIPT_CMD $PATH_TO_DSGRN $NETWORKFILE $PATTERNDIR $DATABASEDIR $RESULTSDIR $NETWORKID #$QUERIES
	else;
		echo "\nsbatch not implemented yet\n"
	fi
done

