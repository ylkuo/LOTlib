# -*- coding: utf-8 -*-
"""
Print the word probability of production according to the model

"""
from LOTlib.Projects.Quantifier.Model import *

if __name__ == "__main__":

    print "# word production frequencies from our generative model"
    print "word model.frequency"
    show_baseline_distribution(TESTING_SET)
    print "\n\n"
