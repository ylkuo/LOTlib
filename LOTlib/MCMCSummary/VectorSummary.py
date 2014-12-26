import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from MCMCSummary import MCMCSummary


class VectorSummary(MCMCSummary):
    """
    Summarize & plot data for MCMC with a VectorHypothesis (e.g. GrammarHypothesis).

    """
    def __init__(self, skip=100, cap=100):
        MCMCSummary.__init__(self, skip=skip, cap=cap)

    def zip_vector(self, idxs):
        """Return a n-long list - each member is a time series of samples for a single vector item.

        In `self.samples`, we have a list of samples; basically instead of this:
            [sample1, sample2, sample3, ...]

        We want to return this:
            [[s1[0], s2[0], s3[0], ...], [s1[1], s2[1], s3[1], ...], ...]

        """
        zipped_vector = zip(*[[s.value[i] for i in idxs] for s in self.samples])
        zipped_vector = [np.array(l) for l in zipped_vector]
        return zipped_vector

    def median_value(self, idxs=None):
        """Return a vector for the median of each value item accross `self.samples`, items in `idxs`."""
        if idxs is None:
            idxs = range(1, self.samples[0].n)
        vector_data = self.zip_vector(range(1, idxs))
        return [np.mean(v) for v in vector_data]

    def mean_value(self, idxs=None):
        """Return a vector for the mean of each value item accross `self.samples`, items in `idxs`."""
        if idxs is None:
            idxs = range(1, self.samples[0].n)
        vector_data = self.zip_vector(idxs)
        return [np.mean(v) for v in vector_data]

    # --------------------------------------------------------------------------------------------------------
    # Plotting methods

    def plot(self, plot_type):
        assert plot_type in ('violin', 'values', 'post', 'MLE', 'MAP'), "invalid plot type!"
        if plot_type == 'violin':
            return self.violinplot_value()
        if plot_type == 'values':
            self.lineplot_value()
        if plot_type in ('post', 'MLE', 'MAP'):
            self.lineplot_gh_metric(metric=plot_type)

    def violinplot_value(self):
        """
        TODO: doc?

        """
        # Numpy array of sampled values for each vector element altered in proposals
        s0 = self.samples[0]
        propose_idxs = s0.propose_idxs
        y_labels = [s0.rules[i].short_str() for i in propose_idxs]
        vector_data = self.zip_vector(propose_idxs)

        def draw_violinplot(value):
            """Clear axis & draw a labelled violin plot of the specified data.

            Note:
              * If we haven't accepted any proposals yet, all our data is the same and this causes a
                singular matrix 'LinAlgError'
            """
            data = [vector[0:value] for vector in vector_data]

            ax.clear()
            ax.set_title('Distribution of values over GrammarRules generated by MH')
            try:
                vplot = ax.violinplot(data, points=100, vert=False, widths=0.7,
                                      showmeans=True, showextrema=True, showmedians=True)
            except Exception:     # seems to catch LinAlgError, ValueError
                vplot = None
            ax.set_yticks(range(1, len(propose_idxs)+1))
            ax.set_yticklabels(y_labels)

            fig.canvas.draw_idle()
            return vplot

        # Set up initial violinplot
        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2, left=0.1)
        violin_stats = draw_violinplot(self.sample_count)

        # Slider updates violinplot as a function of how many samples have been generated
        slider_ax = plt.axes([0.1, 0.1, 0.8, 0.02])
        slider = Slider(slider_ax, "after N samples", valmin=1., valmax=self.sample_count, valinit=1.)
        slider.on_changed(draw_violinplot)

        plt.show()
        return violin_stats

    def lineplot_value(self):
        """
        http://matplotlib.org/examples/pylab_examples/subplots_demo.html

        """
        # Numpy array of sampled values for each vector element altered in proposals
        s0 = self.samples[0]
        propose_idxs = s0.propose_idxs
        n = len(propose_idxs)
        y_labels = [s0.rules[i].short_str() for i in propose_idxs]
        vector_data = self.zip_vector(propose_idxs)

        # N subplots sharing both x/y axes
        f, axs = plt.subplots(n, sharex=True, sharey=True)
        axs[0].set_title('\tGrammar Priors as a Function of MCMC Samples')
        y_min = math.ceil(min([v for vector in vector_data for v in vector]))
        y_max = math.ceil(max([v for vector in vector_data for v in vector]))
        for i in range(n):
            axs[i].plot(vector_data[i])
            axs[i].set_yticks(np.linspace(y_min, y_max, 5))
            # axs[i].scatter(vector_data[i])
            rule_label = axs[i].twinx()
            rule_label.set_yticks([0.5])
            rule_label.set_yticklabels([y_labels[i]])

        # Fine-tune figure; make subplots close to each other and hide x ticks for all but bottom plot.
        f.subplots_adjust(hspace=0)
        plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
        plt.show()

    def lineplot_gh_metric(self, metric='post'):
        """
        Draw a line plot for the GrammarHypothesis, evaluated by GH.posterior_score, MAP, or MLE.

        """
        assert metric in ('post', 'MLE', 'MAP'), "invalid plot metric!"
        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2, left=0.1)
        ax.set_title('Evaluation for GrammarHypotheses Sampled by MCMC')

        if metric == 'post':
            mcmc_values = [gh.posterior_score for gh in self.samples]
        elif metric == 'MAP':
            mcmc_values = [gh.max_a_posteriori() for gh in self.samples]
        elif metric == 'MLE':
            mcmc_values = [gh.max_like_estimate() for gh in self.samples]
        else:
            mcmc_values = []
        ax.plot(mcmc_values)
        plt.show()

    def plot_y_in_concept(self, n=10):
        """
        TODO

        This should be a method to visualize p(y \in C) over each y in the domain.

        For reference, see the bar graphs in Josh Tenenbaum / Kevin Murphy's 'Bayesian Concept Learning'.

        Notes:
            * for now, this is only built for NumberGameHypothesis.
            * this should be 3 barplots: bayesian model averaging (weighted likelihood), MLE, & MAP
            * there should be a slider so we can see how each of these changes over samples (like violinplot)

        """
        pass
        '''
        # Update the bar plots when you move the slider
        def draw_barplots(idx):
            gh = self.samples[idx]
            y_likelihoods = [0]*gh.domain

            for i in range(1, gh.domain):                                # TODO: gh won't have `domain`
                y_likelihoods[i] = math.exp(gh.compute_likelihood([i]))  # TODO compute_likelihood won't work.

            axs[0].clear()
            axs[0].set_title('Distribution of values over GrammarRules generated by MH')
            axs[0] = plt.hist(h_in_domain, bins=domain, range=(1, domain))
            axs[0].set_yticks(range(0., 1., .2))


            axs.plotstuff()

            fig.canvas.draw_idle()

        fig, axs = plt.subplots(n, sharex=True, sharey=True)
        axs[0].set_title('Grammar Priors as a Function of MCMC Samples')
        draw_barplots(0)

        # Slider updates violinplot as a function of how many samples have been generated
        slider_ax = plt.axes([0.1, 0.1, 0.8, 0.02])
        slider = Slider(slider_ax, "after N samples", valmin=1., valmax=self.sample_count, valinit=1.)
        slider.on_changed(draw_barplots)
        plt.show()
        '''



