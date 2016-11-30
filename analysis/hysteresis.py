import DSGRN
import json,os

def hysteresis(database,gene,FP_OFF,FP_ON,gene_index):
    hys_query = DSGRN.HysteresisQuery(database,gene,FP_OFF,FP_ON)
    num_reduced_param = hys_query.GeneQuery.number_of_reduced_parameters()
    hysteresis_True = [ hys_query.GeneQuery.database.full_parameter_index(rpi,0,gene_index) for rpi in range(num_reduced_param) if hys_query(rpi) ]
    reset_bistab_True = [ hys_query.GeneQuery.database.full_parameter_index(rpi,0,gene_index) for rpi in range(num_reduced_param) if hys_query.resettable_bistability(rpi) ]
    return num_reduced_param, hysteresis_True, reset_bistab_True

def hysteresis_counts_only(database,gene,FP_OFF,FP_ON,gene_index):
    hys_query = DSGRN.HysteresisQuery(database,gene,FP_OFF,FP_ON)
    num_reduced_param = hys_query.GeneQuery.number_of_reduced_parameters()
    hys_counts, bistab_counts = 0,0
    for rpi in range(num_reduced_param):
        hys_counts += hys_query(rpi)
        bistab_counts += hys_query.resettable_bistability(rpi)
    return num_reduced_param, hys_counts, bistab_counts

def fullinducibility(database,gene,FP_OFF,FP_ON,gene_index):
    ind_query = DSGRN.InducibilityQuery(database,gene,FP_OFF,FP_ON)
    num_reduced_param = ind_query.GeneQuery.number_of_reduced_parameters()
    fullinducibility_True = [ ind_query.GeneQuery.database.full_parameter_index(rpi,0,gene_index) for rpi in range(num_reduced_param) if all(ind_query(rpi)) ]
    return num_reduced_param, fullinducibility_True, None

def wrapper(databasefolder,FP_OFF,FP_ON,gene,savefilename,call,record_params=True):
    results = {}
    for db in os.listdir(databasefolder):
        if db[-2:] == 'db':
            dbfile = os.path.join(databasefolder,db)
            database = DSGRN.Database(dbfile)
            network_spec = database.network.specification()
            print(network_spec)
            num,Trueparams,ResetBistab = call(database,gene,FP_OFF,FP_ON,database.network.index(gene))
            if record_params:
                if ResetBistab is not None:
                    results[network_spec] = (num,len(Trueparams),Trueparams,len(ResetBistab),ResetBistab)
                    print (num,len(Trueparams),len(ResetBistab))
                else:
                    results[network_spec] = (num,len(Trueparams),Trueparams)
                    print (num,len(Trueparams))
            else:
                if ResetBistab is not None:
                    results[network_spec] = (num,len(Trueparams),len(ResetBistab))
                    print (num,len(Trueparams),len(ResetBistab))
                else:
                    results[network_spec] = (num,len(Trueparams))
                    print (num,len(Trueparams))
    if ResetBistab is None:
        for d in results:
            print d,results[d][:-1],"\n"
    else:
        for d in results:
            print d,results[d][:2],results[d][3],"\n"        
    with open(savefilename,'w') as f:
        json.dump(results,f)

def Yao_analysis(databasefolder='/Users/bcummins/ProjectSimulationResults/YaoNetworks/Yaonetworks_nonessential_databases',savefilename='/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_hysteresisresults.json',call=hysteresis):
    FP_OFF= {"EE":[0,0],"Rp":[1,1]}
    FP_ON={"EE":[1,8],"Rp":[0,0]}
    wrapper(databasefolder,FP_OFF,FP_ON,"S",savefilename,call)

def E2F_nets234_analysis(databasefolder='/Users/bcummins/ProjectSimulationResults/E2FNaturePaper/6Dnetworks/', savefilename='/Users/bcummins/ProjectSimulationResults/E2FNaturePaper/6Dnetworks/6D_2016_08_26_cancerE2F_hysteresis_resetbistab_nets2_3_4.json',call=hysteresis):
    FP_OFF={"E2F":[0,0],"E2F_Rb":[1,1]} 
    FP_ON={"E2F":[1,8],"E2F_Rb":[0,0]}
    wrapper(databasefolder,FP_OFF,FP_ON,"S",savefilename,call)

def E2F_net1_analysis(dbfile = "/share/data/CHomP/Projects/DSGRN/DB/data/6D_2016_08_26_cancerE2Fnetwork1.db",savefilename="6D_2016_08_26_cancerE2F_hysteresis_resetbistab_net1.json",call=hysteresis_counts_only):
    FP_OFF={"E2F":[0,0],"E2F_Rb":[1,1]} 
    FP_ON={"E2F":[1,8],"E2F_Rb":[0,0]}
    database = DSGRN.Database(dbfile)
    network_spec = database.network.specification()
    print(network_spec)
    num,hys,bistab = call(database,"S",FP_OFF,FP_ON,database.network.index("S"))
    result = { network_spec : (num,hys,bistab) }
    print result[network_spec]
    with open(savefilename,'w') as f:
        json.dump(result,f)

def yeastSTART_analysis(dbfile = "/Users/bcummins/ProjectSimulationResults/E2FNaturePaper/5D_2016_11_28_yeastSTART.db",savefilename="/Users/bcummins/ProjectSimulationResults/E2FNaturePaper/5D_2016_11_28_yeastSTART_hysteresis.json",call=hysteresis):
    FP_OFF={"SBF":[0,0],"SBF_Whi5":[1,1]} 
    FP_ON={"SBF":[1,8],"SBF_Whi5":[0,0]}
    database = DSGRN.Database(dbfile)
    network_spec = database.network.specification()
    print(network_spec)
    num,Trueparams,ResetBistab = call(database,"S",FP_OFF,FP_ON,database.network.index("S"))
    result = { network_spec : (num,len(Trueparams),Trueparams,len(ResetBistab),ResetBistab) }
    print result[network_spec][:2],result[network_spec][3]
    with open(savefilename,'w') as f:
        json.dump(result,f)


if __name__ == "__main__":
    # Yao_analysis(savefilename='/Users/bcummins/ProjectSimulationResults/YaoNetworks/YaoNetworks_nonessential_hysteresisresults.json',call=hysteresis)
    # yeastSTART_analysis()
    E2F_net1_analysis()