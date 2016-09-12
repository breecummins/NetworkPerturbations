from pythonmodules.makejobs import Job 
import networkperturbations as perturb
import subprocess, os, DSGRN, sys, itertools, json

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

# def Yao_low(param,numparams,count):
#     if param.logic()[0].hex() == '0': # if L, U of source S are lowest
#         numparams += 1
#         ann = getAnnotations(param)
#         if len(ann) == 1 and ann[0][:2] == 'FP':
#             digits = [int(i) for i in ann[0] if i.isdigit()]
#             if digits[-2] == 1 and digits[-1] == 0: # if Rp high and EE low
#                 count += 1
#     return numparams,count

# def Yao_high(param,numparams,count):
#     if param.logic()[0].hex() == 'F': # if L, U of source S are highest
#         numparams += 1
#         ann = getAnnotations(param)
#         if len(ann) == 1 and ann[0][:2] == 'FP':
#             digits = [int(i) for i in ann[0] if i.isdigit()]
#             if digits[-2] == 0 and digits[-1] >= 1: # if Rp low and EE high
#                 count += 1
#     return numparams,count

def Yao_FPs(param,numparams,count,low=True):
    if param.logic()[0].hex() == '0'*low + 'F'*(not low):
        numparams+=1
        ann = getAnnotations(param)
        nums = [[int(i) for i in a if i.isdigit()][-2:] for a in ann if a[:2]=='FP']
        if len(nums)!=1 or (low and ( ([1,0] not in nums) or (any(filter(lambda x: x[0] ==0 and x[1] > 0,nums))) )) or (not low and ( ([1,0] in nums) or (not any(filter(lambda x: x[0] ==0 and x[1] > 0,nums))) )):
            pass
        else: 
            count+=1
    return numparams,count

def runYaoNonEssential(savefile = '/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_FPresults.txt'):
    networkdir = '/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential'
    list_of_networks=[]
    results=[]
    paramstrs=[]
    for fname in os.listdir(networkdir):
        full = os.path.join(networkdir,fname)
        with open(full,'r') as f:
            list_of_networks.append(f.read())
        network = DSGRN.Network(full)
        parametergraph = DSGRN.ParameterGraph(network)
        paramslow,countlow,totlow,paramshigh,counthigh,tothigh = [],0,0,[],0,0
        for p in xrange(parametergraph.size()):
            param = parametergraph.parameter(p)
            totlow,nc= Yao_FPs(param,totlow,0,low=True)
            if nc:
                countlow+=1
                paramslow.append(tuple([ tuple([ tuple(a) for a in v  ]) for v in eval(param.stringify())[1:]])) #[1:] means cut off S param 
            else:
                tothigh,nc= Yao_FPs(param,tothigh,0,low=False)
                if nc:
                    counthigh+=1
                    paramshigh.append(tuple([ tuple([ tuple(a) for a in v  ]) for v in eval(param.stringify())[1:]]))
        both = set(paramslow).intersection(paramshigh)
        r = (countlow,totlow,counthigh,tothigh,len(both))
        print list_of_networks[-1]
        print r
        results.append(r)
        paramstrs.append(both)
    with open(savefile,'w') as sf:
        sf.write(str(results)+'\n')
        sf.write(str(zip(list_of_networks,paramstrs)))

# def E2F_low(param,numparams,count):
#     if param.logic()[0].hex() == '0': # if L, U of source S are lowest
#         numparams += 1
#         ann = getAnnotations(param)
#         if len(ann) == 1 and ann[0][:2] == 'FP':
#             digits = [int(i) for i in ann[0] if i.isdigit()]
#             if digits[-2] == 0 and digits[-1] == 1: # E2F low and E2F_Rb high (opposite of Yao)
#                 count += 1
#     return numparams,count

# def E2F_high(param,numparams,count):
#     if param.logic()[0].hex() == 'F': # if L, U of source S are highest
#         numparams += 1
#         ann = getAnnotations(param)
#         if len(ann) == 1 and ann[0][:2] == 'FP':
#             digits = [int(i) for i in ann[0] if i.isdigit()]
#             if digits[-2] >= 1 and digits[-1] == 0: # E2F high and E2F_Rb low (opposite of Yao) 
#                 count += 1
#     return numparams,count

def E2F_FPs(param,numparams,count,low=True):
    if param.logic()[0].hex() == '0'*low + 'F'*(not low):
        numparams+=1
        ann = getAnnotations(param)
        nums = [[int(i) for i in a if i.isdigit()][-2:] for a in ann if a[:2]=='FP']
        if len(nums)!=1 or (low and ( ([0,1] not in nums) or (any(filter(lambda x: x[0] >0 and x[1] == 0,nums))) )) or (not low and ( ([0,1] in nums) or (not any(filter(lambda x: x[0] >0 and x[1] == 0,nums))) )):
            pass
        else: 
            count+=1
    return numparams,count

def truncateSfromE2Fparam(param):
    #cut off S param
    p = param.stringify()
    return p[0]+p[p.index('[',18):]

def runE2F6DNonEssential(networknum='2',networkdir = '/Users/bcummins/ProjectSimulationResults/E2F_Rb_paper_data/',writeparams=True):    
    fname = networkdir+'6D_2016_08_26_cancerE2Fnetwork'+networknum+'_nonessential.txt'
    savefile = networkdir+'6D_2016_08_26_cancerE2Fnetwork'+networknum+'_nonessential_FPresults_intersectedbistable.txt'
    bistablefname=networkdir+'6D_2016_08_26_cancerE2Fnetwork'+networknum+'_bistabilityquery.txt'
    network = DSGRN.Network(fname)
    bistablenetworkspec = network.specification().replace('\n',': E\n',1)
    bistablenetwork = DSGRN.Network()
    bistablenetwork.assign(bistablenetworkspec)
    bistableparametergraph = DSGRN.ParameterGraph(bistablenetwork)
    with open(bistablefname,'r') as f:
        bistableparams = set([])
        for p in f:
            param = bistableparametergraph.parameter(int(p))
            bistableparams.add(truncateSfromE2Fparam(param)) 
    parametergraph = DSGRN.ParameterGraph(network)
    paramslow,countlow,totlow,paramshigh,counthigh,tothigh = set([]),0,0,set([]),0,0
    for p in xrange(parametergraph.size()):
        param = parametergraph.parameter(p)
        paramstr = truncateSfromE2Fparam(param)
        if paramstr in bistableparams:
            totlow,nc= E2F_FPs(param,totlow,0,low=True)
            if nc:
                countlow+=1
                paramslow.add(paramstr) 
                if not (countlow + counthigh)%50000:
                    print countlow+counthigh
                    sys.stdout.flush()
            else:
                tothigh,nc= E2F_FPs(param,tothigh,0,low=False)
                if nc:
                    counthigh+=1
                    paramshigh.add(paramstr)
                    if not (countlow + counthigh)%50000:
                        print countlow+counthigh
                        sys.stdout.flush()
    both = paramshigh & paramslow
    results = (countlow,totlow,counthigh,tothigh,len(both))
    print results
    with open(savefile,'w') as sf:
        sf.write(open(fname).read())
        sf.write('\n\nCount E2F low params + bistability out of total S low params, Count E2F high params + bistability out of total S high params, Count params in both:\n')
        sf.write(str(results))
        if writeparams:
            sf.write('\n\nParams in both:\n')
            sf.write(str(both))


def wavepool_network1_Dukediscussion_perturbations_5D_2016_08_23_FCquery(fname='/Users/bcummins/ProjectSimulationResults/wavepool_networkperturbations_paper_data/5D_2016_08_23_wavepool_network1_Dukediscussion_noregulationswap_selfedges_results.json',NETWORKDIR = '/Users/bcummins/ProjectSimulationResults/wavepool_networkperturbations_paper_data/5D_2016_08_23_wavepool_network1_Dukediscussion_topnetworks/',dsgrn="/Users/bcummins/GIT/DSGRN",location='local'):
    lod = json.load(open(fname,'r'))
    # networks=[ d["Network"] for d in lod  if float(d['SingleFPQueryParameterCount'])/int(d['ParameterCount'])*100 > 25 ]
    networks=[ d["Network"] for d in lod  if float(d['SingleFPQueryParameterCount'])/int(d['ParameterCount'])*100 > 25 ]
    N=len(str(len(networks)))  
    subprocess.call('mkdir '+NETWORKDIR,shell=True)  
    for (k,n) in enumerate(networks):
        uid = str(k).zfill(N)
        nfile = os.path.join(NETWORKDIR, "network"+uid+".txt")
        open(nfile,'w').write(n)
    params={}
    params['dsgrn'] = dsgrn
    params['networkfolder'] = NETWORKDIR
    params['queryfile'] = './shellscripts/stableFCqueryscript.sh'
    job = Job(location,params)
    job.prep()
    job.run()



if __name__ == '__main__':
    # makeSelfEdgePerturbations()
    # makeYaoGraphs()
    # runYaoNonEssential()
    # compareYaoParamsNonEssential('S : (S) \nMD : (S) : E\nRp : (~MD) : E\nEE : (MD + EE)(~Rp) : E\n')
    # compareYaoParamsNonEssential('S : (S) \nMD : (S) : E\nRp : (~MD)(~EE) : E\nEE : (MD)(~Rp) : E\n')
    # runE2F6DNonEssential(networknum='1',networkdir='./',writeparams=False)
    # wavepool_network1_Dukediscussion_perturbations_5D_2016_08_23_FCquery()
    wavepool_network1_Dukediscussion_perturbations_5D_2016_08_23_FCquery('5D_2016_08_23_wavepool_network1_Dukediscussion_noregulationswap_selfedges_results.json','5D_2016_08_23_wavepool_network1_Dukediscussion_topnetworks','/share/data/bcummins/DSGRN','qsub')