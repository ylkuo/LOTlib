import matplotlib.pyplot as plt

SAMPLE_SIZE = 4000

cfg_correctness = {
    'every': [0],
    'every-prime': [0],
    'most': [0],
    'most-prime': [0],
    'subset': [0],
    'subset-prime': [0],
    'differ': [0],
    'differ-prime': [0],
    'gleeb': [0],
    'gleeb-prime': [0]
}
csg_correctness = {
    'every': [0],
    'every-prime': [0],
    'most': [0],
    'most-prime': [0],
    'subset': [0],
    'subset-prime': [0],
    'differ': [0],
    'differ-prime': [0],
    'gleeb': [0],
    'gleeb-prime': [0]
}

def read_correctness(grammar_type):
    f = open('results/correctness_' + grammar_type + '_' + str(SAMPLE_SIZE) + '.txt', "r")
    lines = f.readlines()
    for line in lines:
        cols = line.split(',')
        word = cols[0]
        correctness = float(cols[2])
        if grammar_type == 'cfg':
            cfg_correctness[word].append(correctness)
        elif grammar_type == 'csg':
            csg_correctness[word].append(correctness)
    f.close()

def plot(word):
    fig = plt.figure()
    ax = plt.axes(xlim=(0, 20.), ylim=(0, 1.1))
    plt.plot(cfg_correctness[word], 'r')
    plt.plot(csg_correctness[word], 'b')
    #plt.ylabel('some numbers')
    fig.savefig('figures/'+word+'.png')

read_correctness('cfg')
read_correctness('csg')
for word in cfg_correctness.keys():
    plot(word)
