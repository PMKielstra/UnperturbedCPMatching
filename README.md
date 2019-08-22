# Unperturbed C-P-Matching Sample Code
[![DOI](https://zenodo.org/badge/202629044.svg)](https://zenodo.org/badge/latestdoi/202629044)

This is an example implementation, in Python 3, of the minimum-cost perfect matching algorithm described in Chen, Cheung, Kielstra, and Winn's paper _Revisiting a Cutting Plane Method for Perfect Matchings_.  It currently uses SciPy to solve linear programs, but will work with any black-box LP solver with only minor alterations.

This is academic example code, not suitable for use in a production environment.

## Requirements
* [SciPy](https://www.scipy.org/) and [NumPy](https://www.numpy.org/)
* [igraph](https://igraph.org/python/)

```
pip3 install numpy scipy python-igraph
```

## Usage
```python
import cpmatching
import cpmatching.io as io
from igraph import Graph

G = Graph()
G.add_vertices(16)
G.add_edges([[13, 15], [11, 14], [10, 11], [10, 14], [9, 11], [8, 11], \
[7, 12], [5, 15], [5, 13], [4, 11], [4, 13], [3, 7], [2, 6], [2, 13], \
[1, 5], [0, 1], [0, 3], [0, 12], [8, 9], [4, 12]])
G.es["weight"] = 1

x = cpmatching.find_matching(G)

io.pretty_print_solution(G, x)
```

The algorithm functions by solving a sequence of linear programs.  Internally, solutions to these are rounded to avoid errors caused by floating-point inaccuracy.  In some cases, such as if you want to use fractional edge costs, this might cause problems.  The `find_matching()` routine has an optional parameter, `round_to`, which sets the number of decimal places to which to round.  By default it is equal to `3`.  If you use fractional costs which must be specified to `x` d.p., it is prudent to set `round_to` equal to at least `x+1`.

The `io` sub-package has a number of functions for inputting and outputting graphs in the nicest possible ways.

## Different LP Solvers

The algorithm is not tied to any specific linear program solver.  To use a different one, simply modify the `solve_linear_program` function in `_linprogs.py`.  This takes a linear program of the form

```
min c^t x
s.t. A_ub x <= b_ub
A_eq x == b_eq
bounds[i][0] <= x[i] <= bounds[i][1]
```

If `bounds` is a single tuple, then we take `bounds[0] <= x[i] <= bounds[1]` for all `x` instead.

To work with the rest of the code without incident, your new `solve_linear_program` function must return an object with the following properties:

* `x`: The solution to the linear program.
* `fun`: The objective function value.
* `slack`: The slack in the inequalities in the solution, nominally equal to `b_ub - A_ub x`.

If it isn't plug-and-play after that, you've either found a bug in the code or an error in the README.
