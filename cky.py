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


def cnf_cky(pcfg, sent):
    ### YOUR CODE HERE
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

    def create_tree(bp, pi, n, sent):
        return create_tree_rec(1, n, 'ROOT', bp, pi, sent)

    def create_tree_rec(i, j, symbol, bp, pi, sent):
        if pi[(i, j, symbol)] == 0.0:
            raise KeyError
        if i == j:
            leaf = '(' + symbol + ' ' + sent[i - 1] + ')'
            return leaf
        s = bp[(i, j, symbol)][1]
        expansion = bp[(i, j, symbol)][0][0]
        if i == s:
            left = symbol + ' ' + '(' + expansion[0] + ' ' + sent[i - 1] + ')'
            right = create_tree_rec(s + 1, j, expansion[1], bp, pi, sent)
            return '(' + left + ' ' + right + ')'
        left = create_tree_rec(i, s, expansion[0], bp, pi, sent)
        right = create_tree_rec(s + 1, j, expansion[1], bp, pi, sent)
        return '(' + symbol + ' ' + left + ' ' + right + ')'

    pi = dict()
    bp = dict()
    sent = sent.split(' ')
    n = len(sent)
    non_terminals = [nt for nt in pcfg._rules if not pcfg.is_terminal(nt)]
    binary_rules = get_binary_rules(pcfg)
    for i in range(1,n+1):
        for X in non_terminals:
            for rule in pcfg._rules[X]:
                pi[(i,i,X)] = rule[1]/pcfg._sums[X] if sent[i-1] == rule[0][0] else 0.0
                if pi[(i, i, X)] > 0.0:
                    break

    for l in range(1,n):
        for i in range(1,n-l+1):
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
                            bp[(i,j,X)] = (binary_rule,s)

    try:
        tree = create_tree(bp,pi,n,sent)
        return tree
    except:
        pass
    ### END YOUR CODE
    return "FAILED TO PARSE!"


def non_cnf_cky(pcfg, sent):
    ### YOUR CODE HERE

    def is_long_terminal(sent, i, rule):
        r = len(rule[0])
        if r == 1:
            return False
        return sent[i:i + r] == rule[0]

    def update_grammar(token, count, pcfg, long_terminal):
        for symbol in pcfg._rules:
            for rule in pcfg._rules[symbol]:
                if rule[0] == long_terminal:
                    pcfg._rules[symbol].remove(rule)
                    pcfg._rules[symbol].append(([token], count))


    # TODO: problem with reduce_to_cnf
    def reduce_to_cnf(pcfg, sent):
        import copy
        pcfg_cnf = copy.deepcopy(pcfg)
        cnf_sent = []
        n = len(sent)
        i = 0
        while i < n:
            next_i = False
            for symbol in pcfg._rules:
                for rule in pcfg._rules[symbol]:
                    if is_long_terminal(sent, i, rule):
                        token = '_'.join(rule[0])
                        if cnf_sent[len(cnf_sent)-1] != token:
                            cnf_sent.append(token)
                        count = rule[1]
                        update_grammar(token, count, pcfg_cnf,rule[0])
                        i += len(rule[0]) - 1
                        next_i = True
                        break
                    elif sent[i] in rule[0]:
                        cnf_sent.append(sent[i])
                        next_i = True
                    if next_i:
                        break
                if next_i:
                    break
            i += 1
        return pcfg_cnf, cnf_sent

    split_sent = sent.split(' ')
    pcfg_cnf, split_sent = reduce_to_cnf(pcfg, split_sent)
    tree = cnf_cky(pcfg_cnf, ' '.join(split_sent))
    ### END YOUR CODE
    return tree.replace('_', ' ')


if __name__ == '__main__':
    import sys
    cnf_pcfg = PCFG.from_file_assert(sys.argv[1], assert_cnf=True)
    non_cnf_pcfg = PCFG.from_file_assert(sys.argv[2])
    sents_to_parse = load_sents_to_parse(sys.argv[3])
    for sent in sents_to_parse:
        print cnf_cky(cnf_pcfg, sent)
        print non_cnf_cky(non_cnf_pcfg, sent)
