import matplotlib.pyplot as plt

SAMPLE_SIZE = {
    'cfg': 10000,
    'csg': 10000,
    'csg_more': 8000
}
FOLDER = '' #'/run_0'
GRAMMARS = ['cfg', 'csg']

cfg_correctness = {
    'every': [0 for _ in range(21)],
    'every-prime': [0 for _ in range(21)],
    'most': [0 for _ in range(21)],
    'most-prime': [0 for _ in range(21)],
    'subset': [0 for _ in range(21)],
    'subset-prime': [0 for _ in range(21)],
    'differ': [0 for _ in range(21)],
    'differ-prime': [0 for _ in range(21)],
    'gleeb': [0 for _ in range(21)],
    'gleeb-prime': [0 for _ in range(21)]
}
csg_correctness = {
    'every': [0 for _ in range(21)],
    'every-prime': [0 for _ in range(21)],
    'most': [0 for _ in range(21)],
    'most-prime': [0 for _ in range(21)],
    'subset': [0 for _ in range(21)],
    'subset-prime': [0 for _ in range(21)],
    'differ': [0 for _ in range(21)],
    'differ-prime': [0 for _ in range(21)],
    'gleeb': [0 for _ in range(21)],
    'gleeb-prime': [0 for _ in range(21)]
}

def read_correctness(grammar_type):
    f = open('results'+FOLDER+'/correctness_' + grammar_type + '_' + str(SAMPLE_SIZE[grammar_type]) + '.txt', "r")
    lines = f.readlines()
    for line in lines:
        cols = line.split(',')
        word = cols[0]
        correctness = float(cols[-6])
        i = int(cols[1]) / 100
        if grammar_type == 'cfg':
            cfg_correctness[word][i] = correctness
        elif grammar_type == 'csg':
            csg_correctness[word][i] = correctness
        elif grammar_type == 'csg_more':
            csg_correctness[word][i] = correctness
    f.close()

def plot(word):
    fig = plt.figure()
    ax = plt.axes(xlim=(0, 20.), ylim=(0, 1.1))
    plt.plot(cfg_correctness[word], 'r')
    plt.plot(csg_correctness[word], 'b')
    #plt.ylabel('some numbers')
    vals = ax.get_xticks()
    ax.set_xticklabels(['{:4.0f}'.format(x*100) for x in vals])
    fig.savefig('figures/'+word+'.png')

for grammar_type in GRAMMARS:
    read_correctness(grammar_type)
for word in cfg_correctness.keys():
    plot(word)
