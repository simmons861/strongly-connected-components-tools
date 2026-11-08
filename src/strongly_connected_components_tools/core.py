"""Tarjan's single-pass algorithm for strongly connected components.

A strongly connected component (SCC) of a directed graph is a maximal set of
vertices such that every vertex can reach every other vertex in the set.  Tarjan's
algorithm finds all SCCs in O(V + E) time using one depth-first traversal.

The implementation here is deliberately iterative.  A recursive version is shorter
but blows the Python recursion limit on graphs whose depth exceeds ~1000, which is
common for linked-list-shaped inputs.  The explicit stack costs a little clarity and
is worth it.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set


class Graph:
    """A directed graph stored as a plain dict-based adjacency list.

    The mapping maps each vertex to an iterable of its out-neighbours.  Vertices
    that appear only as neighbours (and never as keys) are still part of the graph;
    they are treated as having no outgoing edges.  This mirrors the way people
    usually build adjacency dicts by hand and avoids forcing a normalisation pass
    on the caller.

    Vertices may be any hashable value.  The graph is not copied, so mutating the
    underlying mapping after construction changes the graph seen by the algorithms.
    """

    def __init__(self, adjacency: Optional[Mapping] = None) -> None:
        # Store a shallow copy of the mapping so the caller's dict object identity
        # is not tied to ours, but keep the neighbour iterables as given.  Copying
        # them would be surprising for large graphs and is not needed for the
        # algorithms, which only iterate.
        self._adjacency: Dict = dict(adjacency) if adjacency is not None else {}

    @property
    def adjacency(self) -> Dict:
        """Return the underlying adjacency mapping (mutable)."""
        return self._adjacency

    def vertices(self) -> Set:
        """Return the set of all vertices, including neighbour-only ones."""
        result: Set = set(self._adjacency.keys())
        for neighbours in self._adjacency.values():
            result.update(neighbours)
        return result

    def neighbours(self, vertex) -> Iterable:
        """Return the out-neighbours of ``vertex`` (empty if it has none)."""
        return self._adjacency.get(vertex, ())

    def __contains__(self, vertex) -> bool:
        return vertex in self._adjacency or any(
            vertex in neighbours for neighbours in self._adjacency.values()
        )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "Graph({!r})".format(self._adjacency)


def strongly_connected_components(graph) -> List[List]:
    """Return the strongly connected components of ``graph``.

    ``graph`` may be a :class:`Graph` or any mapping from a vertex to an iterable
    of its out-neighbours.  The result is a list of lists; each inner list is one
    SCC.  Within a component the vertices appear in the order Tarjan's algorithm
    finishes them, and the components themselves are ordered by the finish order
    of their roots.  That order is a valid reverse topological order of the
    condensation, which is occasionally useful and costs nothing to preserve.

    Isolated vertices (present as keys with no neighbours, or absent entirely)
    each form their own singleton component.  Self-loops are fine: a vertex with
    an edge to itself is a one-vertex SCC.
    """
    adjacency = graph.adjacency if isinstance(graph, Graph) else graph

    index_counter = 0
    indices: Dict = {}
    lowlink: Dict = {}
    on_stack: Set = set()
    tarjan_stack: List = []
    components: List[List] = []

    # Collect every vertex up front.  We need to start a DFS from vertices that
    # have no incoming edges as well as from those that do, and the adjacency
    # mapping alone does not tell us about neighbour-only vertices.
    all_vertices: Set = set(adjacency.keys())
    for neighbours in adjacency.values():
        all_vertices.update(neighbours)

    for root in all_vertices:
        if root in indices:
            continue

        # Each work item is either ("enter", vertex) or ("exit", vertex).  The
        # "exit" marker lets us perform the lowlink update after all children of
        # the vertex have been processed, which is what the recursive version
        # would do on the way back up the call stack.
        work: List[tuple] = [("enter", root)]
        while work:
            action, vertex = work.pop()

            if action == "enter":
                indices[vertex] = index_counter
                lowlink[vertex] = index_counter
                index_counter += 1
                tarjan_stack.append(vertex)
                on_stack.add(vertex)

                # Push the exit marker first so it runs after all children.  Then
                # push children in reverse so they are visited in the order the
                # caller supplied, which keeps the output stable across runs.
                work.append(("exit", vertex))
                neighbours = list(adjacency.get(vertex, ()))
                for neighbour in reversed(neighbours):
                    if neighbour not in indices:
                        work.append(("enter", neighbour))
                    elif neighbour in on_stack:
                        # Back edge or cross edge to a vertex still on the Tarjan
                        # stack: it belongs to the current SCC candidate.
                        if indices[neighbour] < lowlink[vertex]:
                            lowlink[vertex] = indices[neighbour]
            else:  # action == "exit"
                # All descendants have been processed.  Propagate the lowlink to
                # the parent, but only for tree edges; the child list is no longer
                # available here, so we approximate by looking at every neighbour
                # and updating the parent's lowlink when the neighbour is a child
                # that has finished and is still on the stack.
                for neighbour in adjacency.get(vertex, ()):
                    if neighbour in on_stack and lowlink[neighbour] < lowlink[vertex]:
                        lowlink[vertex] = lowlink[neighbour]

                if lowlink[vertex] == indices[vertex]:
                    component: List = []
                    while True:
                        member = tarjan_stack.pop()
                        on_stack.discard(member)
                        component.append(member)
                        if member == vertex:
                            break
                    components.append(component)

    return components
