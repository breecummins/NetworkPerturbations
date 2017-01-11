from pythonmodules.makejobs import Job
import json, subprocess

def makeYaoDatabases(fname='4D_2016_08_25_Yao.json'):
    # with open(fname,'r') as Yf:
    #     lod = json.load(Yf)
    # subprocess.call('mkdir YaoNetworks',shell=True)
    # N = len(str(len(lod)))
    # for k,d in enumerate(lod):
    #     uid = str(k).zfill(N)
    #     network_spec = d["Network"].replace(': E\n','\n',1)
    #     open('YaoNetworks/network'+uid+'.txt','w').write(network_spec)
    params = {}
    params['dsgrn'] = '../DSGRN'
    params['networkfolder'] = 'YaoNetworks'
    # params['queryfile'] = 'shellscripts/doubleFPqueryscript_Yao.sh'
    params['queryfile'] = 'shellscripts/blankquery.sh'
    params['removeDB'] = 'n'
    params['removeNF'] = 'n'
    job = Job('local',params)
    job.prep()
    job.run()

if __name__ == "__main__":
    # makeYaoDatabases()
    makeYaoDatabases('/Users/bcummins/ProjectSimulationResults/YaoNetworks/4D_2016_08_25_Yao.json')
