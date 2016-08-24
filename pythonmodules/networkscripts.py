from pythonmodules.makejobs import Job 
import networkperturbations as perturb
import subprocess

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
    fname = '3D_2016_08_24_Yaostarter.txt'
    with open(fname,'w') as f:
        f.write('S : S : E\nMD : S : E\nRp : : E\nEE : : E')
    params = {}
    params['networkfile'] = fname
    edgefile = 'YaoEdgeFile.txt'
    with open(edgefile,'w') as f:
        f.write('MD = a(EE)\nRp = r(MD)\nRp = a(EE)\nRp = r(EE)\nEE = r(Rp)\nEE = a(MD)\nEE = r(MD)\nEE = a(EE)')
    params['edgefile'] = edgefile
    params['swap_edge_reg'] = False
    params['numperturbations'] = 144
    params['maxadditionspergraph'] = 6
    params['maxparams'] = 10000000000
    params['time_to_wait'] = 30

    job=Job(params=params)
    job._parsefilesforperturbation()
    networks = perturb.perturbNetwork(job.params)
    job.NETWORKDIR = './Yaonetworks'
    subprocess.call('mkdir '+job.NETWORKDIR,shell=True)
    job._savefiles(networks)


if __name__ == '__main__':
    # makeSelfEdgePerturbations()
    makeYaoGraphs()


