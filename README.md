# strongly-connected-components-tools

Finds the strongly connected components of a directed graph using Tarjan's single-pass algorithm on a plain dict-based adjacency list.

## Usage

```python
from strongly_connected_components_tools import strongly_connected_components

graph = {
    "a": ["b"],
    "b": ["a", "c"],
    "c": ["d"],
    "d": ["c"],
}

for component in strongly_connected_components(graph):
    print(sorted(component))
# ['a', 'b']
# ['c', 'd']
```

The function also accepts a `Graph` wrapper if you prefer an object with `vertices()` and `neighbours()` helpers:

```python
from strongly_connected_components_tools import Graph, strongly_connected_components

g = Graph({"x": ["y"], "y": ["x"]})
assert strongly_connected_components(g) == [["y", "x"]]
```

## Why this exists

Tarjan's algorithm is short, but the textbook presentation is recursive.  On a graph shaped like a linked list that recursion exhausts CPython's default stack long before the algorithm itself is the bottleneck.  This library uses an explicit work stack instead, so a chain of tens of thousands of vertices is fine.  The trade-off is that the code is a little longer and the lowlink propagation happens on an explicit `"exit"` marker rather than on the way out of a function call; the result is the same but the control flow is worth reading once.

The other decision is that the input is a plain mapping, not a bespoke graph class.  Neighbour-only vertices are included automatically, so `{"a": ["b"]}` produces two components even though `"b"` is not a key.  If you need to build a graph incrementally, use the `Graph` wrapper, whose `adjacency` property is mutable.

## Awkward edge

The order of components in the returned list is the order Tarjan's algorithm finishes them, which is a reverse topological order of the condensation.  That is stable and occasionally useful, but it is *not* sorted by vertex and it is *not* the order the vertices first appear in your dict.  If you need a deterministic presentation, sort each component yourself.
