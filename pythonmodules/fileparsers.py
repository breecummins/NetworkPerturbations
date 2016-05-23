def sort_by_list(X,Y,reverse=False):
    # X is a list of length n, Y is a list of lists of length n
    # sort every list in Y by either ascending order (reverse = False) or descending order (reverse=True) of X 
    newlists = [[] for _ in range(len(Y)+1)]
    for ztup in sorted(zip(X,*Y),reverse=reverse):
        for k,z in enumerate(ztup):
            newlists[k].append(z)
    return newlists

def parseLEMfile(threshold=0,fname='/Users/bcummins/ProjectData/malaria/wrair2015_v2_fpkm-p1_s19_40hr_highest_ranked_genes/wrair2015_v2_fpkm-p1_s19_50tfs_top25_dljtk_lem_score_table.txt'):
    # returns the source, target, and type of regulation sorted by decreasing LEM score (also returned)
    # file format must be:
    # 1) optional comment lines denoted by #
    # 2) optional line of column headers in which column 2 does not have the header "="
    # 3) all following lines are data that begin with TARGET_GENE = TYPE_REG(SOURCE_GENE)
    # 4) pld.lap score is the first numerical score on each data line 
    source=[]
    type_reg=[]
    target=[]
    lem_score=[]
    with open(fname,'r') as f:
        for l in f.readlines():
            if l[0] == '#':
                continue
            wordlist=l.split()
            if wordlist[1] != "=":
                continue
            k=3
            while not wordlist[k][0].isdigit():
                k+=1
            lem = float(wordlist[k])
            if lem>threshold:
                target.append(wordlist[0]) 
                lem_score.append(lem)
                two_words=wordlist[2].split('(')
                type_reg.append(two_words[0])
                source.append(two_words[1][:-1])
    [lem_score,source,target,type_reg] = sort_by_list(lem_score,[source,target,type_reg],reverse=True) # reverse=True because we want descending lem scores
    return source,target,type_reg,lem_score

def parseLEMfile_sqrtlossdroot(threshold=1,fname='/Users/bcummins/ProjectData/malaria/wrair2015_v2_fpkm-p1_s19_40hr_highest_ranked_genes/wrair2015_v2_fpkm-p1_s19_50tfs_top25_dljtk_lem_score_table.txt'):
    # returns the source, target, and type of regulation sorted by increasing sqrt loss/root score (also returned). Smaller scores are higher ranking.
    # file format must be:
    # 1) optional comment lines denoted by #
    # 2) optional line of column headers in which column 2 does not have the header "="
    # 3) all following lines are data that begin with TARGET_GENE = TYPE_REG(SOURCE_GENE)
    # 4) sqrt loss / root score is the last numerical score (and word) on each data line 
    source=[]
    type_reg=[]
    target=[]
    sqrtloss_root=[]
    with open(fname,'r') as f:
        for l in f.readlines():
            if l[0] == '#':
                continue
            wordlist=l.split()
            if wordlist[1] != "=":
                continue
            sqlr = float(wordlist[-1])
            if sqlr<threshold:
                target.append(wordlist[0]) 
                sqrtloss_root.append(sqlr)
                two_words=wordlist[2].split('(')
                type_reg.append(two_words[0])
                source.append(two_words[1][:-1])
    [sqrtloss_root,source,target,type_reg] = sort_by_list(sqrtloss_root,[source,target,type_reg],reverse=False) 
    return source,target,type_reg,sqrtloss_root

def parseLEMfile_pickbadnetworks(usepldLap=1,threshold=0,fname='/Users/bcummins/ProjectData/malaria/wrair2015_v2_fpkm-p1_s19_40hr_highest_ranked_genes/wrair2015_v2_fpkm-p1_s19_50tfs_top25_dljtk_lem_score_table.txt'):
    # returns the source, target, and type of regulation sorted by decreasing LEM score (also returned)
    # file format must be:
    # 1) optional comment lines denoted by #
    # 2) optional line of column headers in which column 2 does not have the header "="
    # 3) all following lines are data that begin with TARGET_GENE = TYPE_REG(SOURCE_GENE)
    # 4) pld.lap score is the first numerical score on each data line 
    source=[]
    type_reg=[]
    target=[]
    score=[]
    with open(fname,'r') as f:
        for l in f.readlines():
            if l[0] == '#':
                continue
            wordlist=l.split()
            if wordlist[1] != "=":
                continue
            if usepldLap:
                k=3
                while not wordlist[k][0].isdigit():
                    k+=1
            else:
                k=-1
            S = float(wordlist[k])
            if usepldLap:
                condition = S<=threshold
            else:
                condition = S>=threshold
            if condition:
                target.append(wordlist[0]) 
                score.append(S)
                two_words=wordlist[2].split('(')
                type_reg.append(two_words[0])
                source.append(two_words[1][:-1])
        # don't worry about sorting -- these are all the worst edges
    return source,target,type_reg,score

def parseRankedGenes(fname="/Users/bcummins/ProjectData/yeast/haase-fpkm-p1_yeast_s29_DLxJTK_257TFs.txt"):
    # file format: 
    # 1) optional comment lines denoted by hash 
    # 2) followed by an optional line of column headers with the second column header not beginning with a digit
    # 3) followed by lines beginning with GENE_NAME RANK
    genes = []
    ranks = []
    with open(fname,'r') as f:
        for l in f.readlines():
            if l[0] == '#':
                continue
            wordlist=l.split()
            if not wordlist[1][0].isdigit():
                continue
            genes.append(wordlist[0])
            ranks.append(int(wordlist[1]))
    ranked_genes = sort_by_list(ranks,[genes],reverse=False)[1] # reverse=False because we want ascending ranks
    return ranked_genes

def createNetworkFile(node_list,graph,regulation,essential=None,fname="network.txt",save2file=True):
    # take a graph and return a network spec file
    # which edges are essential
    if essential is None:
        essential = [False]*len(node_list)
    # calculate inedges and get regulation type
    dual=[[(j,reg[outedges.index(node)]) for j,(outedges,reg) in enumerate(zip(graph,regulation)) if node in outedges] for node in range(len(node_list))]
    # auto-generate network file for database
    networkstr = ""  
    for (name,inedgereg,ess) in zip(node_list,dual,essential):
        act = " + ".join([node_list[i] for (i,r) in inedgereg if r == 'a'])
        if act:
            act = "(" + act  + ")"
        rep = "".join(["(~"+node_list[i]+")" for (i,r) in inedgereg if r == 'r'])
        nodestr = name + " : " + act + rep 
        if ess:
            nodestr += " : E"
        nodestr += "\n"
        networkstr += nodestr
    if save2file:
        with open(fname,'w') as f:
            f.write(networkstr)
    return networkstr

def getGraphFromNetworkFile(network_filename=None,networkstr=None):
    # take a network spec file or string and return a graph
    # either one or the other must be supplied
    # if both are supplied, the filename will be used instead of the string
    if network_filename is not None:
        with open(network_filename,'r') as nf:
            networkstr = nf.read()
    if networkstr:
        eqns = networkstr.split("\n")
    else:
        raise ValueError("Empty network string.")
    node_list = []
    inedges = []
    essential = [] #essentialness is inherited
    for l in eqns:
        if l:
            words = l.replace('(',' ').replace(')',' ').replace('+',' ').split()
            if words[-2:] == [':', 'E']:
                essential.append(True)
                words = words[:-2]
            else:
                essential.append(False)
            node_list.append(words[0])
            inedges.append(words[2:]) # get rid of ':' at index 1
    graph = [[] for _ in range(len(node_list))]
    regulation = [[] for _ in range(len(node_list))]
    for target,edgelist in enumerate(inedges):
        for ie in edgelist:
            if ie[0] == '~':
                ind = node_list.index(ie[1:])
                regulation[ind].append('r') 
            else:
                ind = node_list.index(ie)
                regulation[ind].append('a') 
            graph[ind].append(target)  # change inedges to outedges
    return node_list,graph,regulation,essential

def makeYeastRankedGenes(ranked_genes_file="/Users/bcummins/ProjectData/yeast/haase-fpkm-p1_yeast_s29_DLxJTK_257TFs.txt",LEMfile="/Users/bcummins/ProjectData/yeast/haase-fpkm-p1_yeast_s29_top25dljtk_lem_score_table.txt",savefile="datafiles/haase-fpkm-p1_yeast_s29_DLxJTK_top25TFs.txt"):
    allrankedgenes = parseRankedGenes(ranked_genes_file)
    source,_,_,_ = parseLEMfile(threshold=-1,fname=LEMfile)
    genes = list(set(source))
    ranked_genes=[]
    for a in allrankedgenes:
        if a in genes:
            ranked_genes.append(a)
        if len(ranked_genes) == len(genes):
            with open(savefile,'w') as sf:
                for k,r in enumerate(ranked_genes):
                    sf.write(r+' '+str(k+1))
                    if k+1 < len(ranked_genes):
                        sf.write("\n")
    if len(ranked_genes) < len(genes):
        raise ValueError('Some genes are unranked.')

def generateMasterList(fname='/Users/bcummins/ProjectData/malaria/wrair2015_pfalcip_462TF_forLEM/cuffNorm_subTFs_stdNames.txt'):
    # This is for all 462 TFs in the original malaria data set. May be deprecated.
    f=open(fname,'r')
    wordlist = f.readline().split()[22::]
    f.close()
    genelist = wordlist[::22]
    timeseries=[]
    for k in range(len(genelist)):
        timeseries.append([float(w) for w in wordlist[22*k+1:22*(k+1)]])
    return genelist, timeseries

if __name__ == '__main__':
    # parseRankedGenes("datafiles/wrair-fpkm-p1_malaria_s19_DLxJTK_50putativeTFs.txt")
    # makeYeastRankedGenes()
    # source,target,type_reg,lem_score = parseLEMfile()
    # for k,(s,t,l) in enumerate(zip(source,target,lem_score)):
    #     if s == 'PF3D7_1139300' and t == 'PF3D7_1337100':
    #         print l
    #         print k
    #         print len(source)

    source,target,type_reg,sqrtloss_root=parseLEMfile_sqrtlossdroot()
    for k,(s,t,l) in enumerate(zip(source,target,sqrtloss_root)):
        if k < 20:
            print s,t,l