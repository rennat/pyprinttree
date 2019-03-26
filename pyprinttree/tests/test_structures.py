from __future__ import absolute_import
from __future__ import unicode_literals

import gc
import os

import psutil
import unittest

import pyprinttree


class NodeTestCase(unittest.TestCase):

    def test_node_equals_id_string(self):
        node = pyprinttree.Node('12345')
        self.assertEqual(node, '12345')

    def test_node_equals_id_int(self):
        node = pyprinttree.Node(12345)
        self.assertEqual(node, 12345)

    def test_node_equals_id_float(self):
        node = pyprinttree.Node(12.3)
        self.assertEqual(node, 12.3)

    def test_node_equals_id_hashable_object(self):
        class HashableObject:
            def __eq__(self, other):
                return hash(self) == hash(other)

            def __hash__(self):
                return 1

        obj = HashableObject()
        node = pyprinttree.Node(obj)
        self.assertEqual(node, obj)

    def test_conform(self):
        a = 'a'
        conformed_a = pyprinttree.Node.conform(a)
        self.assertIsInstance(conformed_a, pyprinttree.Node)
        b = pyprinttree.Node('b')
        conformed_b = pyprinttree.Node.conform(b)
        self.assertIs(b, conformed_b)


class EdgeTestCase(unittest.TestCase):

    def setUp(self):
        self.start_node = pyprinttree.Node('foo')
        self.end_node = pyprinttree.Node('bar')

    def test_edge_equals_node_tuple(self):
        edge = pyprinttree.Edge(self.start_node, self.end_node)
        self.assertEqual(edge, (self.start_node, self.end_node))

    def test_edge_equals_node_id_tuple(self):
        edge = pyprinttree.Edge(self.start_node, self.end_node)
        self.assertEqual(edge, ('foo', 'bar'))


class GraphTestCase(unittest.TestCase):

    def test_add_nodes(self):
        tree = pyprinttree.Tree()
        for id_ in 'abcdef':
            tree.add(pyprinttree.Node(id_))
        self.assertEqual(set(tree.nodes.values()), set('abcdef'))

    def test_add_create_and_add_nodes(self):
        tree = pyprinttree.Tree()
        for id_ in 'abcdef':
            tree.add(id_)
        self.assertEqual(set(tree.nodes.values()), set('abcdef'))

    def test_add_edge(self):
        tree = pyprinttree.Tree()
        nodes = [pyprinttree.Node(id_) for id_ in 'abcdef']
        for node in nodes:
            tree.add(node)
        pairs = list(zip(nodes[:-1], nodes[1:]))
        for start_node, end_node in pairs:
            tree.add(start_node, end_node)
        self.assertEqual(set(tree.nodes.values()), set('abcdef'))
        self.assertEqual(
            set((edge.start, edge.end) for edge in tree.edges.values()),
            set(pairs)
        )

    def test_get_roots(self):
        tree = pyprinttree.Tree()
        tree.add('a', 'b')
        tree.add('a', 'c')
        tree.add('b', 'd')
        self.assertEqual(set(tree.get_roots()), set('a'))
        tree.add('e', 'f')
        self.assertEqual(set(tree.get_roots()), set('ae'))

    def test_iter_nodes_top_down(self):
        tree = pyprinttree.Tree()
        pairs = list(zip('abc', 'bcd')) + list(zip('be', 'ef')) + list(zip('bg', 'gh'))
        for start_node, end_node in pairs:
            tree.add(start_node, end_node)
        tree.add('i')
        iterable = tree.iter_nodestate_top_down()
        self.assertIs(iterable, iter(iterable))
        self.assertEqual(
            [
                (state.node.id, state.generation, state.branch_index)
                for state in iterable
            ],
            [
                ('a', 0, 1),
                ('b', 1, 1),
                ('g', 2, 3),
                ('h', 3, 3),
                ('e', 2, 2),
                ('f', 3, 2),
                ('c', 2, 1),
                ('d', 3, 1),
                ('i', 0, 0),
            ]
        )


class MemoryUsageTestCase(unittest.TestCase):

    @staticmethod
    def create_large_tree():
        tree = pyprinttree.Tree()
        ids = list(range(10000))
        for start, end in zip(ids[1:], ids[:-1]):
            tree.add(start, end)
        return tree

    def test_linked_nodes_are_cleaned_up_by_garbage_collection(self):
        """
        Test that unreferenced linked nodes are picked up by garbage collection.

        NOTE: If this test fails it may not indicate an actual problem because of the
        technique employed to test memory recovery.
        """
        process = psutil.Process(os.getpid())
        starting_usage = process.memory_info().rss
        tree = self.create_large_tree()
        full_usage = process.memory_info().rss
        del tree
        gc.collect()
        final_usage = process.memory_info().rss
        used = full_usage - starting_usage
        cleaned = full_usage - final_usage
        delta = abs(used - cleaned)
        self.assertLess(delta, 0.015 * used, "memory usage: {}".format({
            "starting": starting_usage,
            "full": full_usage,
            "final": final_usage,
            "used": used,
            "cleaned": cleaned,
            "delta": delta
        }))
