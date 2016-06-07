import os

def gimme_positive_int(inputstr):
    def checkforint(inputstr):
        while True:
            try:
                myint = int(inputstr)
                break
            except:
                fail=True
                while fail:
                    inputstr = raw_input("\nResponse not recognized. Please enter a positive integer.  ")
                    try:
                        myint = int(inputstr)
                        fail=False
                    except:
                        fail=True
        return myint
    myint = checkforint(inputstr)
    while myint <=0:
        myint = checkforint("")
    return myint

def gimme_nonneg_int(inputstr):
    def checkforint(inputstr):
        while True:
            try:
                myint = int(inputstr)
                break
            except:
                fail=True
                while fail:
                    inputstr = raw_input("\nResponse not recognized. Please enter a non-negative integer.  ")
                    try:
                        myint = int(inputstr)
                        fail=False
                    except:
                        fail=True
        return myint
    myint = checkforint(inputstr)
    while myint < 0:
        myint = checkforint("")
    return myint

def gimme_positive_or_minusone_float(inputstr):
    def checkforfloat(inputstr):
        while True:
            try:
                myfloat = float(inputstr)
                break
            except:
                fail=True
                while fail:
                    inputstr = raw_input("\nResponse not recognized. Please enter a floating point number.  ")
                    try:
                        myfloat = float(inputstr)
                        fail=False
                    except:
                        fail=True
        return myfloat
    myfloat = checkforfloat(inputstr)
    while not (myfloat > 0 or myfloat == -1):
        myfloat = checkforfloat("")
    return myfloat

def gimme_floats_0_1(inputlist):
    def checkbounds(inputlist):
        for s in inputlist:
            if s < 0 or s>1:
                return True
        if not inputlist:
            return True
        return False
    fail=checkbounds(inputlist)
    while fail:
        inputlist = input("\nResponse not recognized. Enter a list of floats between 0 and 1 inclusive.  ")
        fail=checkbounds(inputlist)
    return inputlist

def gimme_str_from_list(inputstr,correctinputs):
    while inputstr not in correctinputs:
        inputstr = raw_input("\nResponse not recognized. Please enter one of {}.  ".format(' or '.join(correctinputs)))
    return inputstr

def gimme_existing_file(inputstr):
    while not os.path.isfile(os.path.expanduser(inputstr)):
        inputstr = raw_input("\nFile not found. Enter new path.  ")
    return os.path.expanduser(inputstr)

def gimme_existing_path(inputstr):
    while True:
        if not os.path.isdir(os.path.expanduser(inputstr)):
            inputstr = raw_input("\nPath not found. Enter new path.  ")
        else:
            return os.path.expanduser(inputstr)

def getinfo():
    params = dict()
    # get path to DSGRN
    params['dsgrn'] = gimme_existing_path(raw_input("\nEnter the path of the DSGRN folder.  "))
    if not os.path.isdir(os.path.expanduser(os.path.join(params['dsgrn'],'software/Signatures'))):
        print "\nDSGRN has a non-standard file structure. Program cannot be completed.\n")
        raise ValueError
    # get network spec(s)
    netfolder = gimme_str_from_list(raw_input("\nAre your perturbations already constructed in a separate folder (y or n)?  "),['y','n'])
    if netfolder == 'y':
        # perturbations pre-calculated
        params['networkfolder'] = gimme_existing_path(raw_input("\nEnter the path of the network perturbations folder.  "))
    elif netfolder == 'n':
        # perturbations are not pre-calculated
        params['starting_networkspec'] = gimme_existing_file(raw_input("\nGive the path to a file containing the network specification that is to be perturbed.  "))
        # choose random or deterministic perturbations and get associated parameters
        params['rand_or_det'] = gimme_str_from_list(raw_input("\nDo you want random perturbations ('r') or deterministic perturbations ('d')?  "),['r','d'])
        if params['rand_or_det'] == 'r':
            params['numperturbations'] = gimme_positive_int(raw_input("\nHow many perturbations do you want? Example: 1000.  " ))
        elif params['rand_or_det'] == 'd':
            params['numtopnodes'] = gimme_nonneg_int(raw_input("\nHow many top nodes would you like to add? Integer >= 0:  "))
            if params['numtopnodes'] > 0:
                params['rankedgenesfile'] = gimme_existing_file(raw_input("\nGive the path to a file containing the ranked nodes.  "))
            params['numtopedges']= gimme_nonneg_int(raw_input("\nHow many top edges would you like to add? Integer >= 0:  "))
            if params['numtopedges'] > 0:
                params['lemfile'] = gimme_existing_file(raw_input("\nGive the path to a file containing the LEM-ranked edges.  "))
                params['lap_or_root'] = gimme_str_from_list(raw_input("\nDo you want to use pld.Lap scores ('p') or square root loss / root scores ('s')?  "),'p or s')
            if params['numtopedges'] == 0 and params['numtopnodes'] == 0:
                print "\nNeither top nodes nor edges are specified. No deterministic perturbations can be done. Start over with random perturbations.\n"
                raise ValueError
            params['pairwise'] = gimme_str_from_list(raw_input("\nDo you want both singleton and pairwise combinations of top edges and/or nodes ('b') or just singletons ('s')?  "),['b','s'])
        # get max size of each database
        params['maxparams'] = gimme_positive_int(raw_input("\nHow many parameters will you admit per perturbation? Example: 200000.  "))
    # which database queries to perform; more can be added in a modular fashion
    params['stableFCs'] = gimme_str_from_list(raw_input("\nDo you want to know the number of parameters exhibiting at least one stable FC (y or n)?  "),['y','n']) 
    params['multistable']= gimme_str_from_list(raw_input("\nDo you want to know the number of parameters exhibiting more than one stable Morse set of any type (y or n)?  "),['y','n'])
    params['singlefpqueries'] = input("\nWould you like to make single FP queries? If so, enter a list of arguments. \nIncorrect format, state, or variable names will crash the process later. \nExample of two single queries: ['E2F 3 3 Rb 0 0', 'E2F 0 0 Rb 1 1']. Enter [] for no queries.  ")
    params['dualfpqueries'] = input("\nWould you like to query for the simultaneous presence of two FPs? If so, enter a list of arguments. \nIncorrect format, state, or variable names will crash the process later. \nExample of two dual queries: ['E2F 3 3 Rb 0 0 E2F 0 0 Rb 1 1', 'Myc 0 1 E2F 2 2 E2F 0 2 Rb 1 1']. Enter [] for no queries.  ")
    # choose whether to pattern match and get associated parameters
    params['patternmatch'] = gimme_str_from_list(raw_input("\nDo you want to pattern match (y or n)?  "),['y','n'])
    # FIXME: if networkfolder in params, ask for path to pattern files, if they exist
    if params['patternmatch'] == 'y':
        params['timeseriesfile'] = gimme_existing_file(raw_input("\nGive the path to a file containing the time series data.  "))
        params['ts_type'] = gimme_str_from_list(raw_input("\nDo the time series occur in rows ('row') or columns ('col')?  "),['row','col'])
        params['ts_trunction'] = gimme_positive_or_minusone_float(raw_input("\nChoose a (positive) truncation time for the time series data, or the value -1 for no truncation.  "))
        params['scaling_factors'] = gimme_floats_0_1(input("\nGive a list of scaling factors between 0 and 1 to construct the partial orders from the data. Example: [0.0, 0.05, 0.1, 0.15].  "))
    return params

def constructcommands(params):
    pass

if __name__ == '__main__':
    params = getinfo()
    print("\n")
    print params