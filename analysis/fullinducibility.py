import queryDSGRN as qDSGRN
from pythonmodules.makejobs import Job
import json,subprocess

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

def fullinducibilityquery_Yao(databasefolder):
    with open('4D_2016_08_25_Yao.json','r') as Yf:
        lod = json.load(Yf)
    networks = [d["Network"].replace(': E\n','\n',1) for d in lod]

    FP_OFF= {"EE":[0,0],"Rp":[1,1]}
    FP_ON={"EE":[1,8],"Rp":[0,0]}

    countOFF=0
    countON=0
    countBiStab=0
    fullInduc = {}

    for (net,db) in zip(networks,databasefolder):
        database = qDSGRN.dsgrnDatabase(db)
        num_Sparams,num_remainder = database.single_gene_query_prepare("S")
        matchesON = frozenset(database.SingleFPQuery(FP_OFF))
        matchesOFF = frozenset(database.SingleFPQuery(FP_ON))
        matchesBiStab = frozenset(database.DoubleFPQuery(FP_ON,FP_OFF))
        min_gpi = 0
        max_gpi = num_Sparams-1
        OFF = set([])
        ON = set([])
        BiStab = set([])
        fraction_full_inducible = set([])
        for m in range(num_remainder):
            graph = database.single_gene_query("S", m)
            if graph.mgi(min_gpi) in matchesOFF and graph.mgi(min_gpi) not in matchesBiStab:
                OFF.add(m)
            if graph.mgi(max_gpi) in matchesON and graph.mgi(max_gpi) not in matchesBiStab:
                ON.add(m)
            for i in range(min_gpi+1,max_gpi):
                if graph.mgi(i) in matchesBiStab:
                    BiStab.add(m)
                    break
            








if __name__ == "__main__":
    makeYaoDatabases()


