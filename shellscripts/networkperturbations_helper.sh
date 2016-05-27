#!/bin/bash

# dependencies: dsgrn, bash 4

. querylibrary.sh # import custom functions

#Active comments for SGE
#$ -V
#$ -cwd
#$ -j y
#$ -S /bin/bash
#$ -pe orte 8

# helper script for constructing and analyzing network perturbations


DSGRN=$1
SIGNATURES="$DSGRN/software/Signatures/bin/Signatures"
PATTERNMATCH="$DSGRN/software/PatternMatch/bin/PatternMatchDatabase"
FPQUERY="$DSGRN/software/FPQuery/FPQuery"

NETWORKFILE=$2
PATTERNDIR=$3 
DATABASEDIR=$4 
RESULTSDIR=$5 
NETWORKID=$6
QUERIES=$7

DATABASEFILE="$DATABASEDIR/database$NETWORKID.db"

# make database
mpiexec --mca mpi_preconnect_mpi 1 -np $NSLOTS -x LD_LIBRARY_PATH $SIGNATURES $NETWORKFILE DATABASEFILE

# if making the database fails, then quit
if [ ! -f $3 ]; then echo "Database $NETWORKID did not compute\n"; cat $2; exit 1; fi 

# do queries here
NUMPARAMS=`getnumparams $NETWORKFILE`

# QUERIES is a list of elements (key, query_cmd, (arg1,...,argn), summary_cmd (arg1,..,argm))
# use associative array -- need bash 4
SUMMARY=()
for Q in ${QUERIES[@]}; do
	KEY=${Q[1]}
	CMD=${Q[2]}
	ARGS=${Q[3]}
	`CMD ${ARGS[@]}`
	CMD=${Q[4]}
	ARGS=${Q[5]}
	VAL=`CMD ${ARGS[@]}`
	SUMMARY+=(($KEY,$VAL))


# make StableFClist -- only want to do this if some condition is met -- either pattern matching or # stable FCs is desired
# may need to make this an input argument
STABLEFCLIST="$DATABASEDIR/StableFCList$NETID.txt"
getstableFClist $DATABASEFILE $STABLEFCLIST  
STABLEFCS=`getcountuniquelines $STABLEFCLIST`
# MULTISTABLE=`getcountfromfile $MULISTABLEFILE`
# rm $MULTISTABLEFILE

# save results here if there is no pattern matching to do

rm $DATABASEFILE

# pattern match in stable FCs -- if condition is met
for PATTERNFILE in $( echo $PATTERNDIR/$NETID/* | xargs ls ); do
	P=`basename $PATTERNFILE`
	NUM="$NETID${P##pattern}"
	NUM=${NUM%%.*}
	MATCHFILE=$DATABASEDIR/Matches$NUM.txt
	mpiexec --mca mpi_preconnect_mpi 1 -np $NSLOTS -x LD_LIBRARY_PATH $PATTERNMATCH $NETWORKFILE $PATTERNFILE $STABLEFCLIST $MATCHFILE > /dev/null
	MATCHES=`getcountuniquelines $MATCHFILE`
	# note: grep -o "[0-9]*" appears to be buggy on Mac OS X, hence the more complex sed expression instead

	# dump inputs and results to json -- need general file that takes a list of key, value pairs
	python summaryJSON.py $2 $5 $MATCHES $STABLEFCS $MULTISTABLE $NODES $7

	rm $PATTERNFILE $MATCHFILE
done

# delete intermediate files
rm $NETWORKFILE $STABLEFCLIST

