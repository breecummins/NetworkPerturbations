import DSGRN
import json,os

def hysteresis(dbfile,FP_OFF,FP_ON,gene):
    database = DSGRN.Database(dbfile)
    gene_index = database.network.index(gene)
    print(database.network.specification())
    hys_query = DSGRN.HysteresisQuery(database,gene,FP_OFF,FP_ON)
    num_reduced_param = hys_query.GeneQuery.number_of_reduced_parameters()
    hysteresis_True = [ hys_query.GeneQuery.database.full_parameter_index(rpi,0,gene_index) for rpi in range(num_reduced_param) if hys_query(rpi) ]
    return database.network.specification(), num_reduced_param, hysteresis_True

def hys_wrapper(databasefolder,FP_OFF,FP_ON,gene,savefilename):
    HysteresisDict = {}
    for db in os.listdir(databasefolder):
        if db[-2:] == 'db':
            dbfile = os.path.join(databasefolder,db)
            network_spec,num_reduced_param,hysteresis_True = hysteresis(dbfile,FP_OFF,FP_ON,gene)
            HysteresisDict[network_spec] = (num_reduced_param,len(hysteresis_True),hysteresis_True)
    for d in HysteresisDict:
        print d,d[:-1]
    with open(savefilename,'w') as f:
        json.dump(HysteresisDict,f)

def hysteresis_Yao(databasefolder='/Users/bcummins/ProjectSimulationResults/YaoNetworks/Yaonetworks_nonessential_databases',savefilename='/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_hysteresisresults.json'):
    FP_OFF= {"EE":[0,0],"Rp":[1,1]}
    FP_ON={"EE":[1,8],"Rp":[0,0]}
    hys_wrapper(databasefolder,FP_OFF,FP_ON,"S",savefilename)

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
    hysteresis_Yao()
