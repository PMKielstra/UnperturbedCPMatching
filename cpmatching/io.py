from igraph import *

def pretty_input_graph():
    """A user-friendly way to type in a graph with the fewest keystrokes."""
    vertNumber = int(input("How many vertices?  "))
    G = Graph()
    G.add_vertices(vertNumber)
    print("Successfully added {} vertices, numbered 0 through {}.".format(vertNumber, vertNumber - 1))
    counter = 0
    while True:
        source = input("Enter the source for edge {}, or press return to stop adding edges.  ".format(counter))
        if not source.isdigit():
            break
        target = input("Enter the target for edge {}.  ".format(counter))
        weight = input("Enter the weight of edge {}.  ".format(counter))
        try:
            G.add_edge(int(source), int(target), weight=int(weight))
        except InternalError as ie:
            print(ie.message)
            continue
        except ValueError:
            print("You entered a non-integer value, so we can't add this edge.")
            continue
    return G

def graph_from_network_x(graph):
    """Converts a NetworkX graph to an igraph graph."""
    verts = list(graph.nodes)
    G = Graph()
    G.add_vertices(len(verts))
    edges = list(graph.edges.data("weight", default=1))
    G.add_edges([(verts.index(edge[0]), verts.index(edge[1])) for edge in edges])
    G.es["weight"]=[e[2] for e in edges]
    return G

def pretty_print_solution(graph, x):
    """Print a list of the edges in the given graph for which x=1, preceded by a header."""
    print("Edges in solution:")
    for i, val in enumerate(x):
        if val > 0:
            print("{}: {} (cost {})".format(graph.es[i].tuple, val, graph.es[i]["weight"]))
    print("Total cost: {}".format(sum([x[i] * graph.es[i]["weight"] for i in range(len(x))])))

def perturb(graph):
    """Perturb the cost function of a graph according to Chandrasekaran's paper."""
    m = len(graph.es)
    for i in range(1, m+1):
        graph.es[i-1]["weight"] += 0.5**i
