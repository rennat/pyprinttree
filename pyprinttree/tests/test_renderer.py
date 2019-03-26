from __future__ import absolute_import
from __future__ import unicode_literals

import textwrap
import unittest

from pyprinttree import load_from_pair_list
from pyprinttree import render_tree_to_string


class RendererTestCase(unittest.TestCase):

    @staticmethod
    def render(node_id_pairs):
        tree = load_from_pair_list(node_id_pairs)
        return render_tree_to_string(tree)

    def test_render_single_branch(self):
        actual = self.render([
            ('a', 'b'),
            ('b', 'c'),
            ('c', 'd'),
        ])
        expected = textwrap.dedent(r'''
            * a
            * b
            * c
            * d
        ''').lstrip('\n')
        self.assertEqual(actual, expected)

    def test_render_dual_branches(self):
        actual = self.render([
            ('a', 'b'),
            ('b', 'c'),
            ('c', 'd'),
            ('a', 'e'),
            ('e', 'f'),
        ])
        expected = textwrap.dedent(r'''
            * a
            |\
            | * e
            | * f
            * b
            * c
            * d
        ''').lstrip('\n')
        self.assertEqual(actual, expected)

    def test_render_triple_branches(self):
        actual = self.render([
            ('a', 'b'),
            ('b', 'c'),
            ('c', 'd'),
            ('a', 'e'),
            ('e', 'f'),
            ('a', 'g'),
        ])
        expected = textwrap.dedent(r'''
            * a
            |\
            | |\
            | | * g
            | * e
            | * f
            * b
            * c
            * d
        ''').lstrip('\n')
        self.assertEqual(actual, expected)
