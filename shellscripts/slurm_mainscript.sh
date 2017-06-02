#!/bin/bash

# analyze random networks

STARTINGFILE=$1 # network spec file: /Users/bcummins/GIT/DSGRN/networks/5D_2016_02_08_cancer_withRP_essential.txt
NUMNETWORKS=$2 # number of networks: 10000
MAXNODES=$3 # max number of nodes to allow (it is possible to choose too few nodes so that networks can never finish generating)
MAXPARAMS=$4 # max number of parameters per network to allow (networks might not finish generating if this is too small)
DSGRN=$5 #/Users/bcummins/GIT/DSGRN

SIGNATURES=$DSGRN/software/Signatures/bin/Signatures
SCRATCH=/scratch/sharker
DATETIME=`date +%Y_%m_%d_%H_%M_%S`
INPUTDIR=$SCRATCH/random_networks$DATETIME
DATABASEDIR=$SCRATCH/random_databases$DATETIME
OUTPUTDIR=$SCRATCH/random_outputfiles$DATETIME

mkdir -p $DATABASEDIR/ $OUTPUTDIR/ $INPUTDIR/

python ./random_networkbuilder.py $STARTINGFILE $NUMNETWORKS "$INPUTDIR/network_" $MAXNODES $MAXPARAMS

# use xargs below since the number of files can be large
for NETWORK in $( echo $INPUTDIR/* | xargs ls ); do
	NUM=$(echo `basename $NETWORK` | sed -e s/[^0-9]//g);
	DATABASENAME="$DATABASEDIR/database$NUM.db";
	echo "Network: $NETWORK"
	#/home/sharker/work/bin/dsgrn network $NETWORK parameter
	sbatch slurm_helperscript.sh $SIGNATURES $NETWORK $DATABASENAME $OUTPUTDIR $NUM
done
