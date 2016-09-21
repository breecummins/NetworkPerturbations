import queryDSGRN as qDSGRN
from pythonmodules.makejobs import Job
import json,subprocess,os

def makeYaoDatabases():
    with open('4D_2016_08_25_Yao.json','r') as Yf:
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
    job = Job('qsub',params)
    job.prep()
    job.run()

def fullinducibilityquery_Yao(databasefolder='/Users/bcummins/ProjectSimulationResults/YaoNetworks/Yaonetworks_nonessential_databases'):
    with open('/Users/bcummins/ProjectSimulationResults/YaoNetworks/4D_2016_08_25_Yao.json','r') as Yf:
        lod = json.load(Yf)
    networks = [d["Network"].replace(': E\n','\n',1) for d in lod]

    FP_OFF= {"EE":[0,0],"Rp":[1,1]}
    FP_ON={"EE":[1,8],"Rp":[0,0]}

    fullInducDict = {}

    for (net,db) in zip(networks,os.listdir(databasefolder)):
        database = qDSGRN.dsgrnDatabase(os.path.join(databasefolder,db))
        num_Sparams,num_remainder = database.single_gene_query_prepare("S")
        print net
        print str(num_remainder) + "\n"
        matchesBiStab = frozenset(database.DoubleFPQuery(FP_ON,FP_OFF))
        matchesOFF = set(database.SingleFPQuery(FP_OFF))
        print matchesBiStab.issubset(matchesOFF)
        matchesOFF = frozenset(matchesOFF.difference(matchesBiStab))
        matchesON = set(database.SingleFPQuery(FP_ON))
        print matchesBiStab.issubset(matchesON)
        print "\n"
        matchesON = frozenset(matchesON.difference(matchesBiStab))
        min_gpi = 0
        max_gpi = num_Sparams-1
        OFF = set([])
        ON = set([])
        BiStab = set([])
        for m in range(num_remainder):
            graph = database.single_gene_query("S", m)
            if graph.mgi(min_gpi) in matchesOFF:
                OFF.add(m)
            if graph.mgi(max_gpi) in matchesON:
                ON.add(m)
            for i in range(min_gpi+1,max_gpi):
                if graph.mgi(i) in matchesBiStab:
                    BiStab.add(m)
                    break
        fullinduc = len(BiStab.intersection(OFF.intersection(ON)))
        fullInducDict[str(net)] = (len(OFF),len(ON),len(BiStab),num_remainder,fullinduc)
    print fullInducDict
    with open('/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_fullinducibilityresults2.json','w') as f:
        json.dump(fullInducDict,f)

if __name__ == "__main__":
    # makeYaoDatabases()
    fullinducibilityquery_Yao()


