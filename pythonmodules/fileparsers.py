# FIXME: move time series parsers here from ExtremaPO.py

def parseEdgeFile(fname='/Users/bcummins/ProjectData/malaria/wrair2015_v2_fpkm-p1_s19_40hr_highest_ranked_genes/wrair2015_v2_fpkm-p1_s19_50tfs_top25_dljtk_lem_score_table.txt'):
    # returns a list of (source, target, regulation) edges 
    # file format must be:
    # 1) optional comment lines/column headers beginning with #
    # 2) data lines where the first column is an edge of the form TARGET_GENE = TYPE_REG(SOURCE_GENE)
    # 3) other columns in the line must be space, tab, or comma separated
    edgelist=[]
    with open(fname,'r') as f:
        for l in f.readlines():
            if l:
                if l[0] == '#':
                    continue
                wordlist=l.replace(',',' ').replace('=',' ').split()
                target=wordlist[0]
                regsource=wordlist[1].replace('(',' ').replace(')',' ').split()
                reg=regsource[0]
                source=regsource[1]
                edgelist.append((source,target,reg))
    return edgelist

def parseNodeFile(fname="/Users/bcummins/ProjectData/yeast/haase-fpkm-p1_yeast_s29_DLxJTK_257TFs.txt"):
    # file format must be: 
    # 1) optional comment lines/column headers beginning with hash 
    # 2) data lines beginning with NODE_NAME
    # 3) other columns in the line must be space, tab, or comma separated
    nodelist = []
    with open(fname,'r') as f:
        for l in f.readlines():
            if l:
                if l[0] == '#':
                    continue
                wordlist=l.replace(',',' ').split()
                nodelist.append(wordlist[0])
    return nodelist


if __name__ == '__main__':
    pass
    # parseRankedGenes("datafiles/wrair-fpkm-p1_malaria_s19_DLxJTK_50putativeTFs.txt")
    # makeYeastRankedGenes()
    # source,target,type_reg,lem_score = parseLEMfile()
    # for k,(s,t,l) in enumerate(zip(source,target,lem_score)):
    #     if s == 'PF3D7_1139300' and t == 'PF3D7_1337100':
    #         print l
    #         print k
    #         print len(source)

    # source,target,type_reg,sqrtloss_root=parseLEMfile_sqrtlossdroot()
    # for k,(s,t,l) in enumerate(zip(source,target,sqrtloss_root)):
    #     if k < 20:
    #         print s,t,l
