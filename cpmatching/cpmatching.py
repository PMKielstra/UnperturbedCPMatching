import cpmatching._utils as utils
import cpmatching._linprogs as linprogs
from copy import deepcopy

def find_matching(graph, round_to=3):
    """Implements the Unperturbed C-P-Matching Algorithm, which emulates perturbed C-P-Matching by using multiple different linear programs.

    :param graph: An igraph graph with costs stored as "weight" on each edge.
    :param round_to: The number of decimal places to which to round intermediate solutions.
    :returns: A one-dimensional vector, with every element 0 or 1, indicating whether or not that edge is in the matching.
    """
    
    utils.sanity_check(graph)

    if round_to < 1:
        raise utils.AlgorithmError("The algorithm requires half-integral intermediate solutions, so rounding to <1 d.p. would break it.")

    F = []
    Gamma = [{i:0 for i in range(len(graph.vs))}] * (len(graph.es) + 1) #Gamma is implemented as a list of dicts.

    while True:
        x = linprogs.solve_primal(graph, F, round_to)
        if utils.is_integral(x):
            return [int(i) for i in x] #Because it might not be integral, x is a float.  Now we know it is, we'll convert it to an int.
        duals = linprogs.solve_duals(graph, F, x, Gamma, round_to)

        H1 = set()
        for S in F:
            if max([Pi.get(S, 0) for Pi in duals]) > 0: #Technically we only need know if there exists a Pi such that Pi(S)>0.  However, using max does the same thing and is easier to implement and read.
                H1.add(S)

        H2 = set()
        cycles = utils.get_cycles(graph, x)
        for cycle in cycles:
            C = set(cycle)
            for element in cycle:
                for cut in H1:
                    if element in cut:
                        C = set.union(C, set(cut))
            H2.add(tuple(C))

        F = list(set.union(H1, H2))
        Gamma = deepcopy(duals)
