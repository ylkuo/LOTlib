
from math import log
from LOTlib.Eval import RecursionDepthException
from LOTlib.Miscellaneous import Infinity

class MultinomialLikelihood(object):
    """
    Compute multinomial likelihood for data where the data is a dictionary and the function
    output is also a dictionary of counts. The self dictionary gets normalized to be a probability
    distribution. Smoothing term called "outlier" is the (unnormalized) probability assigned to
    out of sample items
    """

    def compute_single_likelihood(self, datum, outlier=-100):
        assert isinstance(datum.output, dict)

        try:

            hc = self(*datum.intput) # output dictionary, output->counts
            assert isinstance(hc, dict)

            hz = log(sum(ho.values())) # normalizing factor

            return sum( dc * ( log(hc.get(k,outlier)) - hz ) for k, dc in datum.output.items() )

            return ll
        except RecursionDepthException as e:
            return -Infinity