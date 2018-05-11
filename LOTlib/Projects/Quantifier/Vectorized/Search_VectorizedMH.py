# -*- coding: utf-8 -*-
"""
This basically out a new version and makes a much smaller hypothesis space, one for each word, which we can then run again on

Let's add options for many different kinds of proposals:
    - Distance metric based
    - Flat uniform
    - Sample from the prior
    - Build a large, sparse, connected graph of each guys' nearest neighbors
    - What if you hash the semantics, and "propose" by altering it a little and re-querying the hash?

"""

import pickle, os, sys
import numpy as np

from random import randint
from copy import copy
from scipy.special import logsumexp

from LOTlib.Miscellaneous import sample1, weighted_sample
from LOTlib.Projects.Quantifier.Model import *
from LOTlib.TopN import TopN
from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.Projects.Quantifier.Model import *


IN_PATH = 'data/all_trees_cfg.pickle'
DISTANCE_CACHE = 'data/dist_all_trees_cfg.pickle'
OUT_PATH = 'data/top_mh_tree_cfg.pickle'
TOP_COUNT = 50

ALPHA = 0.9
PALPHA = 0.9

STEPS = 100000
SKIP = 500

####################################################################################
## A bunch of things for computing distances and gradients, etc

# Hash each hypothesis to its index
hyp2index = {}

# Proposals to cache
proposal_to = None
proposal_probs = None
proposal_Z = None

def get_tree_set_responses(t, context_sets):
    resps = []
    if isinstance(t, FunctionNode):
        f = eval('lambda context: ' + str(t))
    else:
        f = t.fvalue
    for context in context_sets:
        resps.append(f(context))
    return resps

def mapto012(resps):
    ret = []
    for resp in resps:
        if resp is True:
            ret.append(1)
        elif resp is False:
            ret.append(-1)
        else:
            ret.append(0)
    return ret

def get_proposal_dist(my_finite_trees):
    if os.path.exists(DISTANCE_CACHE):
        SCALE = 0.75 # tuned to give a reasonable acceptance ratio
        TOP_N = 1000 # store only the top this many

        # Compute distances the matrix way:
        data = generate_data(100)
        RM = np.zeros((len(my_finite_trees), len(data))) # repsonse matrix
        for i, x in enumerate(my_finite_trees):
            RM[i,:] = np.array(mapto012(get_tree_set_responses(x, data)))
        RM = np.matrix(RM)

        # Okay now convert to each of the kinds of agreement we want
        # NOTE: (RM==1)+0 Gives an integer matrix, 0/1 for whether RM==1
        # NOTE: we need to do these as += because otherwise we can get memory errors
        agree  = ((RM==1)+0) * ((RM==1)+0).transpose() # How often do we agree on 1s (yay matrix math)
        agree += ((RM==-1)+0) * ((RM==-1)+0).transpose() # how often do we agree on -1s
        agree += ((RM==0)+0) * ((RM==0)+0).transpose() # how often do we agree on undefs?
        print "# Done computing agreement matrix for proprosals"

        proposal_probability = np.exp(-SCALE * (len(data)-agree)) # the more you disagree, the less you are proposed to

        # now we have to sort:
        mftlen = len(my_finite_trees)
        proposal_to = np.zeros((mftlen, TOP_N))
        proposal_probs = np.zeros((mftlen, TOP_N))
        proposal_Z = np.zeros((mftlen, 1))

        for i in range(len(my_finite_trees)):
            r = np.array(proposal_probability[i,:].tolist()[0])
            r[i] = 0.0 # never propose to ourself
            # now sort
            r = -r # so we sort correctly, max first
            idx = r.argsort(kind='mergesort')[:TOP_N] # Sort and take the first TOP_N
            r = -r
            proposal_Z[i] = np.sum(r[idx]) # necessary since we take a subset
            proposal_to[i, :] = idx
            proposal_probs[i, :] = r[idx]
        pickle.dump([proposal_to, proposal_probs, proposal_Z], open(DISTANCE_CACHE, "wb"))
    else:
        proposal_to, proposal_probs, proposal_Z = pickle.load(open(DISTANCE_CACHE, "rb"))

def distance_based_proposer(x):
    y, lp = weighted_sample(proposal_to[x,:], probs=proposal_probs[x,:],
                            Z=proposal_Z[x], return_probability=True, log=False)
    bp = lp + log(proposal_Z[x]) - log(proposal_Z[y]) # the distance d is the same, but the normalizer differs
    return y, lp - bp

####################################################################################
# Define a class that can do MH on these fancy proposals

class VectorizedLexicon_DistanceMetricProposal(VectorizedLexicon):
    def __init__(self, *args, **kwargs):
        VectorizedLexicon.__init__(self, *args, **kwargs)

    def copy(self):
        return VectorizedLexicon_DistanceMetricProposal(self.target_words,
            self.finite_trees, self.priorlist, word_idx=np.copy(self.word_idx),
            ALPHA=self.ALPHA, PALPHA=self.PALPHA)

    def propose(self):
        new = self.copy()
        i = sample1(range(len(self.word_idx)))
        p, fb = distance_based_proposer(i)
        new.word_idx[i] = p
        return new, fb

def VectorizedLexicon_to_SimpleLexicon(vl):
    L = SimpleLexicon(grammar, args=['A', 'B', 'S']) ## REALLY THIS SHOULD BE GRICEAN
    for i, wi in enumerate(vl.word_idx):
        L.set_word(index2word[i], vl.finite_trees[wi])
    return L

########################################################################
# Define Run and a function mapping vectorized lexicon to normal

def run(data_size, my_finite_trees):
    data = generate_data(data_size)

    # the prior for each tree
    prior = np.array([x.compute_prior() for x in my_finite_trees])
    prior = prior - logsumexp(prior)

    # the likelihood weights for each hypothesis
    weights = np.array([my_weight_function(h) for h in my_finite_trees])
    # response[h,di] gives the response of the h'th tree to data di
    response = np.array([mapto012(get_tree_set_responses(t, data)) for t in my_finite_trees])

    # Now actually run:
    hypset = TopN(N=TOP_COUNT)

    learner = VectorizedLexicon_DistanceMetricProposal(target.all_words(), my_finite_trees, prior)
    databundle = [response, weights]
    generator = MHSampler(learner, databundle, STEPS, skip=SKIP)
    for g in generator:
        hypset.add(VectorizedLexicon_to_SimpleLexicon(g), g.posterior_score)
    return hypset

####################################################################################
## Main running
####################################################################################

# Load the trees from a file
my_finite_trees = pickle.load(open(IN_PATH))
print "# Done loading", len(my_finite_trees), "trees"

# Gives index to each hypothesis
for i, h in enumerate(my_finite_trees):
    hyp2index[h] = i

# Compute or load proposals
get_proposal_dist(my_finite_trees)

DATA_AMOUNTS = range(0, 2050, 100)
allret = map(run, DATA_AMOUNTS)

# combine into a single hypothesis set and save
outhyp = TopN()
for r in allret:
    outhyp.update(r)
pickle.dump(outhyp, open(OUT_PATH, 'w'))

