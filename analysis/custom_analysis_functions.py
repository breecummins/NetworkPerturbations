import json
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.size'] = 24
import suggestiongraphs as SG
import DSGRN, subprocess


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
    print N
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
    print N
    notzeros=[ d for d in lod  if d['SingleFPQueryParameterCount']>0 ]
    percents=[ float(d['SingleFPQueryParameterCount'])/int(d['ParameterCount'])*100 for d in notzeros ]
    bigpercents=[ p for p in percents if p > 1 ]
    bestones=[ d for p,d in zip(percents,notzeros) if p > 20 ]
    print lod[0]
    extrapoints = [(float(lod[0]['SingleFPQueryParameterCount'])/int(lod[0]['ParameterCount']),100)]
    nounicode=dict()
    for item in d['SingleFPQuery'].iteritems():
        nounicode[str(item[0])] = item[1]
    xlabel = "SingleFPQuery: " + str(nounicode)
    title = "% parameters with FP query over {} networks with >1%".format(len(bigpercents))
    axislims = [0,100,0,500]
    makeHistogram(bigpercents,45,extrapoints,xlabel,title,axislims)
    print bestones

def wavepool_network1_Dukediscussion_perturbations_5D_2016_08_23(fname='/Users/bcummins/ProjectSimulationResults/wavepool_networkperturbations_paper_data/5D_2016_08_23_wavepool_network1_Dukediscussion_noregulationswap_selfedges_results.json'):
    lod = json.load(open(fname,'r'))
    N = len(lod)
    # print N
    # print lod[0]
    notzeros=[ d for d in lod  if d['SingleFPQueryParameterCount']>0 ]
    percents=[ float(d['SingleFPQueryParameterCount'])/int(d['ParameterCount'])*100 for d in notzeros ]
    bigpercents=[ p for p in percents if p > 2 ]
    bestones=sorted([ (p,d["Network"]) for p,d in zip(percents,notzeros) if p > 25 ],reverse=True)
    extrapoints = [(float(lod[0]['SingleFPQueryParameterCount'])/int(lod[0]['ParameterCount']),100)]
    nounicode=dict()
    for item in d['SingleFPQuery'].iteritems():
        nounicode[str(item[0])] = item[1]
    xlabel = "SingleFPQuery: " + str(nounicode)
    title = "% parameters with FP query over {} networks with >2%".format(len(bigpercents))
    axislims = [0,100,0,750]
    # makeHistogram(bigpercents,50,extrapoints,xlabel,title,axislims)
    # for z in bestones:
    #     print z
    



def wavepool_network1_Dukediscussion_perturbations_suggestiongraphs(network_spec_file='/Users/bcummins/ProjectSimulationResults/wavepool_networkperturbations_paper_data/5D_2016_08_02_wavepool_network1_Dukediscussion.txt', fname='/Users/bcummins/ProjectSimulationResults/wavepool_networkperturbations_paper_data/5D_2016_08_23_wavepool_network1_Dukediscussion_noregulationswap_selfedges_results.json'):
    with open(network_spec_file,'r') as f:
        network_spec = f.read()
    with open(fname,'r') as f:
        lod = json.load(f)
    list_of_networks = [ d["Network"] for d in lod  if float(d['SingleFPQueryParameterCount'])/int(d['ParameterCount']) > 0.10 ]
    print "\n\nEdges suggested by all {} networks with greater than {}% SBF, HCM1 high, rest low FP:\n".format(len(list_of_networks),10)
    getSuggestedEdges(network_spec,list_of_networks)
    list_of_networks = [ d["Network"] for d in lod  if float(d['SingleFPQueryParameterCount'])/int(d['ParameterCount']) > 0.15 ]
    print "\n\nEdges suggested by all {} networks with greater than {}% SBF, HCM1 high, rest low FP:\n".format(len(list_of_networks),15)
    getSuggestedEdges(network_spec,list_of_networks)
    list_of_networks = [ d["Network"] for d in lod  if float(d['SingleFPQueryParameterCount'])/int(d['ParameterCount']) > 0.20 ]
    print "\n\nEdges suggested by all {} networks with greater than {}% SBF, HCM1 high, rest low FP:\n".format(len(list_of_networks),20)
    getSuggestedEdges(network_spec,list_of_networks)
    list_of_networks = [ d["Network"] for d in lod  if float(d['SingleFPQueryParameterCount'])/int(d['ParameterCount']) > 0.25 ]
    print "\n\nEdges suggested by all {} networks with greater than {}% SBF, HCM1 high, rest low FP:\n".format(len(list_of_networks),25)
    getSuggestedEdges(network_spec,list_of_networks)

def getSuggestedEdges(network_spec,list_of_networks):
    if list_of_networks[0] == network_spec:
        list_of_networks = list_of_networks[1:] # FIXME: Actually need graph isomorphism here
    ref_graph,suggestiongraphs = SG.getAllSuggestionGraphs(network_spec,list_of_networks)
    # print list_of_networks[66]
    # print suggestiongraphs[66].graphviz()
    # print list_of_networks[99]
    # print suggestiongraphs[99].graphviz()
    counts, edges = SG.countSuggestedEdges(ref_graph,suggestiongraphs)
    for c,e in zip(counts,edges):
        print str(e) + ': ' + str(c)

def wavepool_network2_Dukediscussion_perturbations_6D_2016_08_02(network_spec_file='/Users/bcummins/ProjectSimulationResults/wavepool_networkperturbations_paper_data/6D_2016_08_02_wavepool_network2_Dukediscussion.txt',fname='/Users/bcummins/ProjectSimulationResults/wavepool_networkperturbations_paper_data/6D_2016_08_02_wavepool_network2_Dukediscussion_results.json'):
    # with open(network_spec_file,'r') as f:
    #     network_spec = f.read()
    with open(fname,'r') as f:
        lod = json.load(f)
    # # They are the same
    # print network_spec
    # print lod[0]["Network"]
    N = len(lod)
    percents=[ float(d['StableFCParameterCount'])/int(d['ParameterCount'])*100 for d in lod ]
    list_of_networks = [ d["Network"] for (p,d) in zip(percents,lod)  if p > 0.00 ]
    nonzeros = [p for p in percents if p > 1]
    bestones=[ d for p,d in zip(nonzeros,list_of_networks) if p > 50 ]
    extrapoints = [(float(lod[0]['StableFCParameterCount'])/int(lod[0]['ParameterCount']),50)]
    xlabel = "Stable FC Parameter Count"
    title = "% parameters with at least 1 stable FC over {} networks with >1%".format(len(nonzeros))
    axislims = [0,100,0,100]
    makeHistogram(nonzeros,45,extrapoints,xlabel,title,axislims)
    for b in bestones: print b
    getSuggestedEdges(lod[0]["Network"],list_of_networks[1:])

def YaoNetworks(fname='/Users/bcummins/ProjectSimulationResults/YaoNetworks/4D_2016_08_25_Yao.json'):
    with open(fname,'r') as f:
        lod = json.load(f)
    percents=[ float(d['DoubleFPQueryParameterCount'])/int(d['ParameterCount'])*100 for d in lod ]
    xlabel = "DoubleFPQuery: " + d['DoubleFPQuery']
    title = "% parameters with double FP over {} networks".format(len(lod))
    axislims = [0,100,0,25]
    makeHistogram(percents,20,[],xlabel,title,axislims)


def YaoNetworks_tiered_suggested_edges(fname='/Users/bcummins/ProjectSimulationResults/YaoNetworks/4D_2016_08_25_Yao.json'):
    nname='/Users/bcummins/ProjectSimulationResults/YaoNetworks/4D_2016_08_24_Yaostarter.txt'
    with open(nname,'r') as f:
        network_spec = f.read()
    with open(fname,'r') as f:
        lod = json.load(f)
    bistablepercents=sorted([ (float(d['DoubleFPQueryParameterCount'])/int(d['ParameterCount'])*100,d["Network"],d['DoubleFPQueryParameterCount']) for d in lod ],reverse=True)

    def bistable_sugg_edges(thresh):
        list_of_networks = [y[1] for y in filter(lambda x: x[0] > thresh and x[2]>0, bistablepercents)]
        ref_graph,suggestiongraphs = SG.getAllSuggestionGraphs(network_spec,list_of_networks)
        counts, edges = SG.countSuggestedEdges(ref_graph,suggestiongraphs)
        print "\n\nEdges suggested by all {} networks with greater than {}% bistability:\n".format(len(list_of_networks),thresh)
        for c,e in zip(counts,edges):
            print str(e) + ': ' + str(c)

    bistable_sugg_edges(0)
    # bistable_sugg_edges(25)
    bistable_sugg_edges(50)
    # bistable_sugg_edges(75)
    bistable_sugg_edges(99)

def YaoNetworks_fullinducibility(fname='/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_fullinducibilityresults.json'):
    # format: (len(resettablebistab),len(induc),len(BiStab),fullinduc,size_factor_graph)
    with open(fname,'r') as f:
        fidict = json.load(f) 

    def makeAllHistograms():
        # low FP at low S
        percents = [float(val[0])/val[3] for val in fidict.values() if val[0] > 0]
        xlabel = "% parameters in the factor graph"
        title = "Resettable bistability > 0 for {} total networks".format(len(percents))
        axislims = [0,5,0,10]
        numbins = 10
        makeHistogram(percents,numbins,[],xlabel,title,axislims)

        # high FP at high S
        percents = [float(val[1])/val[3] for val in fidict.values() if val[1] > 0]
        xlabel = "% parameters in the factor graph"
        title = "Inducibility > 0 for {} total networks".format(len(percents))
        axislims = [0,5,0,10]
        numbins = 10
        makeHistogram(percents,numbins,[],xlabel,title,axislims)

        # full incibility
        percents = [float(val[2])/val[3] for val in fidict.values() if val[2] > 0]
        xlabel = "% parameters in the factor graph"
        title = "Full inducibility > 0 for {} total networks".format(len(percents))
        axislims = [0,5,0,10]
        numbins = 10
        makeHistogram(percents,numbins,[],xlabel,title,axislims)

    makeAllHistograms()

    # full inducibility suggested edges
    list_of_networks = [key for key,val in fidict.iteritems() if val[2] > 0]
    with open('/Users/bcummins/ProjectSimulationResults/YaoNetworks/4D_2016_08_24_Yaostarter.txt','r') as nf:
        network_spec = nf.read()
    getSuggestedEdges(network_spec,list_of_networks)

def E2Fbistability(func=1,networknum='2'):
    def bicount():
        N = parametergraph.size()
        n = subprocess.check_output('cat '+bistablefname+' | wc -l', shell=True)
        print "Percentage bistability:"
        print float(n)/N

    def checkall3():
        with open(bistablefname,'r') as f:
            params = []
            bistablecount = 0
            for p in f:
                param = parametergraph.parameter(int(p))
                params.append(tuple([ tuple([ tuple(a) for a in v  ]) for v in eval(param.stringify())[1:]])) #[1:] means cut off S param 
                bistablecount+=1
        with open('/Users/bcummins/ProjectSimulationResults/E2F_Rb_paper_data/6D_2016_08_26_cancerE2Fnetwork'+networknum+'_nonessential_FPresults.txt','r') as f:
            getnext=0
            for l in f.readlines():
                if l == 'Params in both:\n':
                    getnext=1
                elif getnext:
                    lowandhigh = eval(l)
                    break
        allparams = set(params).intersection(lowandhigh)
        print "Count of params with all three properties:"
        print len(allparams)
        print "Percentage bistability:"
        print float(bistablecount)/N

    network = DSGRN.Network('/Users/bcummins/ProjectSimulationResults/E2F_Rb_paper_data/6D_2016_08_26_cancerE2Fnetwork'+networknum+'.txt')
    parametergraph = DSGRN.ParameterGraph(network)
    bistablefname = '/Users/bcummins/ProjectSimulationResults/E2F_Rb_paper_data/bistabilityquerynet'+networknum+'.txt'        
    if func == 1:
        bicount()
    else:
        checkall3()

if __name__ == "__main__":
    # wavepool_network1_Dukediscussion_perturbations_5D_2016_08_23()
    # wavepool_network1_Dukediscussion_perturbations_suggestiongraphs()
    # YaoNetworks()
    # YaoNetworks_tiered_suggested_edges()
    # E2Fbistability(1,'4')
    # wavepool_network2_Dukediscussion_perturbations_6D_2016_08_02()
    YaoNetworks_fullinducibility()

