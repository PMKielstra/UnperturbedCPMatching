from copy import copy
from .partitioning import end_in_delta

def sanity_check(graph):
    """Quick checks for graphs that have no perfect matchings or could otherwise cause the algorithm to fail:
    -Graphs without any vertices.
    -Graphs without any edges.
    -Graphs without edge weights.
    -Graphs with disconnected odd components."""
    if len(graph.vs) == 0:
        raise AlgorithmError("The graph has no vertices.")
    if len(graph.es) == 0:
        raise AlgorithmError("The graph has no edges.")
    if not graph.is_weighted():
        raise AlgorithmError("The graph has no edge weights.  If you want to run the algorithm on an unweighted graph, please set all edge weights to 1.")
    for c in graph.clusters():
        if len(c) % 2 == 1:
            raise AlgorithmError("The graph has an odd cluster or single uncovered vertex and so does not have a perfect matching.")

def is_integral(x):
    """Is every value in a list an integer?"""
    for i in x:
        if i % 1 != 0:
            return False
    return True

def get_cycles(graph, x):
    """Find all cycles in the support of x, where x is a vector from graph.es to [0, 1]."""
    cycles = []
    halfedges = [] #Not halves of edges, but 1/2-edges.
    for i, val in enumerate(x): #First, get a list of all edges that must be part of a cycle.
        if 0 < val < 1: #Edges are part of a cycle if and only if they have non-integral weight in x.
            halfedges.append(copy(graph.es[i].tuple)) #Copy instead of just append because otherwise we'd be passing by reference and so we'd end up mutating the graph later.
    while len(halfedges) > 0: #The algorithm works as follows.  We first take one edge from halfedges and add it to cycles.  Then we look through all the other 1/2-edges and try to use them to extend the cycle.  Once we get stuck, we create a new cycle from one of the halfedges we haven't used yet.
        cycles.append(list(halfedges.pop()))
        making_progress = True
        while making_progress: #We might have to loop through halfedges multiple times before exhausting all possibilities to extend known cycles, just due to the ordering of halfedges.  For example, if cycles=[[1,2]] and halfedges=[[3,4],[2,3],[1,4]], then [3,4] wouldn't be used to extend the cycle until the second loop.
            making_progress = False
            for edge in halfedges:
                for cycle in cycles:
                    if end_in_delta(edge, cycle, 1): #These two if blocks do basically the same thing.  Cycles are made of vertices, not edges, so if we find an edge with only one end in the cycle we just add the other end.
                        cycle.append(edge[0])
                        halfedges.remove(edge)
                        making_progress = True
                    elif end_in_delta(edge, cycle, 0):
                        cycle.append(edge[1])
                        halfedges.remove(edge)
                        making_progress = True
                    elif edge[0] in cycle and edge[1] in cycle: #If we find an edge with both ends in a cycle, then we've completed the cycle.  For example, if we already have 1-2-3 and then we get 3-1, that's a valid edge, but it doesn't add any more vertices.  In this case, we just say we've processed the edge.
                        halfedges.remove(edge)
                        making_progress = True
    return cycles #When there are no more halfedges left to make cycles out of, return our list.

class AlgorithmError(Exception):
    """For when the linear programming solver is performing as expected but the algorithm is feeding it garbage."""
    pass
