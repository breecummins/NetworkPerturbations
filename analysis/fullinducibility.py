import queryDSGRN as qDSGRN
from pythonmodules.makejobs import Job
import json,subprocess,os

def makeYaoDatabases(fname='4D_2016_08_25_Yao.json'):
    with open(fname,'r') as Yf:
        lod = json.load(Yf)
    subprocess.call('mkdir YaoNetworks',shell=True)
    N = len(str(len(lod)))
    for k,d in enumerate(lod):
        uid = str(k).zfill(N)
        network_spec = d["Network"].replace(': E\n','\n',1)
        open('YaoNetworks/network'+uid+'.txt','w').write(network_spec)
    params = {}
    params['dsgrn'] = '../DSGRN'
    params['networkfolder'] = 'YaoNetworks'
    params['queryfile'] = 'shellscripts/doubleFPqueryscript_Yao.sh'
    params['removeDB'] = 'n'
    params['removeNF'] = 'n'
    job = Job('qsub',params)
    job.prep()
    job.run()

def fullinducibilityquery_Yao(databasefolder='/Users/bcummins/ProjectSimulationResults/YaoNetworks/Yaonetworks_nonessential_databases'):

    FP_OFF= {"EE":[0,0],"Rp":[1,1]}
    FP_ON={"EE":[1,8],"Rp":[0,0]}

    fullInducDict = {}

    for db in os.listdir(databasefolder):
        database = qDSGRN.dsgrnDatabase(os.path.join(databasefolder,db))
        size_factor_graph,num_factor_graphs = database.single_gene_query_prepare("S")
        print(database.network.specification())
        print str(num_factor_graphs) + "\n"
        matchesBiStab = frozenset(database.DoubleFPQuery(FP_ON,FP_OFF))
        matchesOFF = frozenset(set(database.SingleFPQuery(FP_OFF)).difference(matchesBiStab))
        matchesON = frozenset(set(database.SingleFPQuery(FP_ON)).difference(matchesBiStab))
        min_gpi = 0
        max_gpi = size_factor_graph-1
        OFF = set([])
        ON = set([])
        BiStab = set([])
        for m in range(num_factor_graphs):
            graph = database.single_gene_query("S", m)
            if graph.mgi(min_gpi) in matchesOFF:
                OFF.add(m)
            if graph.mgi(max_gpi) in matchesON:
                ON.add(m)
            for i in range(min_gpi+1,max_gpi):
                if graph.mgi(i) in matchesBiStab:
                    BiStab.add(m)
                    break
        resettablebistability = BiStab.intersection(OFF)
        inducibility = BiStab.intersection(ON)
        fullinducibility = len(resettablebistability.intersection(inducibility))
        fullInducDict[database.network.specification()] = (len(resettablebistability),len(inducibility),fullinducibility,num_factor_graphs)
    print fullInducDict
    with open('/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_fullinducibilityresults.json','w') as f:
        json.dump(fullInducDict,f)

if __name__ == "__main__":
    # makeYaoDatabases()
    # makeYaoDatabases('/Users/bcummins/ProjectSimulationResults/YaoNetworks/4D_2016_08_25_Yao.json')
    fullinducibilityquery_Yao()


