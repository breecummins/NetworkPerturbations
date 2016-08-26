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

if __name__ == '__main__':
    # makeSelfEdgePerturbations()
    # makeYaoGraphs()
    runYaoNonEssential(Yao_high,'/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_highFPresults.txt')

