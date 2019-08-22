import numpy
from scipy import optimize
from copy import copy, deepcopy
import cpmatching._utils as utils

def solve_linear_program(c, A_ub, b_ub, A_eq, b_eq, bounds=(0, None)):
    """Solve the linear program
    min c^t x
    s. t. A_ub @ x <= b_ub
    A_eq @ x == b_ub
    bounds[i][0] <= x[i] <= bounds[i][1]

    If bounds is not a list, we assume that the bounds are the same for every element.

    This was originally written as (and currently still is) a wrapper around SciPy's optimize.linprog, which was chosen because it was the msot bare-bones commonly-available linear programming software and therefore would not tie us down to any particular features.

    Currently we use the revised simplex method of solving the linear programs.  The interior point method did not give good enough accuracy for our purposes.

    We use a function instead of simply calling the linprog function because that way it would be easier to change to a different linear program.

    :raises AlgorithmError: Raises an exception if the linear program solver can't solve the LP for some reason."""
    solution = optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="revised simplex")
    if solution.status == 0:
        return solution
    else:
        raise utils.AlgorithmError(solution.message)

def solve_primal(graph, F, round_to):
    """Solve P_F(graph, costs) via optimize.linprog.  Find the minimum cost and then find the lexicographically minimum solution with that cost."""
    equality_matrix = numpy.zeros((len(graph.vs), len(graph.es))) #The matrix for constraints of the form x(δ(v))=1 for v a vertex of the graph.
    for i in range(0, len(graph.vs)):
        for j in range(0, len(graph.es)):
            if i in graph.es[j].tuple:
                equality_matrix[i, j] = 1

    inequality_matrix = numpy.zeros((len(F),len(graph.es))) #The matrix for constraints of the form x(δ(S))≥1 for S in F.
    for i in range(0, len(F)):
        for j in range(0, len(graph.es)):
            if utils.edge_in_delta(graph.es[j].tuple, F[i]):
                inequality_matrix[i, j] = -1 #The linear program solver only allows less-than inequalities, so we multiply greater-than inequalities by -1.  This is also why, later, b_ub is made of -1s instead of 1s.

    equality_costs = [1] * len(graph.vs)
    inequality_costs = [-1] * len(F)

    solution = solve_linear_program(graph.es["weight"], inequality_matrix, inequality_costs, equality_matrix, equality_costs)
    min_cost = round(solution.fun, round_to) #The solver might give us something ever-so-slightly wrong due to floating point inaccuracies.  This wouldn't actually affect the rest of the code too much, but we round to make sure.

    equality_matrix = numpy.append(equality_matrix, numpy.array(graph.es["weight"]).reshape(1, -1), axis=0) #Add the constraint that graph.es["weight"] @ x == min_cost.
    equality_costs.append(min_cost)

    for edge_index in range(len(graph.es)):
        new_edge_costs = [0] * len(graph.es)
        new_edge_costs[edge_index] = 1 #Minimize x_i
        solution = solve_linear_program(new_edge_costs, inequality_matrix, inequality_costs, equality_matrix, equality_costs)
        equality_matrix = numpy.append(equality_matrix, numpy.array([1 if i == edge_index else 0 for i in range(len(graph.es))]).reshape(1, -1), axis=0) #Add the constraint that x[edge_index] == solution.x[edge_index].  (In other words, x[edge_index] is now fixed.)
        equality_costs.append(solution.x[edge_index])

    return [round(i, round_to) for i in solution.x]

def solve_duals(graph, F, x, Gamma, round_to):
    """Solve D*_F(graph, costs) repeatedly, using the "fake perturbations" method:

    1. Solve D*_F with constraints from Gamma.
    2. Remove slack constraints.
    3. Repeat."""
    duals = []
    removed_constraints = []
    size = len(graph.vs) + len(F) #The size of the solution to the dual problem given.  We'll actually be solving for a vector of length size * 2, because we need to solve for both r and Ψ, but we only want Ψ.
    (tight_sets, untight_sets) = utils.partition_tight_sets(graph, F, x, round_to) #Determine which sets in F are tight and which edges in the graph are in the support of x.
    (supp, not_supp) = utils.partition_support(graph, x)

    #The equality matrix doesn't change (we'd hope, at least, that all constraints in it are tight), so we calculate it outside of this loop.
    equality_matrix = numpy.zeros((len(supp) + len(untight_sets), size * 2)) #This matrix does double duty.  The first len(supp) rows represent the equality conditions in D*_F.  The final len(untightSets) rows force Ψ(S) to be equal to zero if S is not tight.
    for i, edge in enumerate(supp):
        for j in range(0, len(graph.vs)):
            if j in edge.tuple:
                equality_matrix[i, j] = 1
        for j, S in enumerate(F):
            if utils.edge_in_delta(edge.tuple, S):
                equality_matrix[i, j+len(graph.vs)] = 1
    for i, S in enumerate(untight_sets):
        equality_matrix[i + len(supp), untight_sets[i] + len(graph.vs)] = 1

    #Ditto the actual costs of the objective function.
    lp_costs = [0] * (size * 2) #Costs for both Ψ and r.  The former are 0, because Ψ does not appear in the objective function but exists anyway; the latter are as given in D*_F.
    for i in range(0, len(graph.vs)):
        lp_costs[size + i] = 1 #Note how we shift each index along by the size of Ψ, leaving the coefficients of Ψ as zero.
    for i, S in enumerate(F):
        if i in tight_sets:
             lp_costs[size + len(graph.vs) + i] = 1/len(S)

    #Ditto the inequality matrix.
    inequality_matrix = numpy.zeros((size * 2 + len(not_supp) + len(tight_sets), size * 2)) #The inequality matrix represents all three different inequality constraints given in the statement of D*_F.  We also put the non-zero constraints on Ψ here.
    for i in range(0, size): #Rearrange the double inequality to turn it into two single inequalities, both of which are functions of r and Ψ.
        #-r(S)-Psi(S)<=-Gamma(S)
        inequality_matrix[i, i] = -1
        inequality_matrix[i, i + size] = -1
        #-r(S)+Psi(S)<=Gamma(S)
        inequality_matrix[i + size, i] = 1
        inequality_matrix[i + size, i + size] = -1

    for i, edge in enumerate(not_supp): #Inequality constraints for edges not in supp(x).
        for j in range(0, len(graph.vs)):
            if j in edge.tuple:
                inequality_matrix[i + size * 2, j] = 1
        for j, S in enumerate(F):
            if utils.edge_in_delta(edge.tuple, S):
                inequality_matrix[i + size * 2, j+len(graph.vs)] = 1

    for i, v in enumerate(tight_sets):
        inequality_matrix[i + size*2 + len(not_supp), len(graph.vs) + v] = -1

    for index, coefficients in enumerate(Gamma):
        #Get constraint values.
        inequality_costs = [0] * (size * 2 + len(not_supp) + len(tight_sets) - len(removed_constraints))
        current_position = 0
        for i in utils.filtered_positions(range(0, size), removed_constraints):
            inequality_costs[current_position] = -1 * coefficients.get(utils.vertex_or_set(graph, F, i), 0)
            current_position += 1
        for i in utils.filtered_positions(range(size, size * 2), removed_constraints):
            inequality_costs[current_position] = coefficients.get(utils.vertex_or_set(graph, F, i - size), 0)
            current_position += 1
        for i in utils.filtered_positions(range(size * 2, size * 2 + len(not_supp)), removed_constraints):
            if index == 0:
                inequality_costs[current_position] = not_supp[i - size * 2]["weight"]
            elif list(graph.es).index(not_supp[i - size * 2]) == index - 1:
                inequality_costs[current_position] = 1
            current_position += 1
            

        equality_costs = [0] * (len(supp) + len(untight_sets))
        for i, uv in enumerate(supp):
            if index == 0:
                equality_costs[i] = uv["weight"]
            elif list(graph.es).index(uv) == index - 1:
                equality_costs[i] = 1

        #Solve the LP.
        new_dual = solve_linear_program(lp_costs, inequality_matrix, inequality_costs, equality_matrix, equality_costs, bounds=(None, None))
        duals.append({utils.vertex_or_set(graph, F, i):round(new_dual.x[i], round_to) for i in range(len(graph.vs)+len(F))})

        #Remove the slack constraints.
        slack_constraints = []
        for i in range(len(new_dual.slack)):
            if round(new_dual.slack[i], round_to) > 0:
                slack_constraints.append(i)
        inequality_matrix = numpy.delete(inequality_matrix, slack_constraints, axis=0)
        removed_constraints.extend(copy([utils.get_original_position(removed_constraints, x) for x in slack_constraints]))

    return duals
