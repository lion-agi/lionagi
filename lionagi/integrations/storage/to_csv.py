import zipfile
import pandas as pd
from pathlib import Path

from lionagi.integrations.storage.storage_util import output_node_list, output_edge_list


def _output_csv(node_list, node_dict, edge_list, edge_cls_list, zipname='structure_storage'):
    tables = {'Nodes': pd.DataFrame(node_list), 'Edges': pd.DataFrame(edge_list)}
    if edge_cls_list:
        tables['EdgesCondClass'] = pd.DataFrame(edge_cls_list)
    for i in node_dict:
        tables[i] = pd.DataFrame(node_dict[i])

    zipname = zipname + '.zip'

    with zipfile.ZipFile(zipname, 'w') as zf:
        for i in tables:
            filename = i + '.csv'
            with zf.open(filename, 'w') as file:
                tables[i].to_csv(file, index=False)


def to_csv(structure, filename='structure_storage'):
    node_list, node_dict = output_node_list(structure)
    edge_list, edge_cls_list = output_edge_list(structure)

    _output_csv(node_list, node_dict, edge_list, edge_cls_list, filename)
