import unittest

from strongly_connected_components_tools import Graph, strongly_connected_components


def canonical(components):
    """Return a comparable form: each component as a frozenset, sorted."""
    return sorted((frozenset(c) for c in components), key=lambda s: sorted(s))


class StronglyConnectedComponentsTests(unittest.TestCase):
    def test_empty_graph(self):
        self.assertEqual(strongly_connected_components({}), [])

    def test_single_vertex_no_edges(self):
        self.assertEqual(strongly_connected_components({"a": []}), [["a"]])

    def test_single_vertex_self_loop(self):
        self.assertEqual(strongly_connected_components({"a": ["a"]}), [["a"]])

    def test_two_vertices_one_way(self):
        # a -> b: two separate components, no cycle.
        result = canonical(strongly_connected_components({"a": ["b"], "b": []}))
        self.assertEqual(result, [frozenset(["a"]), frozenset(["b"])])

    def test_two_vertices_cycle(self):
        result = canonical(strongly_connected_components({"a": ["b"], "b": ["a"]}))
        self.assertEqual(result, [frozenset(["a", "b"])])

    def test_three_cycle(self):
        graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
        result = canonical(strongly_connected_components(graph))
        self.assertEqual(result, [frozenset(["a", "b", "c"])])

    def test_neighbour_only_vertex_is_included(self):
        # b appears only as a neighbour; it must still be a component.
        result = canonical(strongly_connected_components({"a": ["b"]}))
        self.assertEqual(result, [frozenset(["a"]), frozenset(["b"])])

    def test_two_disjoint_cycles(self):
        graph = {
            "a": ["b"],
            "b": ["a"],
            "c": ["d"],
            "d": ["c"],
        }
        result = canonical(strongly_connected_components(graph))
        self.assertEqual(
            result, [frozenset(["a", "b"]), frozenset(["c", "d"])]
        )

    def test_chain_of_cycles(self):
        # a <-> b -> c <-> d, with a one-way edge b -> c.
        graph = {
            "a": ["b"],
            "b": ["a", "c"],
            "c": ["d"],
            "d": ["c"],
        }
        result = canonical(strongly_connected_components(graph))
        self.assertEqual(
            result, [frozenset(["a", "b"]), frozenset(["c", "d"])]
        )

    def test_condensation_order_is_reverse_topological(self):
        # b -> a, so {b} should come before {a} in the output because Tarjan
        # finishes a component only when its root is popped, and roots are
        # finished in reverse topological order.
        components = strongly_connected_components({"b": ["a"], "a": []})
        self.assertEqual(components, [["a"], ["b"]])

    def test_self_loop_inside_larger_cycle(self):
        graph = {"a": ["a", "b"], "b": ["a"]}
        result = canonical(strongly_connected_components(graph))
        self.assertEqual(result, [frozenset(["a", "b"])])

    def test_graph_wrapper_accepts_mapping(self):
        graph = Graph({"a": ["b"], "b": ["a"]})
        self.assertEqual(graph.vertices(), {"a", "b"})
        self.assertEqual(list(graph.neighbours("a")), ["b"])
        self.assertEqual(list(graph.neighbours("missing")), [])
        result = canonical(strongly_connected_components(graph))
        self.assertEqual(result, [frozenset(["a", "b"])])

    def test_graph_contains(self):
        graph = Graph({"a": ["b"]})
        self.assertIn("a", graph)
        self.assertIn("b", graph)
        self.assertNotIn("c", graph)

    def test_graph_wrapper_is_not_copied(self):
        # The Graph stores a shallow copy of the mapping, so mutating the
        # caller's dict afterwards does not affect the Graph.
        source = {"a": ["b"]}
        graph = Graph(source)
        source["c"] = []
        self.assertNotIn("c", graph)

    def test_long_chain_does_not_recurse(self):
        # 5000 vertices in a line: a recursive implementation would hit the
        # default recursion limit.  The iterative one should not.
        n = 5000
        graph = {i: [i + 1] for i in range(n - 1)}
        graph[n - 1] = []
        components = strongly_connected_components(graph)
        self.assertEqual(len(components), n)
        self.assertEqual(len({v for c in components for v in c}), n)

    def test_duplicate_edges_are_harmless(self):
        graph = {"a": ["b", "b"], "b": ["a", "a"]}
        result = canonical(strongly_connected_components(graph))
        self.assertEqual(result, [frozenset(["a", "b"])])

    def test_vertices_with_no_edges_are_singletons(self):
        graph = {"a": [], "b": [], "c": []}
        result = canonical(strongly_connected_components(graph))
        self.assertEqual(
            result,
            [frozenset(["a"]), frozenset(["b"]), frozenset(["c"])],
        )

    def test_non_string_vertices(self):
        graph = {1: [2], 2: [1], 3: [4]}
        result = canonical(strongly_connected_components(graph))
        self.assertEqual(result, [frozenset([1, 2]), frozenset([3]), frozenset([4])])


if __name__ == "__main__":
    unittest.main()
