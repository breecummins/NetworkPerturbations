getstableFClist() { sqlite3 -separator " " $1 'select ParameterIndex, Vertex from Signatures natural join (select MorseGraphIndex,Vertex from (select MorseGraphIndex,Vertex from MorseGraphAnnotations where Label="FC" except select MorseGraphIndex,Source from MorseGraphEdges));' > $2; } # dbname, outputfile

getmultistabilitylist() { sqlite3 -separator " " $1 'select count(*) from Signatures natural join (select MorseGraphIndex from (select MorseGraphIndex, count(*) as numMinimal from (select MorseGraphIndex,Vertex from MorseGraphVertices except select MorseGraphIndex,Source from MorseGraphEdges) group by MorseGraphIndex) where numMinimal > 1);'  > $2; } # dbname, outputfile

makeFPquery() { $1 $2 $3 > $4; } # FPQUERY DBNAME VARSTR > OUTPUTFILE

getnumparams() { dsgrn network $1 parameter | sed 's/[^0-9]*\([0-9]*\)[^0-9]*/\1/g'; }
getcountuniquelines() { cut -d " " -f 1 $1 | sort | uniq | wc -w; } # count unique parameters in file list (input is file path)
getcountfromfile() { cat $1 | tr -d "\n"; } # pull count number out of file (input is file path)


