import queryDSGRN as qDSGRN
from makejobs import Job
import json,subprocess

def makeYaoDatabases():
    with open('4D_2016_08_25_Yao.json','r') as Yf:
        lod = json.load(Yf)
    subprocess.call('mkdir YaoNetworks',shell=True)
    N = len(lod)
    for k,d in enumerate(lod):
        uid = str(k).zfill(N)
        open('YaoNetworks/network'+uid+'.txt','w').write(d["Network"])
    params = {}
    params['dsgrn'] = '../DSGRN'
    params['networkfolder'] = 'YaoNetworks'
    params['queryfile'] = 'shellscripts/doubleFPqueryscript_Yao.sh'
    params['removeDB'] = 'n'
    job = Job('qsub',params)
    job.prep()
    job.run()

if __name__ == "__main__":
    makeYaoDatabases()


