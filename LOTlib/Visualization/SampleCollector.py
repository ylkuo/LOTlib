"""

We should be able to do:

hypotheses = set()
sc = SampleCollector(rate=100)

for h in lot_iter(mh_sampler):
    hypotheses.add(h)
    # add to SampleCollector
    sc.add_sample(h)

sc.graph('HPD')   # something like this
mean = sc.mean()
"""
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

class SampleCollector:

    def __init__(self, rate):
        self.rate = rate
        self.samples = []
        self.sample_count = 0
        self.count = 0

    def add_sample(self, sample):
        if self.count % self.rate == 0:
            self.samples.append(sample)
            self.sample_count += 1
        self.count += 1


class VectorSampleCollector(SampleCollector):
    def __init__(self, rate):
        SampleCollector.__init__(self, rate)

    def graph_samples(self):
        # this converts [[s1v1 s1v2 s1v3] [s2v1 s2v2 ..] ..] ==> [[s1v1 s2v1 s3v1 ..] [s2v1 s2v2 s2v3 ..] ..]
        vector_data = zip(*[s.value for s in self.samples])
        c = float(self.sample_count)

        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 4., 4.])
        ax.set_title('Distribution of values over GrammarRules generated by MH', fontsize=10)
        ax.set_yticklabels([])

        def update_violinplot(value):
            # TODO: make sure this will update violinplot each time
            ax.violinplot(vector_data, points=100, vert=False, widths=0.7,
                          showmeans=True, showextrema=True, showmedians=True)
            fig.canvas.draw()

        slider = Slider(ax, "after N samples", valmin=1., valmax=c, valinit=c)
        slider.on_changed(update_violinplot)

        plt.show()