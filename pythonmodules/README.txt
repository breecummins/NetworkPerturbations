Keywords in the parameter dictionary. See default_param_dict.json.

REQUIRED:

queryfile           =   path to python script that performs desired DSGRN queries;
                        this includes pattern matching and making posets of extrema if desired (see make_patterns.py);
                        the main calling function inside this script should be named query();
                        see example_query.py

computationsdir     =   path to location where results are to be stored;
                        "./" indicates current directory


EXACTLY ONE OF THE TWO FOLLOWING IS REQUIRED:

networkfolder       =   path to a pre-calculated list of network perturbations
                        or empty string or missing keyword to generate perturbations;
                        specify only if networkfile is blank or missing

networkfile         =   path to network specification file that is to be used as base file for perturbations;
                        or empty string or missing keyword if perturbations already exist;
                        specify only if networkfolder is blank or missing

IF NETWORKFILE IS SPECIFIED, THE FOLLOWING ARE REQUIRED EXCEPT WHERE NOTED:

    nodefile            =   OPTIONAL: path to file containing the names of nodes to add, one line per name;
                            or empty string or missing keyword if no such file exists

    add_anon_nodes      =   "y" or "n" to add unnamed nodes to the perturbed networks

    edgefile            =   OPTIONAL: path to file containing named edges in the form (node1, node2, "a" or "r"), one per line
                            where "a" means activation and "r" means repression;
                            or empty string or missing keyword if no such file exists

    swap_edge_reg       =   true or false to allow the sign of regulation to be swapped on edges in the original network

    numperturbations    =   Maximum number of perturbed networks to find;
                            process may time out before this number is reached

    maxaddspergraph     =   Maximum number of node/edge perturbations to allow in each graph

    maxparams           =   Maximum size of graph allowed measured in number of parameters that DSGRN has to compute

    time_to_wait        =   Maximum time in seconds allowed to calculate perturbations

