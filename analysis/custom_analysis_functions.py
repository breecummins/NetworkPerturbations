import json
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.size'] = 24
import suggestiongraphs as SG
import DSGRN


def makeHistogram(data,nbins,extrapoints,xlabel,title,axislims):
    n, bins, patches = plt.hist(data, nbins, normed=0, facecolor='green', alpha=0.75)
    plt.hold('on')
    N=len(extrapoints)
    if N > 1:
        cm_subsection = [float(x)/(N-1) for x in range(N)]
        colors = [ mpl.cm.jet(x) for x in cm_subsection ]    
    else:
        colors = ['b']
    if N:
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
    makeHistogram(bigpercents,45,extrapoints,xlabel,title,axislims)
    print bestones

    def posinedge(ingene,eqn):
        if '~'+ingene in eqn:
            return False
        elif ingene in eqn:
            return True
        elif 'x' in eqn:
            inds = [i for i in xrange(len(eqn)) if eqn.find('x', i) == i]
            for i in inds:
                extragene = eqn[i:i+2]
                for g in xgenes:
                    if g[0] == extragene and ingene in g[1]:
                        if ( eqn[i-1] == '~' and '~'+ingene in g[1] ) or ( eqn[i-1] != '~' and '~'+ingene not in g[1] ):
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
        genes = [[l.replace(' ','') for l in g.split(':')[:2]] for g in filter(bool,n.split('\n'))]
        YOX1 = genes[4][1]
        NDD1 = genes[2][1]
        xgenes = genes[5:]
        if len(xgenes) >0:
            addednodes+=1
        Y= posinedge('SWI5',YOX1)
        N= posinedge('SWI5',NDD1)
        if Y and N:
            bothedges += 1
            netswithboth.append((p,n))
        elif Y:
            S2Yedge += 1
            netswithS2Y.append((p,n))
        elif N:
            S2Nedge += 1
            netswithS2N.append((p,n))
        if posinedge('NDD1',YOX1):
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

def wavepool_network1_Dukediscussion_perturbations_suggestiongraphs(network_spec_file='/Users/bcummins/GIT/DSGRN/networks/5D_2016_08_02_wavepool_network1_Dukediscussion.txt', fname='/Users/bcummins/ProjectSimulationResults/wavepool_networkperturbations_paper_data/5D_2016_08_23_wavepool_network1_Dukediscussion_noregulationswap_selfedges_results.json'):
    with open(network_spec_file,'r') as f:
        network_spec = f.read()
    with open(fname,'r') as f:
        lod = json.load(f)
    list_of_networks = [ d["Network"] for d in lod  if float(d['SingleFPQueryParameterCount'])/int(d['ParameterCount']) > 0.00 ]
    if list_of_networks[0] == network_spec:
        list_of_networks = list_of_networks[1:]
    print len(list_of_networks)
    ref_graph,suggestiongraphs = SG.getAllSuggestionGraphs(network_spec,list_of_networks)
    print list_of_networks[66]
    print suggestiongraphs[66].graphviz()
    print list_of_networks[99]
    print suggestiongraphs[99].graphviz()
    counts, edges = SG.countSuggestedEdges(ref_graph,suggestiongraphs)
    for c,e in zip(counts,edges):
        print str(e) + ': ' + str(c)

def YaoNetworks(fname='/Users/bcummins/ProjectSimulationResults/YaoNetworks/4D_2016_08_25_Yao.json'):
    with open(fname,'r') as f:
        lod = json.load(f)
    percents=[ float(d['DoubleFPQueryParameterCount'])/int(d['ParameterCount'])*100 for d in lod ]
    xlabel = "DoubleFPQuery: " + d['DoubleFPQuery']
    title = "% parameters with double FP over {} networks".format(len(lod))
    axislims = [0,100,0,25]
    # makeHistogram(percents,20,[],xlabel,title,axislims)
    list_of_networks = [ d["Network"] for d in lod  if float(d['DoubleFPQueryParameterCount'])/int(d['ParameterCount']) == 1.0 ]
    fname='/Users/bcummins/ProjectSimulationResults/YaoNetworks/4D_2016_08_24_Yaostarter.txt'
    with open(fname,'r') as f:
        network_spec = f.read()
    ref_graph,suggestiongraphs = SG.getAllSuggestionGraphs(network_spec,list_of_networks)
    # print list_of_networks[8]
    # print suggestiongraphs[8].graphviz()
    # print list_of_networks[19]
    # print suggestiongraphs[19].graphviz()
    counts, edges = SG.countSuggestedEdges(ref_graph,suggestiongraphs)
    for c,e in zip(counts,edges):
        print str(e) + ': ' + str(c)

    def bestFPresults(fpfile):
        with open(fpfile,'r') as f:
            results = eval(f.read())
        percents = sorted([(float(r[0])/int(r[1])*100,r[2],r[0],r[1]) for r in results],reverse=True)
        count = 0
        for p in percents:
            ess = p[1].replace('\n',': E\n',1) 
            if p[0] >= 70 and ess in list_of_networks:
                print p
                count+=1
        print count
        # for n in list_of_networks: print n

    lowFP = '/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_lowFPresults.txt'
    print 'Low S'
    bestFPresults(lowFP)
    highFP = '/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_highFPresults.txt'
    print 'High S'
    bestFPresults(highFP)

if __name__ == "__main__":
    # wavepool_network1_Dukediscussion_perturbations_5D_2016_08_15('/Users/bcummins/ProjectSimulationResults/wavepool_networkperturbations_paper_data/5D_2016_08_23_wavepool_network1_Dukediscussion_noregulationswap_selfedges_results.json')
    # wavepool_network1_Dukediscussion_perturbations_suggestiongraphs()
    YaoNetworks()




