#! /usr/bin/env python

# Copyright (c) 2011, David Basden
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of the contributors 
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# Contact GitHub API Training Shop Blog About


def partial_order_to_grid(poset, n):
    '''poset is given in 2tuples of indexes into a list containing a linear extension
    as the indicies are into a list containing a valid topological sort,
    i must be < j for every (i,j) in the poset'''
    grid = [[False for j in xrange(n + 1)] + [True] for i in xrange(n + 2)]
    for i, j in poset:
        assert i < j
        grid[i][j] = True
        grid[j][i] = True
    return grid


def vr_topsort(n, m):
    '''Python implementation of Varol and Rotem (1979)
    generate all linear extensions of a poset based on an initial valid linear extension
    as described in
     Yaakov L. Varol and Doron Rotem, An Algorithm to Generate All Topological Sorting Arrangements.
        Computer J., 24 (1981) pp. 83-84.
    the 'seed' topological sort is mapped to integers from [1..n]
    e.g. given nodes {a,b,c,d}, with the partial order of {(c,a),(b,a),(a,d)}
    one valid topological ordering is c,b,a,d.  We then map 1=c 2=b 3=a 4=d
    such that cbad is represented as 1234. The partial order is now
    {(1,3),(2,3),(3,4)} (which can be passed to partial_order_to_grid to generate
    the incidence matrix 'm')

    n is the number of nodes in the set the partial order is across
    m is the incidence matrix of the binary relations after mapping to integers
    '''
    # n is the number of nodes in the DAG
    # m is a table (2d array) of bools giving the adjacency matrix
    # (n rows of n+1, indexed from 1).
    # There is also a terminating 'True' at the end of each row

    # The algorithm was written with list indicies starting at 1,
    # so this implementation does the same. http://xkcd.com/163/
    loc = range(n + 1)
    p = range(n + 2)
    yield p[1:n + 1]
    i = 1
    k = 1
    while i < n:
        k = loc[i]
        kk = k + 1
        if m[i][p[kk]]:
            p[i:k + 1] = [p[k]] + p[i:k]  # roll-right a[i:k+1]
            loc[i] = i
            i += 1
        else:
            p[k], p[kk] = p[kk], p[k]
            loc[i] = kk
            i = 1
            yield p[1:n + 1]


if __name__ == "__main__":
    n = 5
    poset = [(1, 2), (2, 3), (1, 5)]
    grid = partial_order_to_grid(poset, n)
    for le in vr_topsort(n, grid):
        print(le)
