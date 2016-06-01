#!/bin/bash

# main script for constructing and analyzing network perturbations
# dependencies: bash 4 (associative arrays), dsgrn installed on path (get number of parameters -- see querylibrary.sh), DSGRN dependencies, mpiexec, python 2.7, sqlite3

# get commands
# note this is insecure, since these commands will be evaluated and could potentially cause damage
PATH_TO_DSGRN=$1
NETWORK_PERTURBATIONS_CMD=$2
HELPER_SCRIPT_CMD=$3
QUERIES=$4 # QUERIES is an associative array of elements (key, query_cmd, query_arg, summary_cmd)

# make folders to hold input, intermediate, and output files
DATETIME=`date +%Y_%m_%d_%H_%M_%S`
NETWORKDIR=./computations$DATETIME/networks
PATTERNDIR=./computations$DATETIME/patterns
DATABASEDIR=./computations$DATETIME/databases
RESULTSDIR=./computations$DATETIME/results

mkdir -p $NETWORKDIR/ $PATTERNDIR/ $DATABASEDIR/ $RESULTSDIR

# construct the perturbations (required) and patterns (optional)
$NETWORK_PERTURBATIONS_CMD $NETWORKDIR $PATTERNDIR

# for each perturbation, start a scheduled job for analysis
for NETWORKFILE in $( echo $INPUTDIR/* | xargs ls ); do
	bname=`basename $NETWORKFILE`
	netid=${bname%%.*}
	NETWORKID=${netid##network}
	$HELPER_SCRIPT_CMD $PATH_TO_DSGRN $NETWORKFILE $PATTERNDIR $DATABASEDIR $RESULTSDIR $NETWORKID $QUERIES
done

