from __future__ import absolute_import
from __future__ import unicode_literals

from . import structures


__all__ = ['load_from_pair_list', 'load_from_csv']


def load_from_pair_list(node_or_node_id_edge_pairs):
    tree = structures.Tree()
    for start_node_or_node_id, end_node_or_node_id in node_or_node_id_edge_pairs:
        tree.add(start_node_or_node_id, end_node_or_node_id)
    return tree


def _load_from_csv_default_id_validator(value):
    return bool(value) or isinstance(value, int)


def load_from_csv(file_like_object, header_row_count=0, id_column_index=0,
                  parent_column_index=None, child_column_index=None,
                  id_validator=_load_from_csv_default_id_validator,
                  **csv_reader_kwargs):
    import csv

    tree = structures.Tree()
    reader = csv.reader(file_like_object, **csv_reader_kwargs)
    for i, row in enumerate(reader):
        if i < header_row_count:
            continue
        node_id = row[id_column_index]
        if not id_validator(node_id):
            continue
        tree.add(node_id)
        if parent_column_index is not None:
            parent_id = row[parent_column_index]
            if id_validator(parent_id):
                tree.add(parent_id, node_id)
        if child_column_index is not None:
            child_id = row[child_column_index]
            if id_validator(child_id):
                tree.add(node_id, child_id)
    return tree
