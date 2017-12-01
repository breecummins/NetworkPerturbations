import intervalgraph as ig
import itertools


def GrowComponent(ts,epsilon,comp):
    # Grows epsilon components for a given time t. It does this by simultaneously checking both neighboring points,
    # if they exist, and only adding them if they intersect time t and all other times in the component, as well as
    # intersecting each other.

    def BoolIntersect(t1,t2):
        # Checks to see if the epsilon nbhd of value of t2 intersects the epsilon nbhd of value of t2
        if ts[t2] - ts[t1] <= 2*epsilon and ts[t2] - ts[t1] >= -2*epsilon:
            return True
        else:
            return False

    def isgoodcandidate(candidate,comp):
        for time in comp:
            if not BoolIntersect(candidate,time):
                return False
        return True

    def growleft(comp):
        # Proceed to check interval overlap to the left of the component only
        candidate = comp[0] - 1
        while candidate > -1:
            if not isgoodcandidate(candidate,comp):
                return comp
            comp.insert(0, candidate)
            candidate -= 1
        return comp

    def growright(comp):
        # Proceed to check interval overlap to the right of the component only
        candidate = comp[-1] + 1
        N = len(ts)
        while candidate < N:
            if not isgoodcandidate(candidate,comp):
                return comp
            comp.append(candidate)
            candidate += 1
        return comp

    t_beg = comp[0]
    t_end = comp[-1]
    N = len(ts)

    if t_beg == 0:
        return growright(comp)
    elif t_end == N-1:
        return growleft(comp)
    else:
        candidate_beg = t_beg-1
        candidate_end = t_end+1

        while True:
            beg_good = isgoodcandidate(candidate_beg,comp)
            end_good = isgoodcandidate(candidate_end,comp)
            if (not beg_good) and (not end_good):
                return comp
            elif beg_good and (not end_good):
                comp.insert(0, candidate_beg)
                return growleft(comp)
            elif (not beg_good) and end_good:
                comp.append(candidate_end)
                return growright(comp)
            else:
                if not BoolIntersect(candidate_beg,candidate_end):
                    return comp
                else:
                    comp.insert(0,candidate_beg)
                    comp.append(candidate_end)
                    candidate_beg -= 1
                    candidate_end += 1
                    if candidate_beg == -1:
                        if candidate_end < N:
                            return growright(comp)
                        else:
                            return comp
                    elif candidate_end == N:
                        return growleft(comp)
                    else:
                        continue

def BuildEIList(ts,step):
    # Build epsilon indexed list whose entries are lists of components generated at that epsilon
    # Inputs: ts = time series, step = user defined parameter that specifies the increase in epsilon
    # Outputs: eiList = epsilon indexed list
    m,M = min(ts),max(ts)
    nts = [ float(t - m)/(M-m) for t in ts ]
    compList=[[t] for t in range(len(nts))] # compList at epsilon=0
    eiList = [ [[t] for t in range(len(nts))] ] # need a deep copy of compList -- faster to reconstruct
    epsilon = step
    while epsilon <= 0.55:
        compList = [ GrowComponent(nts,epsilon,comp) for comp in compList ] # grow compList from previous calculation
        eiList.append([list(comp) for comp in compList]) # want snapshots of compList at each epsilon, so copy internal lists
        epsilon += step
    return eiList

def MinMaxLabel(eiList,ts):
    # Sorts the unique components grown into two lists, minList and maxList
    # Inputs: eiList, ts
    # Outputs: minList = list containing all components that are minima, maxList = similar

    # flatten eiList
    flat_ei = list(itertools.chain.from_iterable(eiList))
    # get unique elements while preserving order on the flattened eiList
    # (note we throw away duplicates at the beginning of the list)
    compList = [item for k,item in enumerate(flat_ei) if item not in flat_ei[k+1:]]
    minList = []
    maxList = []
    for comp in compList:
        if 0 in comp:
            if not(len(ts)-1 in comp):
                if ts[comp[-1]+1] > ts[comp[-1]]:
                    minList.append(comp)
                else:
                    maxList.append(comp)
        elif len(ts)-1 in comp:
            if not(0 in comp):
                if ts[comp[0]-1] > ts[comp[0]]:
                    minList.append(comp)
                else:
                    maxList.append(comp)
        else:
            if (ts[comp[0]-1] > ts[comp[0]]) and (ts[comp[-1]+1] > ts[comp[-1]]):
                minList.append(comp)
            if (ts[comp[0]-1] < ts[comp[0]]) and (ts[comp[-1]+1] < ts[comp[-1]]):
                maxList.append(comp)
    return minList,maxList

# Return component-chain list indexed by time and a labeled(min/max/n/a) chain list
# Creates list indexed by time where each entry is an epsilon indexed list of components grown at that
# time. This is called chainList. Then I assign each component a label, 'min'/'max'/'n/a' and record
# this as labeledChains.
def BuildChains(eiList,ts,step):
    minList,maxList = MinMaxLabel(eiList,ts)
    chainList = []
    labeledChains = []
    for i in range(0,len(eiList[0])):
        chainList.append([])
        labeledChains.append([])
    for list in eiList:
        ndx = 0
        for item in list:
            chainList[ndx].append(item)
            if item in minList:
                labeledChains[ndx].append('min')
            elif item in maxList:
                labeledChains[ndx].append('max')
            else:
                labeledChains[ndx].append('n/a')
            ndx+=1
    return chainList,labeledChains

# Count number of epsilon steps that mins/maxes persisted and return list of min/max lifetimes.
# Note, only considers those that are local mins/maxes at epsilon = 0. 
# Outputs: minLife = time indexed list initialized to all 0's, time's entry is # of consecutive 
# epsilon steps that time was a min, maxLife = similar
def EpsLife(labeledChains):
    minLife = [0] * len(labeledChains)
    maxLife = [0] * len(labeledChains)
    for t in range(0,len(labeledChains)):
        if labeledChains[t][0] == 'min':
            s = 0
            while labeledChains[t][s] == labeledChains[t][0]:
                minLife[t] += 1
                s+=1
        elif labeledChains[t][0] == 'max':
            s = 0
            while labeledChains[t][s] == labeledChains[t][0]:
                maxLife[t] += 1
                s+=1
    return minLife,maxLife

# Extract the n deepest lifetime mins and maxes. If there are ties, the sequentially first one is chosen
# return list of 2n events, ordered by highest min, highest max, second highest min, ...
def DeepLife(minLife,maxLife,ts,n):
    minLifeCopy = list(minLife)
    maxLifeCopy = list(maxLife)
    deepEventList = []
    for ndx in range(0,n):
        minimum = max(minLifeCopy)
        maximum = max(maxLifeCopy)
        if minLifeCopy.count(minimum) == 1:
            #same stuff as before
            minIndex = minLifeCopy.index(minimum)
        else:
            tmp = filter(lambda x : minLifeCopy[x] == minimum, range(len(minLifeCopy)))
            vals = [ ts[i] for i in tmp ]
            minIndex = tmp[vals.index(min(vals))]
        if maxLifeCopy.count(maximum) == 1:
            maxIndex = maxLifeCopy.index(maximum)
        else:
            tmp = filter(lambda x : maxLifeCopy[x] == maximum, range(len(maxLifeCopy)))
            vals = [ ts[i] for i in tmp ]
            maxIndex = tmp[vals.index(max(vals))]
        deepEventList.append(minIndex)
        deepEventList.append(maxIndex)
        minLifeCopy[minIndex] = 0
        maxLifeCopy[maxIndex] = 0
    return deepEventList

# Given a min and max, find the maximum epsilon step where their components are disjoint
def FindEps(eiList, deepEventList):
    value = 0
    epsilon = 0
    maxEps = -1
    while value == 0:
        for ndx1 in range(0,len(deepEventList)):
            for ndx2 in range(0,len(deepEventList)):
                if len(set(eiList[epsilon][deepEventList[ndx1]]).intersection(eiList[epsilon][deepEventList[ndx2]])) != 0 and ndx1 != ndx2:
                    value = 1
        if value == 0:
            maxEps = epsilon
        epsilon += 1
    return maxEps

# Process a list of time series and output a list of time series info. Each item in the list will correspond to time series
# and will be a list of the form [eiList, minTime, maxTime, eps]
# eiList = epsilon-indexed list of components, deepMin/MaxList = list of times of first n mins/maxes
# eps = highest step of epsilon at which the min component and max component are disjoint
def ProcessTS(tsList, n, step):
    sumList = []
    for ts in tsList:
        eiList = BuildEIList(ts,step)
        chainList, labeledChains = BuildChains(eiList,ts,step)
        minLife,maxLife = EpsLife(labeledChains)
        deepEventList = DeepLife(minLife,maxLife,ts,n)
        eps = FindEps(eiList,deepEventList)
        sumList.append([eiList,deepEventList,eps])
    return sumList

# Find the minimum value of eps such that min/max interval of every time series being processed
# is disjoint. So take min of all eps
def FindMaxEps(sumList):
    epsilon = sumList[0][2]
    for ts in sumList:
        if ts[2] < epsilon:
            epsilon = ts[2]
    return epsilon

# For each ts, pull min/max components for each step up to eps indexed by ts
# then highest min, highest max, second highest min, ...
def PullEventComps(sumList,maxEps,step,n):
    eventCompList = []
    ndx = 0
    for tsList in sumList:
        eventCompList.append([])
        for event in range(0,2*n):
            eventCompList[ndx].append(tsList[0][maxEps][tsList[1][event]])
        ndx += 1
    return eventCompList

# Build partial order list indexed by epsilon. Each PO is a list indexed by 1st ts highest min, 1st ts highest max, 
# 1st ts second highest min, 1st ts second highst max, ..., last ts nth highest min, last ts nth highest max
# Each entry is a list of all mins/maxes that occur before the given min/max. 
def BuildPO(eventCompList,step,n):
    PO = []
    for ts in range(0,len(eventCompList)):
        for event in range(0,2*n):
            PO.append([])
            for ndx in range(0,len(eventCompList)):
                for ndx1 in range(0,2*n):
                    fixed = eventCompList[ts][event]
                    checker = eventCompList[ndx][ndx1]
                    intSize = len(set(fixed).intersection(checker))
                    if intSize == 0:
                        if fixed[0] < checker[0]:
                            PO[2*n*ts + event].append(2*n*ndx + ndx1)
    return PO

# Convert PO's to graph class
def POToGraph(PO,TSLabels,n):
    G = ig.Graph()
    for value in range(0,len(PO)):
        G.add_vertex(value,TSLabels[value/(2*n)])
    for i in range(0,len(PO)):
        for j in PO[i]:
            G.add_edge(i,j)
    G = G.transitive_reduction()
    return G

# Convert graphs to digraphs
def GraphToDigraph(G):
    DG = Digraph(comment = 'PO')
    for v in G.vertices():
        DG.node(str(v),G.vertex_label(v))
    for e in G.edges():
        DG.edge(str(e[0]),str(e[1]))
    DG.render('graph.gv',view=True)

# Labeling function for the genes
def CreateLabel(sumList):
    d = len(sumList)
    label = [0]*(2*d)
    for ndx in range(0,d):
        lastEvent = max(sumList[ndx][1])
        indexOfLE = sumList[ndx][1].index(lastEvent)
        if indexOfLE%2 == 1:   # last event was max, since ordered min,max,min,max,...
            label[2*d - 1 - ndx] = 1
            label[d - 1 - ndx] = 0
        else:
            label[2*d - 1 - ndx] = 0
            label[d - 1 - ndx] = 1
    label = '0b' + ''.join([str(x) for x in label])	#Cast to binary
    label = int(label,2)
    return label

# Create JSON string for each graph
def ConvertToJSON(graph,sumList,TSLabels):
    G = graph
    output = {}
    output["poset"] = [ list(G.adjacencies(i)) for i in G.vertices() ]
    output["events"] = [ TSLabels.index(G.vertex_label(i)) for i in G.vertices() ]
    output["label"] = CreateLabel(sumList)
    output["dimension"] = len(TSLabels)
    return output

def makeJSONstring(TSList,TSLabels,n=1,scalingFactors=[1],step=0.01):
    # TSList is a list of time series, each of which is a list of floats
    # Each time series has a label in the corresponding index of TSLabels
    # n = number of mins/maxes to pull
    # scalingFactors = a list of scaling factors of maxEps (Must be in [0,1])
    # step (default to 0.01)
    if step <=0:
        print "Changing step size to 0.01."
        step = 0.01

    sumList = ProcessTS(TSList,n,step)

    maxEps = FindMaxEps(sumList)
    jsonstrs = []
    for sf in scalingFactors:
        scaledMaxEps = int(sf*maxEps)
        eventCompList = PullEventComps(sumList,scaledMaxEps,step,n)
        PO = BuildPO(eventCompList,step,n)
        graph = POToGraph(PO,TSLabels,n)
        jsonstrs.append(ConvertToJSON(graph,sumList,TSLabels))
    return jsonstrs

def testme():
    import fileparsers
    import matplotlib.pyplot as plt
    TSList,TSLabels,timeStepList = fileparsers.parseTimeSeriesFileRow('/Users/bcummins/ProjectData/malaria/2017/results_Sample08_mal_timeseries.tsv')
    # desiredlabels = ['PVP01_0000070','PVP01_0000080','PVP01_0000090','PVP01_0000100','PVP01_0000110','PVP01_0000120']
    desiredlabels = ['PVP01_0000070','PVP01_0000080']
    ind = timeStepList.index(45)
    labels,data = zip(*[(node,TSList[TSLabels.index(node)][:ind+1]) for node in TSLabels if node in desiredlabels])
    jsonstr = makeJSONstring(data,labels,n=1,scalingFactors=[0.05,0.1,0.5],step=0.01)
    print jsonstr
    ts=timeStepList[:ind+1]
    plt.figure()
    plt.hold('on')
    for d in data:
        m,M = min(d),max(d)
        nd = [ float(t - m)/(M-m) for t in d ]
        plt.plot(ts,nd)
    plt.legend(desiredlabels)
    plt.show()

def malaria1():
    import fileparsers, glob
    import matplotlib.pyplot as plt
    gvstr_base = 'digraph {\n0[label="70 min"];\n1[label="70 max"];\n2[label="80 min"];\n3[label="80 max"];\n'
    for f in glob.glob('/Users/bcummins/ProjectData/malaria/2017/results_Sample*mal_timeseries.tsv'):
        pltname = "/Users/bcummins/ProjectData/malaria/2017/pictures/" + f[-27:-18] + "_70_80.pdf"
        gvnames = ["/Users/bcummins/ProjectData/malaria/2017/pictures/" + f[-27:-18] + "_70_80_"+ c +".gv" for c in ["e05","e10","e50"]]
        TSList,TSLabels,timeStepList = fileparsers.parseTimeSeriesFileRow(f)
        # desiredlabels = ['PVP01_0000070','PVP01_0000080','PVP01_0000090','PVP01_0000100','PVP01_0000110','PVP01_0000120']
        desiredlabels = ['PVP01_0000070','PVP01_0000080']
        ind = timeStepList.index(45)
        labels,data = zip(*[(node,TSList[TSLabels.index(node)][:ind+1]) for node in TSLabels if node in desiredlabels])
        jsonstr = makeJSONstring(data,labels,n=1,scalingFactors=[0.05,0.1,0.5],step=0.01)
        for obj in jsonstr:
            poset = obj["poset"]
            gvstr = gvstr_base
            for k,l in enumerate(poset):
                if not l:
                    pass
                else:
                    for e in l:
                        gvstr += str(k) + " -> " + str(e) + ";\n"
            gvstr += "}"
            gvf = gvnames.pop(0)
            with open(gvf,"w") as gvfobj:
                gvfobj.write(gvstr)
        ts=timeStepList[:ind+1]
        plt.figure()
        plt.hold('on')
        for d in data:
            m,M = min(d),max(d)
            nd = [ float(t - m)/(M-m) for t in d ]
            plt.plot(ts,nd)
        plt.legend(desiredlabels)
        plt.savefig(pltname)


def malaria2():
    import fileparsers, glob
    import matplotlib.pyplot as plt
    gvstr_base = 'digraph {\n0[label="0809100 min"];\n1[label="0809100 max"];\n2[label="0902100 min"];\n3[label="0902100 max"];\n4[label="0000110 min"];\n5[label="0000110 max"];\n6[label="0727100 min"];\n7[label="0727100 max"];\n8[label="1114000 min"];\n9[label="1114000 max"];\n10[label="0309700 min"];\n11[label="0309700 max"];\n12[label="0416100 min"];\n13[label="0416100 max"];\n14[label="1343400 min"];\n15[label="1343400 max"];\n16[label="0721000 min"];\n17[label="0721000 max"];\n18[label="1449900 min"];\n19[label="1449900 max"];\n20[label="1030100 min"];\n21[label="1030100 max"];\n22[label="1108800 min"];\n23[label="1108800 max"];\n24[label="0531500 min"];\n25[label="0531500 max"];\n26[label="1011500 min"];\n27[label="1011500 max"];\n'
    for f in glob.glob('/Users/bcummins/ProjectData/malaria/2017/results_Sample*mal_timeseries.tsv'):
        pltname = "/Users/bcummins/ProjectData/malaria/2017/pictures/" + f[-27:-18] + "_14genes.pdf"
        gvnames = ["/Users/bcummins/ProjectData/malaria/2017/pictures/" + f[-27:-18] + "_14genes_e05.gv"]
        TSList,TSLabels,timeStepList = fileparsers.parseTimeSeriesFileRow(f)
        # desiredlabels = ['PVP01_0000070','PVP01_0000080','PVP01_0000090','PVP01_0000100','PVP01_0000110','PVP01_0000120']
        desiredlabels = ['PVP01_0809100','PVP01_0902100','PVP01_0000110','PVP01_0727100','PVP01_1114000','PVP01_0309700','PVP01_0416100','PVP01_1343400','PVP01_0721000','PVP01_1449900','PVP01_1030100','PVP01_1108800','PVP01_0531500','PVP01_1011500']
        ind = timeStepList.index(45)
        labels,data = zip(*[(node,TSList[TSLabels.index(node)][:ind+1]) for node in TSLabels if node in desiredlabels])
        jsonstr = makeJSONstring(data,labels,n=1,scalingFactors=[0.05],step=0.01)
        for obj in jsonstr:
            poset = obj["poset"]
            gvstr = gvstr_base
            for k,l in enumerate(poset):
                if not l:
                    pass
                else:
                    for e in l:
                        gvstr += str(k) + " -> " + str(e) + ";\n"
            gvstr += "}"
            gvf = gvnames.pop(0)
            with open(gvf,"w") as gvfobj:
                gvfobj.write(gvstr)
        ts=timeStepList[:ind+1]
        plt.figure()
        plt.hold('on')
        for d in data:
            m,M = min(d),max(d)
            nd = [ float(t - m)/(M-m) for t in d ]
            plt.plot(ts,nd)
        plt.legend(desiredlabels,loc='center left', bbox_to_anchor=(1, 0.5))
        plt.savefig(pltname)

def malaria3():
    import fileparsers, glob
    import matplotlib.pyplot as plt
    gvstr_base = 'digraph {\n0[label="9100 min"];\n1[label="9100 max"];\n2[label="9700 min"];\n3[label="9700 max"];\n4[label="1500 min"];\n5[label="1500 max"];\n'
    for f in glob.glob('/Users/bcummins/ProjectData/malaria/2017/results_Sample*mal_timeseries.tsv'):
        pltname = "/Users/bcummins/ProjectData/malaria/2017/pictures/" + f[-27:-18] + "_9100_9700_1500.pdf"
        gvnames = ["/Users/bcummins/ProjectData/malaria/2017/pictures/" + f[-27:-18] + "_9100_9700_1500"+ c +".gv" for c in ["e05","e10","e50"]]
        desiredlabels = ['PVP01_0809100','PVP01_0309700','PVP01_0531500']
        TSList,TSLabels,timeStepList = fileparsers.parseTimeSeriesFileRow(f)
        ind = timeStepList.index(45)
        labels,data = zip(*[(node,TSList[TSLabels.index(node)][:ind+1]) for node in TSLabels if node in desiredlabels])
        jsonstr = makeJSONstring(data,labels,n=1,scalingFactors=[0.05,0.1,0.5],step=0.01)
        for obj in jsonstr:
            poset = obj["poset"]
            gvstr = gvstr_base
            for k,l in enumerate(poset):
                if not l:
                    pass
                else:
                    for e in l:
                        gvstr += str(k) + " -> " + str(e) + ";\n"
            gvstr += "}"
            gvf = gvnames.pop(0)
            with open(gvf,"w") as gvfobj:
                gvfobj.write(gvstr)
        ts=timeStepList[:ind+1]
        plt.figure()
        plt.hold('on')
        for d in data:
            m,M = min(d),max(d)
            nd = [ float(t - m)/(M-m) for t in d ]
            plt.plot(ts,nd)
        plt.legend(desiredlabels)
        plt.savefig(pltname)

def malaria4():
    import fileparsers, glob, json
    for f in glob.glob('/Users/bcummins/ProjectData/malaria/2017/results_Sample*mal_timeseries.tsv'):
        print(f)
        desiredlabels = ['PVP01_0809100','PVP01_0902100','PVP01_0000110','PVP01_0727100','PVP01_1114000','PVP01_0309700',
                         'PVP01_0416100','PVP01_1343400','PVP01_0721000','PVP01_1449900','PVP01_1030100','PVP01_1108800',
                         'PVP01_0531500','PVP01_1011500']
        TSList,TSLabels,timeStepList = fileparsers.parseTimeSeriesFileRow(f)
        ind = timeStepList.index(45)
        labels,data = zip(*[(node,TSList[TSLabels.index(node)][:ind+1]) for node in TSLabels if node in desiredlabels])
        jsonstr = makeJSONstring(data,labels,n=1,scalingFactors=[0.05],step=0.01)
        print(jsonstr[0])
        json.dump(jsonstr[0],open(f[-27:-18]+"posets_14vivax.json","w"))

if __name__ == "__main__":
    # testme()
    # malaria1()
    # malaria3()
    malaria4()



