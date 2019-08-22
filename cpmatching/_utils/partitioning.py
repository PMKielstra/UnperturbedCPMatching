def edge_in_delta(edge, S):
    """Is edge in δ(s)?"""
    return end_in_delta(edge, S, 0) or end_in_delta(edge, S, 1)

def end_in_delta(edge, S, end):
    """Is edge in δ(s), and is the specified end of edge in s?"""
    return edge[end] in S and not edge[1-end] in S

def partition_tight_sets(graph, F, x, round_to):
    """Partition sets in F into those which are tight and not tight with respect to x."""
    tight = []
    untight = []
    for i in range(0, len(F)):
        delta = 0
        for j in range(0, len(graph.es)):
            if edge_in_delta(graph.es[j].tuple, F[i]): #For each set F[i] in F, calculate x(δ(F[i])) by summing the x-values for those edges in δ(F[i])
                delta += x[j]
        if round(delta, round_to) == 1: #Round just in case of issues with floating-point adding.
            tight.append(i)
        else:
            untight.append(i)
    return (tight, untight)

def partition_support(graph, x):
    """Partition edges in the graph into those which are and aren't in the support of x.

    :returns: A tuple containing two lists.  The first is those edges in supp(x), the second is all the rest."""
    supp = []
    not_supp = []
    for i in range(0, len(graph.es)):
        if x[i] != 0:
            supp.append(graph.es[i])
        else:
            not_supp.append(graph.es[i])
    return (supp, not_supp)
