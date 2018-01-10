import fileparsers, ExtremaPO
import itertools, os, json

def makenetworklabelsfromfiles(networkfolder):
    networklabels = []
    uids = []
    for fname in os.listdir(networkfolder):
        uids.append(''.join([c for c in fname if c.isdigit()]))
        networklabels.append(tuple(
            [l.replace(':', ' ').split()[0] for l in open(os.path.join(networkfolder, fname), 'r') if
             l]))
    return networklabels, uids


def parsetimeseries(desiredlabels, timeseriesfile, ts_type, ts_truncation=float(-1)):
    if ts_type == 'col':
        TSList, TSLabels, timeStepList = fileparsers.parseTimeSeriesFileCol(timeseriesfile)
    elif ts_type == 'row':
        TSList, TSLabels, timeStepList = fileparsers.parseTimeSeriesFileRow(timeseriesfile)
    if ts_truncation != float(-1):
        ind = timeStepList.index(ts_truncation)
    else:
        ind = len(timeStepList)
    if not set(desiredlabels).issubset(TSLabels):
        raise ValueError("Missing time series for some nodes. Aborting.")
    labels, data = zip(*[(node, TSList[TSLabels.index(node)][:ind]) for node in TSLabels if node in desiredlabels])
    return labels, data


def makepatterns(networkfolder,timeseriesfile,ts_type,ts_truncation,scalingFactors=[0.05,0.1,0.5]):
    networklabels, uids = makenetworklabelsfromfiles(networkfolder)
    uniqnetlab = list(set(networklabels))
    desiredlabels = set(itertools.chain.from_iterable(uniqnetlab))
    masterlabels, masterdata = parsetimeseries(desiredlabels,timeseriesfile,ts_type,ts_truncation)
    uniqpatterns = []
    for nl in uniqnetlab:
        ts_data = [masterdata[masterlabels.index(n)] for n in nl]
        uniqpatterns.append(
            ExtremaPO.makeJSONstring(ts_data, nl, n=1, scalingFactors=scalingFactors, step=0.01))
    patterns = [uniqpatterns[uniqnetlab.index(nl)] for nl in networklabels]
    return uids, patterns

def savepatterns(uids, patterns, patternfolder,scalingFactors):
    for uid,pats in zip(uids,patterns):
        subdir = os.path.join(patternfolder, uid)
        os.makedirs(subdir)
        for (pat, scfc) in zip(pats, scalingFactors):
            puid = '{:.{prec}f}'.format(scfc, prec=scfc_padding).replace('.', '_')
            pfile = os.path.join(subdir, "pattern" + puid + ".txt")
            json.dump(pat, open(pfile, 'w'))

# TODO make pattern folder using computations