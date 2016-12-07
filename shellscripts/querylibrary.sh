getnumparams() { dsgrn network $NETWORKFILE parameter | sed 's/[^0-9]*\([0-9]*\)[^0-9]*/\1/g'; } # input is network file
getcountuniquelines() { cut -d "|" -f 1 $1 | sort | uniq | wc -w; } # count unique parameters in file list where format is param|morse_set (input is file path)
getcountuniquelines_space() { cut -d " " -f 1 $1 | sort | uniq | wc -w; } # count unique parameters in file list where format is param morse_set (input is file path)
getcountfromfile() { cat $1 | tr -d "\n"; } # pull line count number out of file (input is file path)

getstableFClist() { sqlite3 -separator " " $DATABASEFILE 'select ParameterIndex, Vertex from Signatures natural join (select MorseGraphIndex,Vertex from (select MorseGraphIndex,Vertex from MorseGraphAnnotations where Label="FC" except select MorseGraphIndex,Source from MorseGraphEdges));' > $DATABASEDIR/StableFCList$NETWORKID.txt; } # dbname, outputfile

summarystableFCs() { getcountuniquelines_space $DATABASEDIR/StableFCList$NETWORKID.txt; } # do not delete file -- need for pattern matching

getmultistabilitylist() { sqlite3 -separator " " $DATABASEFILE 'select count(*) from Signatures natural join (select MorseGraphIndex from (select MorseGraphIndex, count(*) as numMinimal from (select MorseGraphIndex,Vertex from MorseGraphVertices except select MorseGraphIndex,Source from MorseGraphEdges) group by MorseGraphIndex) where numMinimal > 1);'  > $DATABASEDIR/Multistability$NETWORKID.txt; } # dbname

summarymultistability() { getcountfromfile $DATABASEDIR/Multistability$NETWORKID.txt; rm $DATABASEDIR/Multistability$NETWORKID.txt; }

# makeFPquery() { $FPQUERY $DATABASEFILE $1 > $DATABASEDIR/FPresult$NETWORKID.txt; } # FPQUERY DBNAME SPECIFIC_FP > OUTPUTFILE

# summaryFP() { getcountuniquelines $DATABASEDIR/FPresult$NETWORKID.txt; rm $DATABASEDIR/FPresult$NETWORKID.txt; }


