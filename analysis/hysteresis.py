import DSGRN
import json,os

def hysteresis(database,gene,FP_OFF,FP_ON,gene_index):
    hys_query = DSGRN.HysteresisQuery(database,gene,FP_OFF,FP_ON)
    num_reduced_param = hys_query.GeneQuery.number_of_reduced_parameters()
    hysteresis_True = [ hys_query.GeneQuery.database.full_parameter_index(rpi,0,gene_index) for rpi in range(num_reduced_param) if hys_query(rpi) ]
    return num_reduced_param, hysteresis_True

def fullinducibility(database,gene,FP_OFF,FP_ON,gene_index):
    ind_query = DSGRN.InducibilityQuery(database,gene,FP_OFF,FP_ON)
    num_reduced_param = ind_query.GeneQuery.number_of_reduced_parameters()
    fullinducibility_True = [ ind_query.GeneQuery.database.full_parameter_index(rpi,0,gene_index) for rpi in range(num_reduced_param) if all(ind_query(rpi)) ]
    return num_reduced_param, fullinducibility_True

def wrapper(databasefolder,FP_OFF,FP_ON,gene,savefilename,call):
    results = {}
    for db in os.listdir(databasefolder):
        if db[-2:] == 'db':
            dbfile = os.path.join(databasefolder,db)
            database = DSGRN.Database(dbfile)
            network_spec = database.network.specification()
            print(network_spec)
            num,Trueparams = call(database,gene,FP_OFF,FP_ON,database.network.index(gene))
            results[network_spec] = (num,len(Trueparams),Trueparams)
    for d in results:
        print d,results[d][:-1],"\n"
    with open(savefilename,'w') as f:
        json.dump(results,f)

def Yao_analysis(databasefolder='/Users/bcummins/ProjectSimulationResults/YaoNetworks/Yaonetworks_nonessential_databases',savefilename='/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_hysteresisresults.json',call=hysteresis):
    FP_OFF= {"EE":[0,0],"Rp":[1,1]}
    FP_ON={"EE":[1,8],"Rp":[0,0]}
    wrapper(databasefolder,FP_OFF,FP_ON,"S",savefilename,call)

def E2F_nets234_analysis(databasefolder='/Users/bcummins/ProjectSimulationResults/E2FNaturePaper', savefilename='/Users/bcummins/ProjectSimulationResults/E2FNaturePaper/6D_2016_08_26_cancerE2F_hysteresisresults_nets2_3_4.json',call=hysteresis):
    FP_OFF={"E2F":[0,0],"E2F_Rb":[1,1]} 
    FP_ON={"E2F":[1,8],"E2F_Rb":[0,0]}
    wrapper(databasefolder,FP_OFF,FP_ON,"S",savefilename,call)

def E2F_net1_analysis(dbfile = "/share/data/CHomP/Projects/DSGRN/DB/data/6D_2016_08_26_cancerE2Fnetwork1.db",savefilename="6D_2016_08_26_cancerE2F_hysteresis_net1.json",call=hysteresis):
    FP_OFF={"E2F":[0,0],"E2F_Rb":[1,1]} 
    FP_ON={"E2F":[1,8],"E2F_Rb":[0,0]}
    dbfile = os.path.join(databasefolder,db)
    database = DSGRN.Database(dbfile)
    network_spec = database.network.specification()
    print(network_spec)
    num,Trueparams = call(database,gene,FP_OFF,FP_ON,database.network.index(gene))
    result = { network_spec : (num,len(Trueparams),Trueparams) }
    print result[network_spec][:-1]
    with open(savefilename,'w') as f:
        json.dump(result,f)



if __name__ == "__main__":
    Yao_analysis(savefilename='/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_hysteresisresults.json',call=hysteresis)
