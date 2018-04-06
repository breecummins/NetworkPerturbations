import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.size'] = 36
mpl.rc('text', usetex=True)


def makeHistogram(data,nbins,extrapoints,xlabel,title,axislims,figsize=None,labelpad=0,savename=""):
    if figsize:
        plt.figure(figsize=figsize)
    plt.hist(data, nbins, normed=0, facecolor='green', alpha=0.75)
    plt.hold('on')
    N=len(extrapoints)
    if N > 1:
        cm_subsection = [float(x)/(N-1) for x in range(N)]
        colors = [ mpl.cm.jet(x) for x in cm_subsection ]    
    else:
        colors = ['b']
    if N:
        for c,pair in zip(colors,extrapoints):
            plt.plot(pair[0],pair[1],marker='*',markersize=24,color=c)
    plt.xlabel(xlabel,labelpad=labelpad)
    plt.ylabel('\# networks',labelpad=labelpad)
    plt.title(title)
    plt.axis(axislims)
    plt.grid(True)
    plt.tight_layout()
    if savename:
        plt.savefig(savename)
    plt.show()


def makeHistogramWithBrokenLines(data,nbins,xlabel,title,xlims,ylims,ylims_outliers,figsize=None,labelpad=0,savename=""):

    if figsize:
        plt.figure(figsize=figsize)

    f, (ax, ax2) = plt.subplots(2, 1, sharex=True)

    plt.title(title)
    ax2.set_xlabel(xlabel,labelpad=labelpad)
    ax2.set_ylabel('\# networks')

    # plot the same data on both axes
    ax.hist(data, nbins, normed=0, facecolor='green', alpha=0.75)
    ax2.hist(data, nbins, normed=0, facecolor='green', alpha=0.75)

    # set x limits
    ax.set_xlim(*xlims)
    ax2.set_xlim(*xlims)

    # zoom-in / limit the view to different portions of the data
    ax.set_ylim(*ylims_outliers)  # outliers only
    ax2.set_ylim(*ylims)  # most of the data

    # hide the spines between ax and ax2
    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.xaxis.tick_top()
    ax.tick_params(labeltop='off')  # don't put tick labels at the top
    ax2.xaxis.tick_bottom()

    # This looks pretty good, and was fairly painless, but you can get that
    # cut-out diagonal lines look with just a bit more work. The important
    # thing to know here is that in axes coordinates, which are always
    # between 0-1, spine endpoints are at these locations (0,0), (0,1),
    # (1,0), and (1,1).  Thus, we just need to put the diagonals in the
    # appropriate corners of each of our axes, and so long as we use the
    # right transform and disable clipping.

    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

    # What's cool about this is that now if we vary the distance between
    # ax and ax2 via f.subplots_adjust(hspace=...) or plt.subplot_tool(),
    # the diagonal lines will move accordingly, and stay right at the tips
    # of the spines they are 'breaking'

    if savename:
        plt.savefig(savename)
    plt.show()
