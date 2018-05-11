# -*- coding: utf-8 -*-

"""
Enumerate all possible trees (as FunctionHypotheses), saving them to a file (for later gibbs as in Search_UnoptimizedGibbs and Search_VectorizedGibbs)

"""
import sys
import pickle

from LOTlib.FunctionNode import FunctionNode
from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib.Miscellaneous import logplusexp
from LOTlib.TopN import TopN
from LOTlib.Projects.Quantifier.Model import *

OUT = "data/all_trees_cfg.pickle" #"data/all_trees_csg.pickle"
DEPTH = 4 #10
MAX_NODES = 10

all_tree_count = 0

## Collapse trees by how they act on data -- collapse equivalent functions
collapsed_forms = dict()

def get_tree_set_responses(t, context_sets):
    resps = []
    if isinstance(t, FunctionNode):
        f = eval('lambda context: ' + str(t))
    else:
        f = t.fvalue
    for context in context_sets:
        resps.append(f(context))
    return resps

# A function to collapse trees together based on their functional response
def add_to_collapsed_trees(t):
    resps = ';'.join(map(str, get_tree_set_responses(t, TESTING_SET)))
    tprior = grammar.log_probability(t)

    if resps in collapsed_forms: # add to the existing collapsed form if no recursion
        collapsed_prob = grammar.log_probability(collapsed_forms[resps])
        collapsed_forms[resps].my_log_probability = logplusexp(collapsed_prob, tprior)
        if tprior > collapsed_forms[resps].display_tree_probability: # display the most concise form
            collapsed_forms[resps] = t
            collapsed_forms[resps].display_tree_probability = tprior
    else:
        collapsed_forms[resps] = t
        collapsed_forms[resps].display_tree_probability = tprior
        t.my_log_probability = tprior # FunctionNode uses this value when we call log_probability()
        print ">>", all_tree_count, len(collapsed_forms),  t, tprior

############################################
### Now actually enumarate trees
for t in grammar.enumerate(d=DEPTH):
    if 'presup_(False' in str(t):
        continue
    if not check_expansion(t):
        continue
    if t.count_subnodes() <= MAX_NODES:
        add_to_collapsed_trees(t)
        all_tree_count += 1
        print ">", t, grammar.log_probability(t)

## for kinder saving and unsaving:
upq = TopN()
for k in collapsed_forms.values():
    upq.add(LOTHypothesis(grammar, k, display='lambda context: %s'), 0.0)
pickle.dump(upq, open(OUT, 'w'))

print "Total tree count: ", all_tree_count
