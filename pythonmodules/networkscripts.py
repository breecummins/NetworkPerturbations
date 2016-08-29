from pythonmodules.makejobs import Job 
import networkperturbations as perturb
import subprocess, os, DSGRN, sys, itertools

def makeSelfEdgePerturbations():
    job=Job()
    job._parsefilesforperturbation()
    networks = perturb.perturbNetwork(job.params)
    numvars = len(filter(bool,job.params['network_spec'].split('\n'))) # number of vars in original network
    selfedgenets = []
    for n in networks:
        eqns = filter(bool,n.split('\n'))
        for e in eqns[numvars:]:
            var,expr = (l.replace(' ','') for l in e.split(':')[:2])
            if var in expr: # FIX: assuming no var is a substring of another, should check
                selfedgenets.append(n)
                break
    print len(selfedgenets)
    job.NETWORKDIR = './selfedgenetworks'
    subprocess.call('mkdir '+job.NETWORKDIR,shell=True)
    job._savefiles(selfedgenets)

def makeYaoGraphs():
    fname = '/Users/bcummins/ProjectSimulationResults/YaoNetworks/4D_2016_08_24_Yaostarter.txt'
    with open(fname,'w') as f:
        f.write('S : S : E\nMD : S : E\nRp : : E\nEE : : E')
    params = {}
    params['networkfile'] = fname
    edgefile = '/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoEdgeFile.txt'
    with open(edgefile,'w') as f:
        f.write('MD = a(EE)\nRp = r(MD)\nRp = a(EE)\nRp = r(EE)\nEE = r(Rp)\nEE = a(MD)\nEE = r(MD)\nEE = a(EE)')
    params['edgefile'] = edgefile
    params['swap_edge_reg'] = False
    params['numperturbations'] = 144
    params['maxadditionspergraph'] = 6
    params['maxparams'] = 10000000000
    params['time_to_wait'] = 5

    job=Job(params=params)
    job._parsefilesforperturbation()
    networks = perturb.perturbNetwork(job.params)
    job.NETWORKDIR = './Yaonetworks'
    subprocess.call('mkdir '+job.NETWORKDIR,shell=True)
    job._savefiles(networks)

def getAnnotations(param):
    domaingraph = DSGRN.DomainGraph(param)
    morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
    morsegraph = DSGRN.MorseGraph()
    morsegraph.assign(domaingraph, morsedecomposition)
    mg = eval(morsegraph.stringify())
    return list(itertools.chain(*mg['annotations']))

def Yao_low(param,numparams,count):
    if param.logic()[0].hex() == '0': # if L, U of source S are lowest
        numparams += 1
        ann = getAnnotations(param)
        if len(ann) == 1 and ann[0][:2] == 'FP':
            digits = [int(i) for i in ann[0] if i.isdigit()]
            if digits[-2] == 1 and digits[-1] == 0: # if Rp high and EE low
                count += 1
    return numparams,count

def Yao_high(param,numparams,count):
    if param.logic()[0].hex() == 'F': # if L, U of source S are highest
        numparams += 1
        ann = getAnnotations(param)
        if len(ann) == 1 and ann[0][:2] == 'FP':
            digits = [int(i) for i in ann[0] if i.isdigit()]
            if digits[-2] == 0 and digits[-1] >= 1: # if Rp low and EE high
                count += 1
    return numparams,count

def runYaoNonEssential(paramfunc=Yao_low,savefile = '/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_lowFPresults.txt'):
    networkdir = '/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential'
    list_of_networks=[]
    totalparams=[]
    counts_of_FP=[]
    for fname in os.listdir(networkdir):
        full = os.path.join(networkdir,fname)
        with open(full,'r') as f:
            list_of_networks.append(f.read())
        network = DSGRN.Network(full)
        parametergraph = DSGRN.ParameterGraph(network)
        numparams,count = 0,0
        for p in range(parametergraph.size()):
            param = parametergraph.parameter(p)
            numparams,count= paramfunc(param,numparams,count)
        counts_of_FP.append(count)
        totalparams.append(numparams)
    results = sorted(zip(counts_of_FP,totalparams,list_of_networks))
    print results
    with open(savefile,'w') as sf:
        sf.write(str(results))

def compareYaoParamsNonEssential(network_spec):
    network = DSGRN.Network()
    network.assign(network_spec)
    parametergraph = DSGRN.ParameterGraph(network)
    lowparams,highparams=[],[]
    for p in range(parametergraph.size()):
        param = parametergraph.parameter(p)
        np,nc= Yao_low(param,0,0)
        if nc:
            lowparams.append(eval(param.stringify())[1:])
        elif not np:
            np,nc= Yao_high(param,0,0)
            if nc:
                highparams.append(eval(param.stringify())[1:])
    print "In low, not high:"
    for p in lowparams:
        if p not in highparams:
            print p
    print "In high, not low:"
    for p in highparams:
        if p not in lowparams:
            print p

def E2F_low(param,numparams,count):
    if param.logic()[0].hex() == '0': # if L, U of source S are lowest
        numparams += 1
        ann = getAnnotations(param)
        if len(ann) == 1 and ann[0][:2] == 'FP':
            digits = [int(i) for i in ann[0] if i.isdigit()]
            if digits[-2] == 0 and digits[-1] == 1: # E2F low and E2F_Rb high (opposite of Yao)
                count += 1
    return numparams,count

def E2F_high(param,numparams,count):
    if param.logic()[0].hex() == 'F': # if L, U of source S are highest
        numparams += 1
        ann = getAnnotations(param)
        if len(ann) == 1 and ann[0][:2] == 'FP':
            digits = [int(i) for i in ann[0] if i.isdigit()]
            if digits[-2] >= 1 and digits[-1] == 0: # E2F high and E2F_Rb low (opposite of Yao) 
                count += 1
    return numparams,count

def runE2F6DNonEssential(fname = '/Users/bcummins/ProjectSimulationResults/E2F_Rb_paper_data/6D_2016_08_26_cancerE2Fnetwork1_nonessential.txt'
,savefile = '/Users/bcummins/ProjectSimulationResults/E2F_Rb_paper_data/6D_2016_08_26_cancerE2Fnetwork1_nonessential_FPresults.txt'):
    network = DSGRN.Network(fname)
    parametergraph = DSGRN.ParameterGraph(network)
    paramslow,countlow,totlow,paramshigh,counthigh,tothigh = [],0,0,[],0,0
    for p in range(parametergraph.size()):
        param = parametergraph.parameter(p)
        totlow,nc= E2F_low(param,totlow,0)
        if nc:
            countlow+=1
            paramslow.append(tuple([ tuple([ tuple(a) for a in v  ]) for v in eval(param.stringify())[1:]])) #[1:] means cut off S param 
        else:
            tothigh,nc= E2F_high(param,tothigh,0)
            if nc:
                counthigh+=1
                paramshigh.append(tuple([ tuple([ tuple(a) for a in v  ]) for v in eval(param.stringify())[1:]]))
    both = set(paramslow).intersection(paramshigh)
    results = (countlow,totlow,counthigh,tothigh,len(both))
    print results
    with open(savefile,'w') as sf:
        sf.write(open(fname).read())
        sf.write('\n\nCount E2F low params out of total S low params, Count E2F high params out of total S high params, Count params in both:\n')
        sf.write(str(results))
        sf.write('\n\nParams in both:\n')
        sf.write(str(both))

if __name__ == '__main__':
    # makeSelfEdgePerturbations()
    # makeYaoGraphs()
    # runYaoNonEssential(Yao_high,'/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_highFPresults.txt')
    # compareYaoParamsNonEssential('S : (S) \nMD : (S) : E\nRp : (~MD) : E\nEE : (MD + EE)(~Rp) : E\n')
    # compareYaoParamsNonEssential('S : (S) \nMD : (S) : E\nRp : (~MD)(~EE) : E\nEE : (MD)(~Rp) : E\n')
    networknum = '3'
    runE2F6DNonEssential(fname = '/Users/bcummins/ProjectSimulationResults/E2F_Rb_paper_data/6D_2016_08_26_cancerE2Fnetwork'+networknum+'_nonessential.txt'
,savefile = '/Users/bcummins/ProjectSimulationResults/E2F_Rb_paper_data/6D_2016_08_26_cancerE2Fnetwork'+networknum+'_nonessential_FPresults.txt')