#!/bin/bash
#SBATCH -n 8                 # One task
#SBATCH -c 1                 # One cpu per task
#SBATCH -N 1                 # Minimum one node
#SBATCH -t 0-10:05           # Runtime in D-HH:MM
#SBATCH -p main              # Partition to submit to
#SBATCH --mem-per-cpu=4000   # Memory pool for all cores (see also --mem-per-cpu)

# arg1 = path to Signatures
# arg2 = network file
# arg3 = database file
# arg4 = output directory
# arg5 = results number

# get unique identifier
NUM=$5

# print file name in case the job has to be aborted
echo "Starting $2."

# make database
mpiexec $1 $2 $3

# if making the database fails, then quit
if [ ! -f $3 ]; then echo "Database $NUM did not compute\n"; cat $2; exit 1; fi 

# otherwise, analyze
# search for stable FCs
sqlite3 -separator " " $3 'select ParameterIndex, Vertex from Signatures natural join (select MorseGraphIndex,Vertex from (select MorseGraphIndex,Vertex from MorseGraphAnnotations where Label="FC" except select MorseGraphIndex,Source from MorseGraphEdges));' > $4/StableFCList$NUM.txt

# search for multistability
sqlite3 -separator " " $3 'select count(*) from Signatures natural join (select MorseGraphIndex from (select MorseGraphIndex, count(*) as numMinimal from (select MorseGraphIndex,Vertex from MorseGraphVertices except select MorseGraphIndex,Source from MorseGraphEdges) group by MorseGraphIndex) where numMinimal > 1);'  > $4/MultistabilityList$NUM.txt

# yank summary results
MATCHES="-1"
STABLEFCS=`cut -d " " -f 1 $4/StableFCList$NUM.txt | sort | uniq | wc -w`
MULTISTABLE=`cat $4/MultistabilityList$NUM.txt`
NODES=`dsgrn network $2 parameter | sed 's/[^0-9]*\([0-9]*\)[^0-9]*/\1/g'`
# note: grep -o "[0-9]*" appears to be buggy on Mac OS X, hence the more complex sed expression instead

# dump inputs and results to json
echo "MATCHES = $MATCHES"
echo "STABLEFCS = $STABLEFCS"
echo "MULTISTABLE = $MULTISTABLE"
echo "NODES = $NODES"

python summaryJSON.py $2 "None" $MATCHES $STABLEFCS $MULTISTABLE $NODES "$4/results$NUM.json"

# delete intermediate files
rm $2 $3 "$4/StableFCList$NUM.txt" "$4/MultistabilityList$NUM.txt"
