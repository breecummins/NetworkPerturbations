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

# def fullinducibilityquery(database,FP_OFF,FP_ON):
#     size_factor_graph,num_reduced_parameters = database.single_gene_query_prepare("S")
#     print str(num_reduced_parameters) + "\n"
#     matchesBiStab = frozenset(database.DoubleFPQuery(FP_ON,FP_OFF))
#     matchesOFF = frozenset(set(database.MonostableFPQuery(FP_OFF)))
#     matchesON = frozenset(set(database.MonostableFPQuery(FP_ON)))
#     min_gpi = 0
#     max_gpi = size_factor_graph-1
#     OFF = set([])
#     ON = set([])
#     BiStab = set([])
#     for m in range(num_reduced_parameters):
#         if not m%1000:
#             print "Reduced parameter {}".format(m)
#         graph = database.single_gene_query("S", m)
#         if graph.mgi(min_gpi) in matchesOFF:
#             OFF.add(m)
#         if graph.mgi(max_gpi) in matchesON:
#             ON.add(m)
#         for i in range(min_gpi+1,max_gpi):
#             if graph.mgi(i) in matchesBiStab:
#                 BiStab.add(m)
#                 break
#     resettablebistability = BiStab.intersection(OFF)
#     inducibility = BiStab.intersection(ON)
#     fullinducibility = resettablebistability.intersection(inducibility)
#     return (len(BiStab),len(resettablebistability),len(inducibility),len(fullinducibility),num_reduced_parameters)

# def fi_wrapper(databasefolder,FP_OFF,FP_ON,savefilename):
#     fullInducDict = {}
#     for db in os.listdir(databasefolder):
#         if db[-2:] == 'db':
#             database = qDSGRN.dsgrnDatabase(os.path.join(databasefolder,db))
#             print(database.network.specification())
#             fullInducDict[database.network.specification()] = fullinducibilityquery(database,FP_OFF,FP_ON)
#     print fullInducDict
#     with open(savefilename,'w') as f:
#         json.dump(fullInducDict,f)

def fullinducibility(dbfile,FP_OFF,FP_ON,gene):
    database = qDSGRN.dsgrnDatabase(dbfile)
    print(database.network.specification())
    size_factor_graph,num_reduced_parameters = database.single_gene_query_prepare(gene)
    print str(num_reduced_parameters) + "\n"
    max_gpi = size_factor_graph-1
    OFF, ON, BiStab = database.full_inducibility(gene,FP_OFF,FP_ON,max_gpi)
    resettablebistability = BiStab.intersection(OFF)
    inducibility = BiStab.intersection(ON)
    fullinducibility = resettablebistability.intersection(inducibility)
    counts = (len(BiStab),len(resettablebistability),len(inducibility),len(fullinducibility),num_reduced_parameters)
    return counts, database.network.specification()

def fi_wrapper(databasefolder,FP_OFF,FP_ON,gene,savefilename):
    fullInducDict = {}
    for db in os.listdir(databasefolder):
        if db[-2:] == 'db':
            dbfile = os.path.join(databasefolder,db)
            counts,network_spec = fullinducibility(dbfile,FP_OFF,FP_ON,gene)
            fullInducDict[network_spec] = counts
    print fullInducDict
    with open(savefilename,'w') as f:
        json.dump(fullInducDict,f)

def fullinducibilityquery_Yao(databasefolder='/Users/bcummins/ProjectSimulationResults/YaoNetworks/Yaonetworks_nonessential_databases',savefilename='/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_fullinducibilityresults.json'):
    FP_OFF= {"EE":[0,0],"Rp":[1,1]}
    FP_ON={"EE":[1,8],"Rp":[0,0]}
    fi_wrapper(databasefolder,FP_OFF,FP_ON,"S",savefilename)

def fullinducibilityquery_E2F(databasefolder='/Users/bcummins/ProjectSimulationResults/E2FNaturePaper', savefilename='/Users/bcummins/ProjectSimulationResults/E2FNaturePaper/6D_2016_08_26_cancerE2F_fullinducibilityresults_nets2_3_4.json'):
    FP_OFF={"E2F":[0,0],"E2F_Rb":[1,1]} 
    FP_ON={"E2F":[1,8],"E2F_Rb":[0,0]}
    fi_wrapper(databasefolder,FP_OFF,FP_ON,"S",savefilename)

def fullinducibilityquery_E2F_network1(dbfile = "/share/data/CHomP/Projects/DSGRN/DB/data/6D_2016_08_26_cancerE2Fnetwork1.db",savefilename="6D_2016_08_26_cancerE2F_fullinducibilityresults_net1.json"):
    FP_OFF={"E2F":[0,0],"E2F_Rb":[1,1]} 
    FP_ON={"E2F":[1,8],"E2F_Rb":[0,0]}
    counts,network_spec = fullinducibility(dbfile,FP_OFF,FP_ON,"S")
    result = {network_spec : counts}
    print result
    with open(savefilename,'w') as f:
        json.dump(result,f)



if __name__ == "__main__":
    # makeYaoDatabases()
    # makeYaoDatabases('/Users/bcummins/ProjectSimulationResults/YaoNetworks/4D_2016_08_25_Yao.json')
    # fullinducibilityquery_Yao()
    # fullinducibilityquery_E2F()
    fullinducibilityquery_E2F_network1()
