def vertex_or_set(graph, F, i):
    """The dual solutions we find will have values on both vertices (which don't change their order, get created, or disappear between iterations) and sets in F (which might do any of those things).  We therefore use integers to index vertices and tuples to index the sets.

    This function, for use when iterating over costs, will return either an integer or a set tuple, allowing us to use one `for i in range` statement to iterate seamlessly over first vertices and then sets."""
    if i < len(graph.vs):
        return i
    else:
        return F[i-len(graph.vs)]

def filtered_positions(positions, removed_constraints):
    """Given a list of positions, and a list of positions that are to be removed from the first one, return the list of positions that have not been removed."""
    return [i for i in positions if i not in removed_constraints]

def get_original_position(removed_constraints, new_constraint):
    """Given a list of indices that have already been removed from a list, and the index of an element in the pruned list, find the index of the element in the original list."""
    working = 0
    pointer = 0
    while working <= new_constraint:
        if pointer not in removed_constraints:
            working += 1
        pointer += 1
    return pointer - 1
