import os,sys
import DSGRN
import readline, glob

###########################################################
# set up tab completion for terminal entry
###########################################################

def complete(text, state):
    mypath = (glob.glob(os.path.expanduser(text)+'*')+[None])[state]
    if os.path.isdir(mypath):
        return mypath +'/'
    else:
        return mypath

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)

###########################################################
# All "gimme" functions are input checkers for getinfo().
###########################################################

def gimme_nonneg_int(inputstr,strictlypositive=False):

    err = "non-negative" if not strictlypositive else "positive"
    errormessage = "\nResponse not recognized. Please enter a " + err + " integer.  "

    success=False
    while not success:
        try:
            myint = int(inputstr)
            if (myint > 0)*(strictlypositive) or (myint >= 0)*(not strictlypositive):
                success = True
            else:
                inputstr = raw_input(errormessage)
        except:
            inputstr = raw_input(errormessage)

    return myint

def gimme_positive_or_minusone_float(inputstr):

    errormessage = "\nResponse not recognized. Please enter a positive truncation time or -1 for no truncation.  "
   
    success = False
    while not success:
        try:
            myfloat = float(inputstr)
            if myfloat > 0 or myfloat == -1:
                success = True
            else:
                inputstr = raw_input(errormessage)
        except:
            inputstr = raw_input(errormessage)

    return myfloat

def gimme_floats_0_1(inputlist):
    # lists are input() instead of raw_input()

    errormessage = "\nResponse not recognized. Enter a list of floats between 0 and 1 inclusive.  "

    def checkbounds(inputlist):
        if not inputlist:
            return False
        newinputlist = []
        for s in inputlist:
            try:
                s = float(s)
                if s < 0 or s>1:
                    return False
                else:            
                    newinputlist.append(s)
            except:
                return False
        return newinputlist

    inputlist = checkbounds(inputlist)
    while not inputlist:
        inputlist = checkbounds(input(errormessage))
    return inputlist

def gimme_str_from_list(inputstr,correctinputs):
    while inputstr not in correctinputs:
        inputstr = raw_input("\nResponse not recognized. Please enter one of {}.  ".format(' or '.join(correctinputs)))
    return inputstr

def gimme_existing_path(inputstr,isfile=False):
    errormessage = "\nPath not found. Enter new path.  " if not isfile else "\nFile not found. Enter new file.  "
    thispath = os.path.expanduser(inputstr)
    while (not os.path.isdir(thispath))*(not isfile) or (not os.path.isfile(thispath))*isfile:
        thispath = os.path.expanduser(raw_input(errormessage))
    return thispath

def gimme_existing_path_skipOK(inputstr,isfile=False):
    if inputstr == "":
        return inputstr
    else:
        return gimme_existing_path(inputstr,isfile)

def gimme_computable_network(inputstr):   

    errormessage = "\nProvided network is not computable. Enter another network file.  "

    def computable(inputstr):
        with open(inputstr,'r') as networkfile:
            network_spec = networkfile.read() 
        network=DSGRN.Network()
        try:
            network.assign(network_spec)
            paramgraph=DSGRN.ParameterGraph(network) 
            return True
        except (AttributeError, RuntimeError):
            return False

    while not computable(inputstr):
        inputstr = gimme_existing_path(raw_input(errormessage),isfile=True)   
    return inputstr    


##########################################
# Request files and parameters from user.
##########################################

def getinfo():
    params = dict()

    print "#############################################"
    print "\nPress Ctrl-C to exit program at any time.\n"
    print "#############################################"

    # get path to DSGRN
    params['dsgrn'] = gimme_existing_path(raw_input("\nEnter the path of the DSGRN folder.  "),isfile=False)
    if not os.path.isdir(os.path.expanduser(os.path.join(params['dsgrn'],'software/Signatures'))):
        print "\n\nDSGRN has a non-standard file structure. Program cannot be completed.\n"
        sys.exit()

    # get network spec(s)
    netfolder = gimme_str_from_list(raw_input("\nAre your network perturbations already constructed (y or n)?  "),['y','n'])
    if netfolder == 'y':
        # perturbations pre-calculated
        params['networkfolder'] = gimme_existing_path(raw_input("\nEnter the path of the network perturbations folder (each file name must have a unique integer).  "),isfile=False)
    elif netfolder == 'n':
        # perturbations are not pre-calculated
        params['networkfile'] = gimme_computable_network(gimme_existing_path(raw_input("\nEnter the path to a network specification file.  "),isfile=True))
        # get node and edge files
        nodefile = gimme_existing_path_skipOK( raw_input("\nEnter the path to a file with nodes to add (leave blank otherwise).  ") , isfile=True)
        if nodefile: params['nodefile'] = nodefile
        edgefile = gimme_existing_path_skipOK(raw_input("\nEnter the path to a file with edges to add (leave blank otherwise).  "),isfile=True)
        if edgefile: params['edgefile'] = edgefile
        if 'edgefile' not in params and 'nodefile' not in params:
            params['add_madeup_nodes'] = gimme_str_from_list(raw_input("\nAdd anonymous nodes to the network (y or n).  "),['y','n'])
        if 'edgefile' in params and 'nodefile' not in params:
            print "\n\nNote: only edges will be added to the existing network (not nodes).\n"
        # allow changes in regulation for the edges in the original network
        preservereg = gimme_str_from_list(raw_input("\nPreserve activating or repressing regulation on edges in the initial network specification (y or n). "),['y','n'])
        if preservereg == 'y':
            params['swap_edge_reg'] = False
        else:
            params['swap_edge_reg'] = True
        # how many perturbations
        params['numperturbations'] = gimme_nonneg_int(raw_input("\nHow many network perturbations do you want? Example: 1000.  " ),strictlypositive=True)
        params['maxadditionspergraph'] = gimme_nonneg_int(raw_input("\nWhat is the maximum number of edge/node perturbations you will permit per graph? Example: 10. "),strictlypositive=True)
        # limit computations
        params['maxparams'] = gimme_nonneg_int(raw_input("\nHow many parameters will you admit per perturbation? Example: 1000000.  "),strictlypositive=True)
        params['time_to_wait'] = gimme_nonneg_int(raw_input("\nHow many seconds will you wait for the network perturbations to complete? Example: 300. "),strictlypositive=True)

    # choose database queries to perform; more can be added in a modular fashion
    # QUERYFILE IS EXTREME SECURITY RISK. FIX!!!
    # params['stableFCs'] = gimme_str_from_list(raw_input("\nCount parameters exhibiting at least one stable FC (y or n).  "),['y','n']) 
    # params['multistable']= gimme_str_from_list(raw_input("\nCount parameters exhibiting more than one stable Morse set of any type (y or n).  "),['y','n'])
    queryfile = gimme_existing_path_skipOK(raw_input("\nEnter the path to a shell script with database queries (leave blank otherwise).  ") , isfile=True)
    if queryfile: params['queryfile'] = queryfile

    # choose whether to pattern match and get associated parameters
    patternmatch = gimme_str_from_list(raw_input("\nDo you want to pattern match (y or n)?  "),['y','n'])
    if patternmatch == 'y':
        if netfolder == 'y':
            patfolder = gimme_str_from_list(raw_input("\nAre your patterns already constructed (y or n)?  "),['y','n'])
            if patfolder == 'y':
                params['patternfolder'] = gimme_existing_path(raw_input("\nEnter the path of the patterns folder.  "),isfile=False)
        # the following is if, not elif
        if netfolder == 'n' or patfolder == 'n':
            params['timeseriesfile'] = gimme_existing_path(raw_input("\nGive the path to a file containing the time series data.  "),isfile=True)
            params['ts_type'] = gimme_str_from_list(raw_input("\nDo the time series occur in rows ('row') or columns ('col')?  "),['row','col'])
            params['ts_truncation'] = gimme_positive_or_minusone_float(raw_input("\nChoose a (positive) truncation time for the time series data, or the value -1 for no truncation.  "))
            params['scaling_factors'] = gimme_floats_0_1(input("\nGive a list of scaling factors (noise levels) between 0 and 1 to construct the patterns from the data. Example: [0.0, 0.05, 0.1, 0.15].  "))

    params['removeDB'] = gimme_str_from_list(raw_input("\nRemove database after query is complete (y or n)? Recommended answer is 'y'. "),['y','n'])
    return params

if __name__ == '__main__':
    pass
    # params = getinfo()
    # print("\n")
    # print params