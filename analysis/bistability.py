import DSGRN,os

def bistability_count(dbfile,FP_OFF,FP_ON):
    database = DSGRN.Database(dbfile)
    BiStab = DSGRN.DoubleFixedPointQuery(database,FP_OFF,FP_ON).matches()
    return len(BiStab)

if __name__ == '__main__':
    dbfile = os.path.expanduser("~/ProjectSimulationResults/E2FNaturePaper/yeastSTART/5D_2016_11_28_yeastSTART.db")
    FP_OFF={"SBF":[0,0],"SBF_Whi5":[1,1]} 
    FP_ON={"SBF":[1,8],"SBF_Whi5":[0,0]}
    print bistability_count(dbfile,FP_OFF,FP_ON)

