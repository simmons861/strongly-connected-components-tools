"""Strongly connected components of a directed graph using Tarjan's algorithm.

This package exposes a single public function, :func:`strongly_connected_components`,
together with the :class:`Graph` helper type that wraps a plain dict-based adjacency
list.  The implementation is iterative: recursion is avoided so that graphs with
long chains do not exhaust the interpreter stack.
"""

from .core import Graph, strongly_connected_components

__all__ = ["Graph", "strongly_connected_components"]
