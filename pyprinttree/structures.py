from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import weakref

from . import constants
from . import exceptions


__all__ = ('Node', 'Edge', 'Tree',)


class Node:

    @classmethod
    def conform(cls, node_or_node_id):
        if isinstance(node_or_node_id, cls):
            return node_or_node_id
        return cls(node_or_node_id)

    def __init__(self, node_id):
        self._id = node_id
        self._parent_edge_refs = dict()
        self._child_edge_refs = dict()

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return self.id

    def __repr__(self):
        return str(self)

    @property
    def id(self):
        return self._id

    def add_edge(self, edge):
        if self.id == edge.start.id:
            self._child_edge_refs[edge.end.id] = weakref.ref(edge)
        elif self.id == edge.end.id:
            self._parent_edge_refs[edge.start.id] = weakref.ref(edge)
        else:
            raise exceptions.EdgeDoesNotLinkNode()

    @property
    def parents(self):
        return [ref().start for ref in self._parent_edge_refs.values()]

    @property
    def children(self):
        return [ref().end for ref in self._child_edge_refs.values()]

    def is_root(self):
        return len(self._parent_edge_refs) == 0

    def is_leaf(self):
        return len(self._child_edge_refs) == 0


class Edge:

    @classmethod
    def make_hash(cls, start_node, end_node):
        return hash((start_node, end_node))

    def __init__(self, start_node, end_node):
        if start_node == end_node:
            raise exceptions.EdgeFormsLoop()
        self._start_ref = weakref.ref(start_node)
        self._end_ref = weakref.ref(end_node)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return self.make_hash(self.start, self.end)

    @property
    def start(self):
        return self._start_ref()

    @property
    def end(self):
        return self._end_ref()


class Tree:

    NodeState = collections.namedtuple('NodeState', ('node', 'generation', 'branch_index',))
    NodeWithScions = collections.namedtuple('NodeWithScions', ('node', 'scions',))

    def __init__(self):
        self._nodes = dict()
        self._edges = dict()

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    def get_node(self, node_id):
        return self._nodes.get(node_id, constants.DoesNotExist)

    def get_edge(self, start_node, end_node):
        return self._edges.get(Edge.make_hash(start_node, end_node), constants.DoesNotExist)

    def add_node(self, node):
        if node in self._nodes:
            raise exceptions.DuplicateNode()
        self._nodes[node.id] = node

    def add_edge(self, edge):
        if edge in self._edges:
            raise exceptions.DuplicateEdge()
        self._edges[edge] = edge
        edge.start.add_edge(edge)
        edge.end.add_edge(edge)

    def get_or_create_and_add_node(self, node_or_node_id):
        node = self.get_node(node_or_node_id)
        if node is constants.DoesNotExist:
            node = Node.conform(node_or_node_id)
            self.add_node(node)
        return node

    def get_or_create_and_add_edge(self, start_node_or_node_id, end_node_or_node_id):
        start_node = Node.conform(start_node_or_node_id)
        end_node = Node.conform(end_node_or_node_id)
        edge = self.get_edge(start_node, end_node)
        if edge is constants.DoesNotExist:
            edge = Edge(start_node, end_node)
            self.add_edge(edge)
        return edge

    def add(self, node_or_node_id, end_node_or_node_id=None):
        """
        The most flexible interface to add Nodes and Edges to a Tree.
        Either adds a single Node to the Tree and returns it
        OR adds an Edge and returns it.
        """
        start_node = self.get_or_create_and_add_node(node_or_node_id)
        if end_node_or_node_id is None:
            return start_node
        end_node = self.get_or_create_and_add_node(end_node_or_node_id)
        edge = self.get_or_create_and_add_edge(start_node, end_node)
        return start_node, end_node, edge

    def get_roots(self):
        return [node for node in self._nodes.values() if node.is_root()]

    def get_leaves(self):
        return [node for node in self._nodes.values() if node.is_leaf()]

    def iter_nodefamilystate_bottom_up(self):
        seen = set()
        deque = collections.deque()
        for node in sorted(self.get_leaves(), key=lambda n: n.id, reverse=True):
            deque.append(self.NodeWithScions(node, 0))
        while True:
            try:
                state = deque.pop()
            except IndexError:
                break
            seen.add(state.node.id)
            yield state
            for parent in state.node.parents:
                if parent.id in seen:
                    continue
                deque.append(self.NodeWithScions(parent, state.scions + 1))

    def iter_nodestate_top_down(self):
        scion_counts = {
            state.node.id: state.scions
            for state in self.iter_nodefamilystate_bottom_up()
        }
        deque = collections.deque()
        for i, node in enumerate(sorted(self.get_roots(), key=lambda n: n.id, reverse=True)):
            deque.append(self.NodeState(node, 0, i))
        while True:
            try:
                state = deque.pop()
            except IndexError:
                break
            yield state
            child_iterator = sorted(state.node.children, key=lambda n: (-scion_counts[n.id], n.id))
            for i, child in enumerate(child_iterator):
                deque.append(self.NodeState(child, state.generation + 1, state.branch_index + i))
