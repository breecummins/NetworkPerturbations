#!/bin/bash

# dependencies: dsgrn in path, DSGRN dependencies, bash 4, mpiexec, python 2.7, qsub, sqlite3

. shellscripts/querylibrary.sh # import custom functions

NSLOTS=4

DSGRN=$1
SIGNATURES="$DSGRN/software/Signatures/bin/Signatures"
PATTERNMATCH="$DSGRN/software/PatternMatch/bin/PatternMatchDatabase"

NETWORKFILE=$2
PATTERNDIR=$3 
DATABASEDIR=$4 
RESULTSDIR=$5 
NETWORKID=$6
QUERYFILE=$7
RMDB=$8
RMNF=$9

DATABASEFILE="$DATABASEDIR/database$NETWORKID.db"

# make database
mpiexec -np $NSLOTS $SIGNATURES $NETWORKFILE $DATABASEFILE

# if making the database fails, then quit
if [ ! -f $DATABASEFILE ]; then echo "Database $NETWORKID did not compute\n"; cat $2; exit 1; fi 

# do queries here (DEADLY INSECURE)
SUMMARYSTR=`. $QUERYFILE` #queries return a string of items of the form "name:value"

NUMPARAMS=`getnumparams $NETWORKFILE`
SUMMARYSTR="$SUMMARYSTR __ ParameterCount: $NUMPARAMS" #put key:value pairs into a string for parsing, separate entries by **

STABLEFCLIST="$DATABASEDIR/StableFCList$NETWORKID.txt" # this file name should match the one in querylibrary.sh by convention

# if pattern matching desired (pattern dir non-empty), then do it
if [[ `ls -A $PATTERNDIR` ]]; then
	
	# check if stable FC list calculated
	if [ ! -f $STABLEFCLIST ]; then
		getstableFClist
		SUMMARYSTR="$SUMMARYSTR __ StableFCParameterCount:$(summarystableFCs)"
	fi

	# pattern match in stable FCs
	for PATTERNFILE in $PATTERNDIR/$NETWORKID/*; do
		P=`basename $PATTERNFILE | sed 's/[^0-9_]*//g'` #patterns must have unique numbers
		NUM=$NETWORKID"_"$P 
		MATCHFILE=$DATABASEDIR/Matches$NUM.txt
		mpiexec -np $NSLOTS $PATTERNMATCH $NETWORKFILE $PATTERNFILE $STABLEFCLIST $MATCHFILE > /dev/null
		MATCHES=`getcountuniquelines_space $MATCHFILE`

		# dump inputs and results to json
		RESULTSFILE=$RESULTSDIR/results$NUM.txt
		python pythonmodules/summaryJSON.py $NETWORKFILE $PATTERNFILE $RESULTSFILE "$SUMMARYSTR" $MATCHES

		# rm $PATTERNFILE $MATCHFILE
	done
else
	RESULTSFILE=$RESULTSDIR/results$NETWORKID.txt
	python pythonmodules/summaryJSON.py $NETWORKFILE "" $RESULTSFILE "$SUMMARYSTR" ""
fi

# delete intermediate files
if  [  $RMNF == "True" ]; then 
	rm $NETWORKFILE 
fi 
if  [  $RMDB == "True" ]; then 
	rm $DATABASEFILE
	if [ -f $STABLEFCLIST ]; then
		rm $STABLEFCLIST
	fi
fi 

