import pandas as pd
from lionagi.libs import SysUtil

from lionagi.integrations.storage.storage_util import output_node_list, output_edge_list


def _output_excel(node_list, node_dict, edge_list, edge_cls_list, filename='structure_storage'):
    SysUtil.check_import("openpyxl")

    tables = {'Nodes': pd.DataFrame(node_list), 'Edges': pd.DataFrame(edge_list)}
    if edge_cls_list:
        tables['EdgesCondClass'] = pd.DataFrame(edge_cls_list)
    for i in node_dict:
        tables[i] = pd.DataFrame(node_dict[i])

    filename = filename + '.xlsx'

    with pd.ExcelWriter(filename) as writer:
        for i in tables:
            tables[i].to_excel(writer, sheet_name=i, index=False)


def to_excel(structure, filename='structure_storage'):
    node_list, node_dict = output_node_list(structure)
    edge_list, edge_cls_list = output_edge_list(structure)

    _output_excel(node_list, node_dict, edge_list, edge_cls_list, filename)
