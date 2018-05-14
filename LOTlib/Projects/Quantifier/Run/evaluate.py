# -*- coding: utf-8 -*-

import pickle, re
import numpy as np
import pymp

from collections import defaultdict

from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.Miscellaneous import logsumexp
from LOTlib.Projects.Quantifier.Model import *
from LOTlib.TopN import TopN

SAMPLES = 10000
RUNS = 1
NUM_CPU = 20
CONSTRUCT_HSPACE = False

GRAMMAR_TYPE = 'cfg'
MAX_DATA_SIZE = 2050
SAMPLE_SIZE = 4000

def construct_hypothesis_space(data_size):
    all_hypotheses = TopN()
    print 'Data size: ', data_size
    for i in range(RUNS):
        print 'Run: ', i
        hypotheses = TopN(25)
        data = generate_data(data_size)
        learner = GriceanQuantifierLexicon(make_my_hypothesis, my_weight_function)
        for w in target.all_words():
            learner.set_word(w, make_my_hypothesis())
        j = 0
        for h in MHSampler(learner, data, SAMPLES, skip=0):
            hypotheses.add(h)
            j += 1
            if j > 0 and j % 1000 == 0:
                pickle.dump(hypotheses, open('data/hypset_'+GRAMMAR_TYPE+'_'+str(data_size)+'_'+str(j)+'.pickle', 'w'))
            #sstr = str(h)
            #sstr = re.sub("[_ ]", "", sstr)
            #sstr = re.sub("presup", u"\u03BB A B . presup", sstr)
            #print sstr
        all_hypotheses.update(hypotheses)
    return all_hypotheses

def get_hypotheses():
    all_hypotheses = TopN()
    for data_size in range(100, MAX_DATA_SIZE, 100):
        try:
            hypotheses = pickle.load(open('data/hypset_'+GRAMMAR_TYPE+'_'+str(data_size)+'_'+str(SAMPLE_SIZE)+'.pickle'))
        except:
            continue
        all_hypotheses.update(hypotheses)
    return all_hypotheses

def agree_pct(hypotheses):
    # get all the words
    words = hypotheses.best().all_words() # just get the words from the first hypothesis
    # now figure out how often each meaning is right for each word
    agree_pct = dict()  # how often does each part of meaning agree with each word?
    agree_pct_presup = dict()
    agree_pct_literal = dict()
    for h in hypotheses:
        for w in words:
            tresp = [ target.value[w](t) for t in TESTING_SET]
            hresp = [ h.value[w](t)      for t in TESTING_SET]

            key = w+":"+str(h)
            agree_pct[key]         = np.mean(collapse_undefs(tresp) == collapse_undefs(hresp))
            agree_pct_presup[key]  = np.mean(extract_presup(tresp)  == extract_presup(hresp))
            agree_pct_literal[key] = np.mean(extract_literal(tresp) == extract_literal(hresp))
    return agree_pct, agree_pct_presup, agree_pct_literal

def prob_correct(data_size, hypotheses, agree_pct, agree_pct_presup, agree_pct_literal):
    p_representation = defaultdict(int) # how often do you get the right representation
    p_response = defaultdict(int) # how often do you get the right response?
    p_representation_literal = defaultdict(int) # how often do you get the right representation
    p_response_literal = defaultdict(int)  # how often do you get the right response?
    p_representation_presup = defaultdict(int) # how often do you get the right representation
    p_response_presup = defaultdict(int) # how often do you get the right response?

    data = generate_data(data_size)
    # recompute posterior
    print 'Compute posterior for ', str(data_size)
    [x.compute_posterior(data) for x in hypotheses]
    # normalize the posterior in fs
    Z = logsumexp([x.posterior_score for x in hypotheses])

    # and output the top hypotheses
    #qq = TopN(N=25)
    #for h in hypotheses:
    #    qq.push(h, h.posterior_score) # get the tops
    #for i, h in enumerate(qq.get_all(sorted=True)):
    #    for w in h.all_words():
    #        fprintn(8, data_size, i, w, h.posterior_score, q(h.value[w]), f=OUT_PATH+"-hypotheses.txt")

    words = hypotheses.best().all_words()
    # and compute the probability of being correct
    for h in hypotheses:
        hstr = str(h)
        for w in words:
            p = np.exp(h.posterior_score - Z)
            key = w + ":" + hstr
            p_representation[w] += p * (agree_pct[key] == 1.)
            p_representation_presup[w]  += p * (agree_pct_presup[key] == 1.) # if we always agree with the target, then we count as the right rep.
            p_representation_literal[w] += p * (agree_pct_literal[key] == 1.)

            # and just how often does the hypothesis agree?
            p_response[w] += p * agree_pct[key]
            p_response_presup[w]  += p * agree_pct_presup[key]
            p_response_literal[w] += p * agree_pct_literal[key]

    filename = 'results/correctness_'+GRAMMAR_TYPE+'_'+str(SAMPLE_SIZE)+'.txt'
    f = open(filename, 'a')
    for w in words:
        col = [w, str(data_size), str(p_representation[w]),
               str(p_representation_presup[w]), str(p_representation_literal[w]),
               str(p_response[w]), str(p_response_presup[w]), str(p_response_literal[w])]
        f.write(','.join(col))


if __name__ == "__main__":
    if CONSTRUCT_HSPACE:
        print('===== Constructing hypothesis space =====')
        with pymp.Parallel(NUM_CPU) as p:
            for data_size in p.range(0, 2050, 100):
                if data_size == 0:
                    pass
                else:
                    hypotheses = construct_hypothesis_space(data_size)
                    pickle.dump(hypotheses, open('data/hypset_'+GRAMMAR_TYPE+'_'+str(data_size)+'.pickle', 'w'))

    # compute correctness
    print('===== Computing stats =====')
    hypotheses = get_hypotheses()
    agree_pct, agree_pct_presup, agree_pct_literal = agree_pct(hypotheses)
    with pymp.Parallel(NUM_CPU) as p:
        for data_size in p.range(100, 2050, 100):
            prob_correct(data_size, hypotheses, agree_pct, agree_pct_presup, agree_pct_literal)

