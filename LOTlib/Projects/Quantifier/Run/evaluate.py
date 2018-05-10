# -*- coding: utf-8 -*-

import pickle, re
import pymp

from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.Projects.Quantifier.Model import *
from LOTlib.TopN import TopN

SAMPLES = 10000
RUNS = 1000

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
        for h in MHSampler(learner, data, SAMPLES, skip=0):
            hypotheses.add(h)
            #sstr = str(h)
            #sstr = re.sub("[_ ]", "", sstr)
            #sstr = re.sub("presup", u"\u03BB A B . presup", sstr)
            #print sstr
        all_hypotheses.update(hypotheses)
    return all_hypotheses

def agree_pct():
    pass

def prob_correct():
    pass

if __name__ == "__main__":
    print('===== Constructing hypothesis space =====')
    with pymp.Parallel(20) as p:
        for data_size in p.range(0, 2050, 100):
            if data_size == 0:
                pass
            else:
                hypotheses = construct_hypothesis_space(data_size)
                pickle.dump(hypotheses, open('data/hypset_cfg_'+str(data_size)+'.pickle', 'w'))
