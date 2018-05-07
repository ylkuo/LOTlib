# -*- coding: utf-8 -*-
"""
Demo MCMC through lexica. Generally does not work well (too slow) so use the vectorized Gibbs version.

"""
import numpy as np
import re
from LOTlib.FunctionNode import *
from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.Projects.Quantifier.Model import *
from scipy.special import logsumexp

DEPTH_TO_ENUMERATE_PRIOR = 4
NUM_TOP_PRIORS = 1000

if __name__ == "__main__":
    ### sample the target data
    data = generate_data(2000)

    print('===== Distribution of utterances in data =====')
    show_baseline_distribution(TESTING_SET)
    print "\n"

    '''
    print('===== Compute likelihood of sampled data (log probability) =====')
    likelihoods = []
    for word, expr in target.value.items():
        print word
        new_data = filter(lambda ud: ud.utterance == word, data)
        target.compute_likelihood(new_data)
        likelihoods.append((word, target.likelihood))
    likelihoods = sorted(likelihoods, key=lambda tup: tup[1], reverse=True)
    for word, likelihood in likelihoods:
        print word, ', ', likelihood
    '''

    def check_expansion(node, term_type='none'):
        if not isFunctionNode(node):
            return True
        if node.term_type != term_type:
            return False
        args = node.args
        if args is None:
            return True
        elif len(args) == 1:
            return check_expansion(args[0])
        elif 'presup_' in str(node):
            return check_expansion(args[0]) and check_expansion(args[1])
        else:
            return check_expansion(args[0], 'left') and check_expansion(args[1], 'right')
        return True

    print('===== Enumerate grammar and prior (log probability) =====')
    hypotheses = []
    conserve_prob = []
    non_conserve_prob = []
    for t in grammar.enumerate(d=DEPTH_TO_ENUMERATE_PRIOR):
        if 'presup_(False' in str(t):
            continue
        if not check_expansion(t):
            continue
        conserve = is_conservative(t, TESTING_SET)
        prob = grammar.log_probability(t)
        hypotheses.append((t, prob, conserve))
        if conserve:
            conserve_prob.append(prob)
        else:
            non_conserve_prob.append(prob)
    hypotheses = sorted(hypotheses, key=lambda tup: tup[1], reverse=True)
    for t, prob, conserve in hypotheses[:NUM_TOP_PRIORS]:
        print(t, prob, conserve)
    print '\n'

    #print('===== Sum of log priors =====')
    #print('Conservative: ', np.exp(logsumexp(np.asarray(conserve_prob))))
    #print('Non-Conservative: ', np.exp(logsumexp(np.asarray(non_conserve_prob))))


    # intialize a learner lexicon, at random
    h0 = GriceanQuantifierLexicon(make_my_hypothesis, my_weight_function)
    for w in target.all_words():
        h0.set_word(w, make_my_hypothesis()) # We will defautly generate from null the grammar if no value is specified
    #print h0

    #for word, hypothesis in h0.value.items():
    #    print(word, is_conservative(hypothesis, TESTING_SET))

    #### Now we have built the data, so run MCMC
    for h in MHSampler(h0, data, 10, skip=0):
        sstr = str(h)
        sstr = re.sub("[_ ]", "", sstr)
        sstr = re.sub("presup", u"\u03BB A B . presup", sstr)
        print h.posterior_score, "\t", h.prior, "\t", h.likelihood, "\t", target.likelihood, "\n", sstr, "\n\n"

        #for t in data:
            #print h(t.utterance, t.context), t
