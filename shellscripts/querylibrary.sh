getnumparams() { dsgrn network $1 parameter | sed 's/[^0-9]*\([0-9]*\)[^0-9]*/\1/g'; }
getcountuniquelines() { cut -d " " -f 1 $1 | sort | uniq | wc -w; } # count unique parameters in file list (input is file path)
getcountfromfile() { cat $1 | tr -d "\n"; } # pull count number out of file (input is file path)

getstableFClist() { sqlite3 -separator " " $DATABASEFILE 'select ParameterIndex, Vertex from Signatures natural join (select MorseGraphIndex,Vertex from (select MorseGraphIndex,Vertex from MorseGraphAnnotations where Label="FC" except select MorseGraphIndex,Source from MorseGraphEdges));' > $DATABASEDIR/StableFCList$NETID.txt; } # dbname, outputfile

summarystableFCs() { getcountuniquelines $DATABASEDIR/StableFCList$NETID.txt; } # do not delete file -- need for pattern matching

getmultistabilitylist() { sqlite3 -separator " " $DATABASEFILE 'select count(*) from Signatures natural join (select MorseGraphIndex from (select MorseGraphIndex, count(*) as numMinimal from (select MorseGraphIndex,Vertex from MorseGraphVertices except select MorseGraphIndex,Source from MorseGraphEdges) group by MorseGraphIndex) where numMinimal > 1);'  > $DATABASEDIR/Multistability$NETID.txt; } # dbname, outputfile

summarymultistability() { getcountfromfile $DATABASEDIR/Multistability$NETID.txt; rm $DATABASEDIR/Multistability$NETID.txt; }

makeFPquery() { $FPQUERY $DATABASEFILE $1 > $DATABASEDIR/FPresult$NETID.txt; } # FPQUERY DBNAME SPECIFIC_FP > OUTPUTFILE

summaryFP() { getcountuniquelines $DATABASEDIR/FPresult$NETID.txt; rm $DATABASEDIR/FPresult$NETID.txt; }

