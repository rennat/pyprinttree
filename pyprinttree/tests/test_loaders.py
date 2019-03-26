from __future__ import absolute_import
from __future__ import unicode_literals

import csv
import io
import sys
import unittest

import pyprinttree.loaders


class ListLoaderTestCase(unittest.TestCase):

    def test_loads_node_id_edge_pairs(self):
        node_ids = 'abcdef'
        node_id_edge_pairs = list(zip(node_ids[1:], node_ids[:-1]))
        tree = pyprinttree.loaders.load_from_list(node_id_edge_pairs)
        self.assertEqual(set(n.id for n in tree.nodes.values()), set(node_ids))
        self.assertEqual(
            set((e.start.id, e.end.id) for e in tree.edges.values()),
            set(node_id_edge_pairs)
        )


class CsvLoaderTestCase(unittest.TestCase):

    @staticmethod
    def make_fake_csv_file_handle(*rows):
        if sys.version > '3.0.0':
            fake_handle = io.StringIO()
        else:
            fake_handle = io.BytesIO()
        writer = csv.writer(fake_handle)
        writer.writerows(rows)
        fake_handle.seek(0)
        return fake_handle

    def test_loads_from_csv(self):
        fake_handle = self.make_fake_csv_file_handle(
            ('a', 1, 2, 3),
            ('b', 1, 2, 3),
            ('c', 1, 2, 3)
        )
        tree = pyprinttree.loaders.load_from_csv(fake_handle)
        self.assertEqual(set(n.id for n in tree.nodes.values()), set('abc'))
        self.assertEqual(len(tree.edges), 0)

    def test_id_column_index(self):
        fake_handle = self.make_fake_csv_file_handle(
            (1, 'a', 2, 3),
            (1, 'b', 2, 3),
            (1, 'c', 2, 3)
        )
        tree = pyprinttree.loaders.load_from_csv(fake_handle, id_column_index=1)
        self.assertEqual(set(n.id for n in tree.nodes.values()), set('abc'))
        self.assertEqual(len(tree.edges), 0)

    def test_ignore_header_rows(self):
        fake_handle = self.make_fake_csv_file_handle(
            ('header', 'x', 'y', 'z'),
            ('a', 1, 2, 3),
            ('b', 1, 2, 3),
            ('c', 1, 2, 3)
        )
        tree = pyprinttree.loaders.load_from_csv(fake_handle, header_row_count=1)
        self.assertEqual(set(n.id for n in tree.nodes.values()), set('abc'))
        self.assertEqual(len(tree.edges), 0)

    def test_default_validator(self):
        fake_handle = self.make_fake_csv_file_handle(
            ('', 1, 2, 3),
            (0, 1, 2, 3),
            (None, 1, 2, 3)
        )
        tree = pyprinttree.loaders.load_from_csv(fake_handle, header_row_count=1)
        self.assertEqual(set(n.id for n in tree.nodes.values()), set('0'))
        self.assertEqual(len(tree.edges), 0)

    def test_loads_parent_relations(self):
        fake_handle = self.make_fake_csv_file_handle(
            ('a', None, 2, 3),
            ('b', 'a', 2, 3),
            ('c', 'b', 2, 3)
        )
        tree = pyprinttree.loaders.load_from_csv(fake_handle, parent_column_index=1)
        self.assertEqual(set(n.id for n in tree.nodes.values()), set('abc'))
        self.assertEqual(
            set((e.start.id, e.end.id) for e in tree.edges.values()),
            {('a', 'b'), ('b', 'c')}
        )

    def test_loads_child_relations(self):
        fake_handle = self.make_fake_csv_file_handle(
            ('a', 'b', 2, 3),
            ('b', 'c', 2, 3),
            ('c', None, 2, 3)
        )
        tree = pyprinttree.loaders.load_from_csv(fake_handle, child_column_index=1)
        self.assertEqual(set(n.id for n in tree.nodes.values()), set('abc'))
        self.assertEqual(
            set((e.start.id, e.end.id) for e in tree.edges.values()),
            {('a', 'b'), ('b', 'c')}
        )
