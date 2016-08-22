import json
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.size'] = 24


def makeHistogram(data,nbins,extrapoints,xlabel,title,axislims):
    n, bins, patches = plt.hist(data, nbins, normed=0, facecolor='green', alpha=0.75)
    plt.hold('on')
    N=len(extrapoints)
    if N > 1:
        cm_subsection = [float(x)/(N-1) for x in range(N)]
        colors = [ mpl.cm.jet(x) for x in cm_subsection ]    
    else:
        colors = ['b']
    for c,pair in zip(colors,extrapoints):
        plt.plot(pair[0],pair[1],marker='*',markersize=24,color=c)
    plt.xlabel(xlabel)
    plt.ylabel('# networks')
    plt.title(title)
    plt.axis(axislims)
    plt.grid(True)
    plt.show()

def wavepool_network1_Dukediscussion_perturbations_5D_2016_08_02(fname='/Users/bcummins/ProjectSimulationResults/wavepool_networkperturbations_paper_data/5D_2016_08_02_wavepool_network1_Dukediscussion_results.json'):
    lod = json.load(open(fname,'r'))
    N = len(lod)
    notzeros=[ d for d in lod  if d['SingleFPQueryParameterCount']>0 ]
    percents=[ float(d['SingleFPQueryParameterCount'])/int(d['ParameterCount'])*100 for d in notzeros ]
    bestones=[ d for p,d in zip(percents,notzeros) if p > 40 ]
    extrapoints = [(float(lod[0]['SingleFPQueryParameterCount'])/int(lod[0]['ParameterCount']),100)]
    nounicode=dict()
    for item in d['SingleFPQuery'].iteritems():
        nounicode[str(item[0])] = item[1]
    xlabel = "SingleFPQuery: " + str(nounicode)
    title = "% parameters with FP query over {} networks with nonzero %".format(len(notzeros))
    axislims = [0,100,0,500]
    makeHistogram(percents,45,extrapoints,xlabel,title,axislims)
    print bestones

def wavepool_network1_Dukediscussion_perturbations_5D_2016_08_15(fname='/Users/bcummins/ProjectSimulationResults/wavepool_networkperturbations_paper_data/5D_2016_08_15_wavepool_network1_Dukediscussion_noregulationswap_results.json'):
    lod = json.load(open(fname,'r'))
    N = len(lod)
    notzeros=[ d for d in lod  if d['SingleFPQueryParameterCount']>0 ]
    percents=[ float(d['SingleFPQueryParameterCount'])/int(d['ParameterCount'])*100 for d in notzeros ]
    bigpercents=[ p for p in percents if p > 1 ]
    bestones=[ d for p,d in zip(percents,notzeros) if p > 20 ]
    extrapoints = [(float(lod[0]['SingleFPQueryParameterCount'])/int(lod[0]['ParameterCount']),100)]
    nounicode=dict()
    for item in d['SingleFPQuery'].iteritems():
        nounicode[str(item[0])] = item[1]
    xlabel = "SingleFPQuery: " + str(nounicode)
    title = "% parameters with FP query over {} networks with >1%".format(len(bigpercents))
    axislims = [0,100,0,500]
    # makeHistogram(bigpercents,45,extrapoints,xlabel,title,axislims)
    print bestones

    def posinedgefromSWI5(mygene):
        if '~SWI5' in mygene:
            return False
        elif 'SWI5' in mygene:
            return True
        elif 'x' in mygene:
            inds = [i for i in xrange(len(mygene)) if mygene.find('x', i) == i]
            for i in inds:
                extragene = mygene[i:i+2]
                for g in xgenes:
                    if g[0] == extragene and 'SWI5' in g[1]:
                        if ( mygene[i-1] == '~' and '~SWI5' in g[1] ) or ( mygene[i-1] != '~' and '~SWI5' not in g[1] ):
                            return True
        return False

    def posinedgefromNDD1(mygene):
        if '~NDD1' in mygene:
            return True
        elif 'NDD1' in mygene:
            return False
        elif 'x' in mygene:
            inds = [i for i in xrange(len(mygene)) if mygene.find('x', i) == i]
            for i in inds:
                extragene = mygene[i:i+2]
                for g in xgenes:
                    if g[0] == extragene and 'NDD1' in g[1]:
                        if ( mygene[i-1] == '~' and '~NDD1' in g[1] ) or ( mygene[i-1] != '~' and '~NDD1' not in g[1] ):
                            return True
        return False


    bestnetworks = [ d['Network'] for (p,d) in zip(percents,notzeros) if p > 10 ]
    bestpercents = [ p for p in percents if p > 10 ]
    S2Yedge=0
    netswithS2Y=[]
    S2Nedge=0
    netswithS2N=[]
    bothedges=0
    netswithboth=[]
    addednodes=0
    N2Yedge=0
    netswithN2Y=[]
    for p,n in zip(bestpercents,bestnetworks):
        genes = [[l.replace(' ','') for l in g.split(':')[:2]] for g in n.split('\n') if g]
        YOX1 = genes[4][1]
        NDD1 = genes[2][1]
        xgenes = genes[5:]
        if len(xgenes) >0:
            addednodes+=1
        Y= posinedgefromSWI5(YOX1)
        N= posinedgefromSWI5(NDD1)
        if Y and N:
            bothedges += 1
            netswithboth.append((p,n))
        elif Y:
            S2Yedge += 1
            netswithS2Y.append((p,n))
        elif N:
            S2Nedge += 1
            netswithS2N.append((p,n))
        if posinedgefromNDD1(YOX1):
            N2Yedge+=1
            netswithN2Y.append((p,n))
    print len(bestnetworks)
    print addednodes
    print float(S2Yedge)/len(bestnetworks)*100
    print float(S2Nedge)/len(bestnetworks)*100
    print float(bothedges)/len(bestnetworks)*100
    print float(N2Yedge)/len(bestnetworks)*100
    print '\n'
    for p,n in netswithN2Y:
        print p
        print n


if __name__ == "__main__":
    wavepool_network1_Dukediscussion_perturbations_5D_2016_08_15()




