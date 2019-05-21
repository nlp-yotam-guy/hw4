from PCFG import PCFG
import math

def load_sents_to_parse(filename):
    sents = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                sents.append(line)
    return sents

def get_binary_rules(pcfg):
    rules = dict()
    for rule in pcfg._rules:
        for rhs in pcfg._rules[rule]:
            if len(rhs[0]) == 2:
                try:
                    rules[rule].append(rhs)
                except:
                    rules[rule] = []
                    rules[rule].append(rhs)
    return rules

def cnf_cky(pcfg, sent):
    ### YOUR CODE HERE
    pi = dict()
    bp = dict()
    sent = sent.split(' ')
    n = len(sent)
    non_terminals = [nt for nt in pcfg._rules if not pcfg.is_terminal(nt)]
    binary_rules = get_binary_rules(pcfg)
    for i in range(n):
        for X in non_terminals:
            for rule in pcfg._rules[X]:
                pi[(i,i,X)] = rule[1]/pcfg._sums[X] if sent[i] in rule[0][0] else 0

    for l in range(n-1):
        for i in range(n-l):
            j = i+l
            for X in non_terminals:
                max_prob = float('-inf')
                if X not in binary_rules:
                    continue
                for binary_rule in binary_rules[X]:
                    for s in range(i,j):
                        q = binary_rule[1]/pcfg._sums[X]
                        if (i,s,binary_rule[0][0]) in pi and (s+1,j,binary_rule[0][1]) in pi:
                            prob = q * pi[(i,s,binary_rule[0][0])] * pi[(s+1,j,binary_rule[0][1])]
                        else:
                            prob = 0.0
                        if prob > max_prob:
                            max_prob = prob
                            pi[(i,j,X)] = max_prob
                            bp[(i,j,X)] = binary_rule

    ### END YOUR CODE
    return "FAILED TO PARSE!"

def non_cnf_cky(pcfg, sent):
    ### YOUR CODE HERE
    raise NotImplementedError
    ### END YOUR CODE
    return "FAILED TO PARSE!"

if __name__ == '__main__':
    import sys
    cnf_pcfg = PCFG.from_file_assert(sys.argv[1], assert_cnf=True)
    non_cnf_pcfg = PCFG.from_file_assert(sys.argv[2])
    sents_to_parse = load_sents_to_parse(sys.argv[3])
    for sent in sents_to_parse:
        print cnf_cky(cnf_pcfg, sent)
        print non_cnf_cky(non_cnf_pcfg, sent)
