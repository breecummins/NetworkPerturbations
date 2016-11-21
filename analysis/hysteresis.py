import DSGRN
import json,os

def hysteresis(dbfile,FP_OFF,FP_ON,gene):
    database = DSGRN.Database(dbfile)
    print(database.network.specification())
    hys_query = DSGRN.HysteresisQuery(database,gene,FP_OFF,FP_ON)
    num_reduced_param = hys_query.GeneQuery.num_reduced_param
    hysteresis_True = []
    for n in range(num_reduced_param):
        if hys_query(n):
            # add info about reduced parameter
            hysteresis_True.append()
    return database.network.specification(), num_reduced_param, hysteresis_True

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
