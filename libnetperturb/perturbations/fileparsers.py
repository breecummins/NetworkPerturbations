def parseTimeSeriesFileCol(fname):
    ''' Parse time series file where each time series is in a column (spans all lines in the file).
    Returns the time series data, the gene label for each series, and the list of times at which the data was taken.
    File format must be:
    1) optional comment lines beginning with #
    2) a line of space-separated gene labels, except for the first element which is a non-gene column header like 'time'
    3) each subsequent line is in the space-separated form: time gene1(time) gene2(time) ...

    '''
    with open(fname,'r') as f:
        value = 0                                              
        for line in f:
            if line:
                if line[0] == '#':
                    continue
                elif value == 1:
                    times = line.split()
                    timeStepList.append(float(times[0]))
                    for ndx in range(1,len(times)):
                        TSData[ndx].append(float(times[ndx]))
                else: # the clause below happens only once at the first non-comment line
                    value = 1
                    TSData = []
                    TSLabels = []
                    timeStepList = []
                    genes = line.split()
                    for ndx in range(1,len(genes)):
                        TSData.append([])
                        TSLabels.append(genes[ndx])
    return TSData,TSLabels,timeStepList

def parseTimeSeriesFileRow(fname):
    ''' Parse time series file where each time series is in a row (single line in the file).
    Returns the time series data, the gene label for each series, and the list of times at which the data was taken.
    File format must be:
    1) optional comment lines beginning with #
    2) a line of space-separated times, beginning with a row label like 'time'
    3) each subsequent line is in the space-separated form: gene_name data(time1) data(time2) ....

    '''
    with open(fname,'r') as f:
        TSList = []
        TSLabels = []
        for line in f:
            if line:
                if line[0] == '#':
                    continue
                else:
                    data = line.split()
                    TSLabels.append(data[0])
                    TSList.append([float(item) for item in data[1:]])
    timeStepList = TSList[0]
    TSList = TSList[1:]
    TSLabels = TSLabels[1:]
    return TSList, TSLabels, timeStepList


def parseEdgeFile(fname):
    ''' Returns a list of (source, target, regulation) edges.
    File format must be:
    1) optional comment lines/column headers beginning with #
    2) data lines where the first column is an edge of the form TARGET_GENE = TYPE_REG(SOURCE_GENE)
    3) other columns in the line must be space, tab, or comma separated
    
    '''
    edgelist=[]
    with open(fname,'r') as f:
        for l in f.readlines():
            if l:
                if l[0] == '#':
                    continue
                wordlist=l.replace(',',' ').replace('=',' ').split()
                target=wordlist[0]
                regsource=wordlist[1].replace('(',' ').replace(')',' ').split()
                reg=regsource[0]
                source=regsource[1]
                edgelist.append((source,target,reg))
    return edgelist

def parseNodeFile(fname):
    ''' Returns a list of nodes from the file.
    File format must be: 
    1) optional comment lines/column headers beginning with # 
    2) data lines beginning with NODE_NAME
    3) other columns in the line must be space, tab, or comma separated
    
    '''
    nodelist = []
    with open(fname,'r') as f:
        for l in f.readlines():
            if l:
                if l[0] == '#':
                    continue
                wordlist=l.replace(',',' ').split()
                nodelist.append(wordlist[0])
    return nodelist
