"""
Attributes defined here:
    - all_objects
    - TESTING_SET_SIZE
    - TESTING_SET
    - target_functions
    - target
    - sample_context
    - generate_data

"""
from random import randint
from cachetools import lru_cache
from LOTlib import break_ctrlc
from LOTlib.DataAndObjects import *
from LOTlib.Primitives.SetTheory import *
from LOTlib.Primitives.Semantics import *
from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib.Miscellaneous import ifelse
import Hypothesis as H, Grammar as G


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~ These should be in Utilities, except then we'd have circular imports ~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def make_my_hypothesis():
    return LOTHypothesis(G.grammar, display='lambda context: %s')

def my_weight_function(h):
    return gricean_weight(h, TESTING_SET, nu=0.1)


def gricean_weight(h, testing_set, nu=1.0):
    """Takes a hypothesis and its function and returns the weight under a gricean setup.

    Production probability is proportional to:  exp( 1.0 / (nu + proportionoftimeitistrue) )

    Notes:
        The max weight is 1/nu, and this should not be huge compared to 1/alpha
        We (should) boundedly memoize this

    """
    #print h

    pct = float(sum(map(lambda s: ifelse(h(s) and not is_undef(h(s)), 1.0, 0.0), testing_set) )) / len(testing_set)
    # pul out the context sets and apply f
    #pct = float(sum(map(lambda s: ifelse(f(*s) is True, 1.0, 0.0), testing_set) )) / len(testing_set)
    # pul out the context sets and apply f
    #pct = float(sum(map(lambda s: ifelse(collapse_undef(f(*s)), 1.0, 0.0), testing_set) )) / len(testing_set)

    return 1.0 / (nu + pct)

def sample_context():
    set_size = randint(1,8)                             # the i'th data point
#    set_size =  weighted_sample( range(1,10+1),        # for the number-style probabilities
#                                 probs=[7187, 1484, 593, 334, 297, 165, 151, 86, 105, 112] )
    si = sample_sets_of_objects(set_size, all_objects)  # get the objects in the current set
    #print 'A: ', [o for o in si if o.shape == 'man']
    #print 'B: ', [o for o in si if o.job == 'pirate']
    #print 'S: ', si
    return H.MyContext(A=set([o for o in si if o.shape == 'man']),
                       B=set([o for o in si if o.job == 'pirate']),
                       S=set(si))

# quantifiers involving cardinality
all_objects = make_all_objects(shape=['man', 'woman', 'child'], job=['pirate', 'chef', 'fireman'])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~ Define a test set -- for doing Gricean things ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
TESTING_SET_SIZE = 1000

# create a small list of all plausible context sets.
# NOTE: Do no use this if utterances consist of all possible words (e.g. man/pirate are allowed to vary)
all_possible_context_sets = []
APD_N = 6
for adb in xrange(APD_N):
    for bda in xrange(APD_N-adb):
        for anb in xrange(APD_N-adb-bda):
            for s in xrange(APD_N-adb-bda-anb):
                adb_ = set([Obj(shape="man", job="chef") for i in xrange(adb)])
                bda_ = set([Obj(shape="woman", job="pirate") for i in xrange(bda)])
                anb_ = set([Obj(shape="man", job="pirate") for i in xrange(anb)])
                s_   = set([Obj(shape="woman", job="chef") for i in xrange(s)])

                all_possible_context_sets.append( [adb_.union(anb_), bda_.union(anb_), s_])
#print(all_possible_context_sets[-1])

TESTING_SET = [sample_context() for x in xrange(TESTING_SET_SIZE)]
print('Finished test set', len(TESTING_SET))
#TESTING_SET = [H.MyContext(A=x[0], B=x[1], S=x[2]) for x in all_possible_context_sets]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~ Define target ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# Write this out as a dictionary so that we can load it into a GriceanSimpleLexicon easier
target_functions = {
    #'the': lambda context: presup_(
    #    cardinality1_(context.A), nonempty_(intersection_(context.A, context.B))),
    #'a/some': lambda context: presup_(
    #    True, nonempty_(intersection_(context.A, context.B))),
    #'one': lambda context: presup_(
    #    nonempty_(context.A), cardinality1_(intersection_(context.A, context.B))),
    #'two': lambda context: presup_(
    #    nonempty_(context.A), cardinality2_(intersection_(context.A, context.B))),
    #'three': lambda context: presup_(
    #    nonempty_(context.A), cardinality3_(intersection_(context.A, context.B))),
    #'both': lambda context: presup_(
    #    cardinality2_(context.A), cardinality2_(intersection_(context.A, context.B))),
    #'either': lambda context: presup_(
    #    cardinality2_(context.A), cardinality1_(intersection_(context.A, context.B))),
    #'neither': lambda context: presup_(
    #    cardinality2_(context.A), empty_(intersection_(context.A, context.B))),
    'every': lambda context: presup_(
        nonempty_(context.A), subset_(context.A, context.B)),
    'most': lambda context: presup_(
        nonempty_(context.A), cardinalitygt_(intersection_(context.A, context.B),
                                             setdifference_(context.A, context.B))),
    #'none/no': lambda context: presup_(
    #    nonempty_(context.A), empty_(intersection_(context.A, context.B))),

    'gleeb': lambda context: presup_(
        nonempty_(context.A), not_(subset_(context.A, context.B))),
    'gleeb-prime': lambda context: presup_(
        nonempty_(context.B), not_(subset_(context.B, context.A))),

    'subset': lambda context: presup_(
        True, subset_(context.A, context.B)),
    'subset-prime': lambda context: presup_(
        True, subset_(context.B, context.A)),

    'differ': lambda context: presup_(
        True, cardinality1_(setdifference_(context.A, context.B))),
    'differ-prime': lambda context: presup_(
        True, cardinality1_(setdifference_(context.B, context.A))),

    'every-prime': lambda context: presup_(
        nonempty_(context.B), subset_(context.B, context.A)),
    'most-prime': lambda context: presup_(
        nonempty_(context.B), cardinalitygt_(intersection_(context.A, context.B),
                                             setdifference_(context.B, context.A))),

    #'1': lambda context: (presup_(False, False)),
    #'2': lambda context: (presup_(True, True)),
    #'3': lambda context: (presup_(True, nonempty_(context.A))),
    #'4': lambda context: (presup_(True, cardinality1_(context.A))),
    #'5': lambda context: (presup_(False, empty_(context.B))),
    #'6': lambda context: (presup_(True, subset_(context.B, context.A))),
    #'7': lambda context: (presup_(True, cardinalityeq_(context.A, context.B))),
    #'8': lambda context: (presup_(False, subset_(context.A, context.B))),
    #'9': lambda context: (presup_(cardinalityeq_(context.A, context.B), nonempty_(context.A))),
    #'10': lambda context: (presup_(cardinalitygt_(context.B, context.A), nonempty_(context.A))),

    #
    # 'few': lambda context: presup_(
    #     True, cardinalitygt_(3, intersection_(context.A, context.B))),
    # 'many': lambda context: presup_(
    #     True, cardinalitygt_(intersection_(context.A, context.B), 3)),
    # 'half': lambda context: presup_(
    #     nonempty_(context.A), cardinalityeq_(intersection_(context.A, context.B),
    #                                          setdifference_(context.A, context.B)))
}

target = H.GriceanQuantifierLexicon(make_my_hypothesis, my_weight_function)
for w, f in target_functions.items():
    target.set_word(w, LOTHypothesis(G.grammar, value='SET_IN_TARGET', f=f))


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~ Generate data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


def generate_data(data_size):
    all_words = target.all_words()
    data = []

    for i in break_ctrlc(xrange(data_size)):
        # a context is a set of men, pirates, and everything. functions are applied to this to get truth values
        context = sample_context()
        word = target.sample_utterance(all_words, context)
        data.append( UtteranceData(utterance=word, context=context, possible_utterances=all_words) )

    return data

