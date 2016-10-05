"""

        Procedures for extracting and manipulating subtrees

"""
from LOTlib.Miscellaneous import UniquifyFunction
from LOTlib.FunctionNode import isFunctionNode
from LOTlib import break_ctrlc
from copy import copy

def generate_trees(grammar, start='START', N=1000):
    """
            Yield a bunch of unique trees, produced from the grammar
    """
    for _ in break_ctrlc(xrange(N)):
        yield grammar.generate(start)


@UniquifyFunction
def generate_unique_trees(grammar, start='START', N=1000):
    """
            Yield a bunch of unique trees, produced from the grammar
    """
    for _ in break_ctrlc(xrange(N)):
        t = grammar.generate(start)
        yield t

@UniquifyFunction
def generate_unique_complete_subtrees(grammar, start='START', N=1000):
    """
            genreate from start and yield all seen subtrees
    """
    for t in generate_unique_trees(grammar, start=start, N=N):
        for ti in t: yield ti

@UniquifyFunction
def generate_unique_partial_subtrees(grammar, start='START', N=1000, npartial=10, p=0.5):
    """
            Generate from grammar N times, and for each sample npartial partial subtrees with the given p parameter
            from EACH element of t
    """
    for t in generate_unique_trees(grammar, start=start, N=N):

        for ti in t:
            for _ in xrange(npartial):
                yield ti.random_partial_subtree(p=p)

def least_common_difference(t1,t2):
    """
        For a pair of trees, find the nodes (one in each tree) defining
        the root of their differences. Return None for identical trees.
    """
    if t1 == t2:
        return None, None
    elif( t1.name == t2.name and \
        t1.returntype == t2.returntype and \
        len(t1.args) == len(t2.args)):

        # first check if any strings (non functions nodes) below differ
        for a,b in zip(t1.argNonFunctionNodes(), t2.argNonFunctionNodes()):
            if a != b:
                return t1,t2 # if so, t1 and t2 differ

        # otherwise check the functionNodes
        differing = [arg1 != arg2 for arg1,arg2 in zip(t1.argFunctionNodes(),t2.argFunctionNodes())]
        if sum(differing) == 1:
            idx = differing.index(True)
            return least_common_difference(t1.args[idx],t2.args[idx])
        else:
            return t1, t2
    return t1,t2

# # # # # # # # # # # # # # # # # # # # # # # # #
# Quick helper functions for subtrees

def count_identical_subtrees(t,x):
    """
            in x, how many are identical to t?
    """
    return sum([tt==t for tt in x])

def count_identical_nonterminals(t,x):
    """
            How many nonterminals in x are of type t?

            Here we add up how many nodes have the same return type
            OR how many leaves (from partial trees) have the same returntype
    """

    return sum([tt.returntype==t for tt in x]) +\
           sum([tt==t for tt in x.all_leaves()])

def count_subtree_matches(t, x):
    """
    :param t: the thing we want to find
    :param x: what we look in
    :return:
    """
    return sum(map(lambda tt: tt.partial_subtree_root_match(t), x))



def trim_leaves(t):
    # A version that doesn't modify t
    return trim_leaves_(copy(t))

def trim_leaves_(t):
    """
        Take a tree t and replace terminal nodes (leaves) with their returntypes.
        
        next_(next_(((nine_ if True else four_) if equal_(ten_, ten_) else one_)))
        to:
        next_(next_(((WORD if BOOL else WORD) if equal_(WORD, WORD) else WORD)))        
        
        NOTE: This modifies t!
    """
    if not isFunctionNode(t):
        return t
    elif t.is_terminal():
        return t.returntype
    
    if isFunctionNode(t) and t.args is not None:
        t.args = [ x.returntype if (isFunctionNode(x) and x.is_terminal()) else trim_leaves_(x) for x in t.args]
    return t
                

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
if __name__ == '__main__':


    from LOTlib.Examples.Number.Model.Utilities import *

    #for t in generate_unique_trees(grammar, start='WORD'): print t

    #for t in generate_unique_complete_subtrees(grammar, start='WORD'): print t

    for t in generate_unique_partial_subtrees(grammar, start='WORD'): print t
