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
if [ ! -f $DATABASEFILE ]; then echo "Database $NETWORKID did not compute\n"; cat $2; exit 1; fi 

# do queries here
NUMPARAMS=`getnumparams $NETWORKFILE`

# QUERIES is a list of elements (key, query_cmd, query_arg, summary_cmd)
# the query command searches the database, and the summary command collapses the data into a statistic
# the key is the dictionary key for the summary statistic as it will be stored in the results file
# use associative array -- need bash 4
SUMMARY=()
for Q in ${QUERIES[@]}; do
	KEY=${Q[1]}
	`${Q[2]} ${Q[3]}`
	VAL=`${Q[4]}`
	SUMMARY+=(($KEY,$VAL))
done

STABLEFCLIST="$DATABASEDIR/StableFCList$NETID.txt"

# if pattern matching desired, then do it
if [[ -d $PATTERNDIR ]]; then
	
	# check if stable FC list calculated
	if [ ! -f $STABLEFCLIST ]; then
		getstableFClist
	fi

	# pattern match in stable FCs
	for PATTERNFILE in $( echo $PATTERNDIR/$NETID/* | xargs ls ); do
		P=`basename $PATTERNFILE`
		NUM="$NETID${P##pattern}" # get everything after "pattern" in the file name (get the scaling factor)
		NUM=${NUM%%.*} # get everything before the file extension to make a unique identifier
		MATCHFILE=$DATABASEDIR/Matches$NUM.txt
		mpiexec --mca mpi_preconnect_mpi 1 -np $NSLOTS -x LD_LIBRARY_PATH $PATTERNMATCH $NETWORKFILE $PATTERNFILE $STABLEFCLIST $MATCHFILE > /dev/null
		MATCHES=`getcountuniquelines $MATCHFILE`
		# note: grep -o "[0-9]*" appears to be buggy on Mac OS X, hence the more complex sed expression instead

		# dump inputs and results to json -- need general file that takes a list of key, value pairs
		python summaryJSON.py $2 $5 $MATCHES $STABLEFCS $MULTISTABLE $NODES $7

		rm $PATTERNFILE $MATCHFILE
	done
fi

# delete intermediate files; it is possible that $STABLEFCLIST does not exist
rm $NETWORKFILE $DATABASEFILE 
rm $STABLEFCLIST



