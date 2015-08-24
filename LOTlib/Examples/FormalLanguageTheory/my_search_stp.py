import sys
import codecs
import itertools
from optparse import OptionParser
from pickle import dump
import time
import numpy as np
import LOTlib
from LOTlib.Miscellaneous import display_option_summary
from LOTlib.MPI.MPI_map import is_master_process, MPI_map
from LOTlib.Inference.Samplers.StandardSample import standard_sample
from LOTlib.Evaluation.Eval import register_primitive
from LOTlib.Miscellaneous import flatten2str, logsumexp, qq
from Model.Hypothesis import make_hypothesis
from Language.Index import instance
from mpi4py import MPI
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
fff = sys.stdout.flush

register_primitive(flatten2str)


def run(mk_hypothesis, lang, size):
    """
    This out on the DATA_RANGE amounts of data and returns all hypotheses in top count
    """
    if LOTlib.SIG_INTERRUPTED:
        return set()

    return standard_sample(lambda: mk_hypothesis(options.LANG, N=options.N),
                           lambda: lang.sample_data_as_FuncData(size),
                           N=options.TOP_COUNT,
                           steps=options.STEPS,
                           show=False, save_top=None)


def simple_mpi_map(run, args):
    hypo_set = run(*(args[rank]))

    if rank == 0:
        _set = set()
        _set.update(hypo_set)
        for i in xrange(size - 1):
            _set.update(comm.recv(source=i+1))
        return _set
    else:
        comm.send(hypo_set, dest=0)
        sys.exit(0)

if __name__ == "__main__":
    # ========================================================================================================
    # Process command line arguments /
    # ========================================================================================================
    fff = sys.stdout.flush
    parser = OptionParser()
    parser.add_option("--language", dest="LANG", type="string", default='An', help="name of a language")
    parser.add_option("--steps", dest="STEPS", type="int", default=10000, help="Number of samples to run")
    parser.add_option("--top", dest="TOP_COUNT", type="int", default=20, help="Top number of hypotheses to store")
    parser.add_option("--finite", dest="FINITE", type="int", default=10, help="specify the max_length to make language finite")
    parser.add_option("--name", dest="NAME", type="string", default='', help="name of file")
    parser.add_option("--N", dest="N", type="int", default=3, help="number of inner hypotheses")
    (options, args) = parser.parse_args()

    prefix = 'out/SimpleEnglish/'
    # prefix = '/home/lijm/WORK/yuan/lot/'
    suffix = time.strftime('_' + options.NAME + '_%m%d_%H%M%S', time.localtime())

    # set the output codec -- needed to display lambda to stdout
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    if is_master_process():
        display_option_summary(options); fff()

    # you need to run 5 machine on that
    DATA_RANGE = np.arange(20, 300, 24)

    language = instance(options.LANG, options.FINITE)
    args = list(itertools.product([make_hypothesis], [language], DATA_RANGE))
    # run on MPI
    # results = MPI_map(run, args)
    hypotheses = simple_mpi_map(run, args)

    # ========================================================================================================
    # Get stats
    # ========================================================================================================

    dump(hypotheses, open(prefix+'hypotheses'+suffix, 'w'))

    # get precision and recall for h
    pr_data = language.sample_data_as_FuncData(1024)
    p = []
    r = []
    print 'compute precision and recall..'
    for h in hypotheses:
        precision, recall = language.estimate_precision_and_recall(h, pr_data)
        p.append(precision)
        r.append(recall)

    # Now go through each hypothesis and print out some summary stats
    for data_size in DATA_RANGE:
        print 'get stats from size : ', data_size

        evaluation_data = language.sample_data_as_FuncData(data_size)

        # Now update everyone's posterior
        for h in hypotheses:
            h.compute_posterior(evaluation_data)

        # compute the normalizing constant. This is the log of the sum of the probabilities
        Z = logsumexp([h.posterior_score for h in hypotheses])

        f = open(prefix + 'out' + suffix, 'a')
        cnt = 0
        for h in hypotheses:
            #compute the number of different strings we generate
            generated_strings = set([h() for _ in xrange(1000)])
            print >> f, data_size, np.exp(h.posterior_score-Z), h.posterior_score, h.prior, \
                h.likelihood, len(generated_strings), qq(h), p[cnt], r[cnt]
            cnt += 1
        f.close()