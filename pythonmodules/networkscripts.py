from pythonmodules.makejobs import Job 
import networkperturbations as perturb
import subprocess

def makeSelfEdgePerturbations():
    job=Job(0)
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

if __name__ == '__main__':
    makeSelfEdgePerturbations()



