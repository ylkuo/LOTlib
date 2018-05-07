"""
Move out some functions from Shared -- things that aren't part of the core model specification

"""
from collections import defaultdict

from scipy.stats import chisquare
from LOTlib.FunctionNode import FunctionNode
from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib.Miscellaneous import *
import Grammar as G
import Hypothesis as H
from Data import target, generate_data, my_weight_function, gricean_weight, make_my_hypothesis
from LOTlib.Primitives.Semantics import is_undef, collapse_undef


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~ Functions for doing Gricean things ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def show_baseline_distribution(testing_set, N=1000):
    frq = defaultdict(int)
    d = generate_data(N)
    for di in d:
        frq[di.utterance] += 1

    for w in frq.keys():
        # figure out how often its true:
        pct = float(sum(map(lambda s: ifelse(target.value[w](s) and not is_undef(target.value[w](s)), 1.0, 0.0), testing_set) )) / len(testing_set)
        print frq[w], "\t", q(w), "\t", pct


def is_conservative(h, testing_set):
    """Check if a hypothesis (funciton node) is conservative or not."""
    #print(str(h))
    if isinstance(h, FunctionNode):
        f = eval('lambda context: ' + str(h))
    else:
        f = h.fvalue
    for x in testing_set:
        new_context = H.MyContext(A=x.A, B=x.B.intersection(x.A), S=x.S.intersection(x.A))
        if f(x) != f(new_context): # HMM: is this right? We intersect s with a?
            return False
    return True


def extract_presup(resp):
    """From a bunch of responses, extract the T/F presups."""
    out = []
    for k in resp:
        if is_undef(k): out.append(False)
        else:           out.append(True)
    return out


def extract_literal(resp):
    """From a bunch of responses, extract the T/F literals."""
    out = []
    for k in resp:
        if (k is True) or (k == "undefT"): out.append(True)
        else:                              out.append(False)
    return out


def collapse_undefs(resp):
    """Collapse together our multiple kinds of undefs so that we can compare vectors."""
    out = []
    for k in resp:
        if is_undef(k):
            out.append("undef")
        else:
            out.append(k)
    return out


def check_counts( obj2counts, expected, threshold=0.001, verbose=False):
    """Check some counts according to a chi-squared statistic.

    We can use this to see if sampling counts, etc. are what they should be.

    Here, obj2counts is a dictionary mapping each thing to a count expected is a *function* that takes an
    object and hands back its expected counts (unnormalized), or a dictionary doing the same (unnormalized)

    TODO: We may want a normalized version?

    """
    objects = obj2counts.keys()
    actual_counts   = map(lambda o: float(obj2counts[o]), objects)
    N = sum(actual_counts)

    if isinstance(expected, dict):
        e = map(lambda o: expected.get(o,0.0), objects)
    else:
        assert callable(expected)
        e = map(lambda o: expected(o), objects)

    Z = float(sum(e))
    expected_counts = map(lambda o: float(o*N)/Z, e)
    chi, p = chisquare(f_obs=actual_counts, f_exp=expected_counts)

    if verbose:
        print "# Chi squared gives chi=%f, p=%f" % (chi,p)
        if p < threshold:
            assert "# *** SIGNIFICANT DEVIATION FOUND IN P"

    assert p > threshold, "*** Chi squared test fail with chi=%f, p=%f" % (chi,p)

    return True
