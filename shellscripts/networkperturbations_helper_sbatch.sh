#!/bin/bash
#SBATCH -n 8                 # One task
#SBATCH -c 1                 # One cpu per task
#SBATCH -N 1                 # Minimum one node
#SBATCH -t 0-10:05           # Runtime in D-HH:MM
#SBATCH -p main              # Partition to submit to
#SBATCH --mem-per-cpu=4000   # Memory pool for all cores (see also --mem-per-cpu)

# dependencies: dsgrn in path, DSGRN dependencies, bash 4, mpiexec, python 2.7, qsub, sqlite3

. shellscripts/querylibrary.sh # import custom functions

DSGRN=$1
SIGNATURES="$DSGRN/software/Signatures/bin/Signatures"
PATTERNMATCH="$DSGRN/software/PatternMatch/bin/PatternMatchDatabase"
FPQUERY="$DSGRN/software/FPQuery/FPQuery"

NETWORKFILE=$2
PATTERNDIR=$3 
DATABASEDIR=$4 
RESULTSDIR=$5 
NETWORKID=$6
QUERYFILE=$7

DATABASEFILE="$DATABASEDIR/database$NETWORKID.db"

# make database
mpiexec $SIGNATURES $NETWORKFILE $DATABASEFILE

# if making the database fails, then quit
if [ ! -f $DATABASEFILE ]; then echo "Database $NETWORKID did not compute\n"; cat $2; exit 1; fi 

# do queries here (DEADLY INSECURE)
SUMMARYSTR=`. $QUERYFILE` #queries return a string of items of the form "name:value"
NUMPARAMS=`getnumparams $NETWORKFILE`
SUMMARYSTR="$SUMMARYSTR ParameterCount:$NUMPARAMS" #put key:value pairs into a string for parsing

STABLEFCLIST="$DATABASEDIR/StableFCList$NETWORKID.txt" # this file name should match the one in querylibrary.sh by convention

# if pattern matching desired (pattern dir non-empty), then do it
if [[ `ls -A $PATTERNDIR` ]]; then
	
	# check if stable FC list calculated
	if [ ! -f $STABLEFCLIST ]; then
		getstableFClist
		SUMMARYSTR="$SUMMARYSTR StableFCParameterCount:$(summarystableFCs)"
	fi

	# pattern match in stable FCs
	for PATTERNFILE in $PATTERNDIR/$NETWORKID/*; do
		P=`basename $PATTERNFILE`
		NUM="$NETWORKID${P##pattern}" # get everything after "pattern" in the file name (get the scaling factor); THIS REQUIRES STEREOTYPED NAMING CONVENTIONS
		NUM=${NUM%%.*} # get everything before the file extension to make a unique identifier
		MATCHFILE=$DATABASEDIR/Matches$NUM.txt
		mpiexec --mca mpi_preconnect_mpi 1 -np $NSLOTS -x LD_LIBRARY_PATH $PATTERNMATCH $NETWORKFILE $PATTERNFILE $STABLEFCLIST $MATCHFILE > /dev/null
		MATCHES=`getcountuniquelines $MATCHFILE`
		# note: grep -o "[0-9]*" appears to be buggy on Mac OS X, hence the more complex sed expression instead

		# dump inputs and results to json
		RESULTSFILE=$RESULTSDIR/results$NUM.txt
		python pythonmodules/summaryJSON.py $NETWORKFILE $PATTERNFILE $RESULTSFILE "$SUMMARYSTR" $MATCHES

		rm $PATTERNFILE $MATCHFILE
	done
else
	RESULTSFILE=$RESULTSDIR/results$NETWORKID.txt
	python pythonmodules/summaryJSON.py $NETWORKFILE "" $RESULTSFILE "$SUMMARYSTR" ""
fi

# delete intermediate files; it is possible that $STABLEFCLIST does not exist
rm $NETWORKFILE $DATABASEFILE 
rm $STABLEFCLIST



