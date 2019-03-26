from __future__ import absolute_import
from __future__ import unicode_literals

import io
import sys


__all__ = ['render_tree', 'render_tree_to_string']


def render_tree(tree, stream=sys.stdout):
    last_branch_index = 0
    for node, generation, branch_index in tree.iter_nodestate_top_down():
        for step_index in range(last_branch_index, branch_index):
            stream.write('{prefix}\\\n'.format(prefix=' '.join('|' * (step_index + 1))))
        stream.write('{prefix}*{postfix} {label}\n'.format(
            label=node,
            prefix='| ' * branch_index,
            postfix=''
        ))
        last_branch_index = branch_index


def render_tree_to_string(tree):
    stream = io.StringIO()
    render_tree(tree, stream)
    stream.seek(0)
    return stream.read()
