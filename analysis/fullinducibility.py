import queryDSGRN as qDSGRN
import json,os

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
    # fullinducibilityquery_Yao()
    # fullinducibilityquery_E2F()
    fullinducibilityquery_E2F_network1()
