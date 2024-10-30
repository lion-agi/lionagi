import zipfile
from pathlib import Path

import pandas as pd

from lionagi.integrations.storage.storage_util import (
    output_edge_list,
    output_node_list,
)


def _output_csv(
    node_list, node_dict, edge_list, edge_cls_list, zipname="structure_storage"
):
    """
    Writes provided node and edge data into multiple CSV files and compresses them into a ZIP archive.

    This helper function takes lists and dictionaries of nodes and edges, converts them to pandas DataFrames,
    and then writes each DataFrame to a CSV file stored inside a ZIP archive. This includes a separate CSV
    for each type of node and edge, as well as edge conditions if they exist.

    Args:
        node_list (list): A list of dictionaries where each dictionary contains attributes of a single node.
        node_dict (dict): A dictionary of lists where each key represents a node type and the value is a list of
                          node attributes for nodes of that type.
        edge_list (list): A list of dictionaries where each dictionary contains attributes of a single edge.
        edge_cls_list (list): A list of dictionaries where each dictionary contains attributes of edge conditions.
        zipname (str): The base name for the output ZIP file that will store the CSV files.

    Returns:
        None: This function does not return a value but outputs a ZIP file containing the CSVs.
    """
    tables = {
        "Nodes": pd.DataFrame(node_list),
        "Edges": pd.DataFrame(edge_list),
    }
    if edge_cls_list:
        tables["EdgesCondClass"] = pd.DataFrame(edge_cls_list)
    for i in node_dict:
        tables[i] = pd.DataFrame(node_dict[i])

    zipname = zipname + ".zip"

    with zipfile.ZipFile(zipname, "w") as zf:
        for i in tables:
            filename = i + ".csv"
            with zf.open(filename, "w") as file:
                tables[i].to_csv(file, index=False)


def to_csv(structure, filename="structure_storage"):
    """
    Converts a structure into a series of CSV files and stores them in a compressed ZIP archive.

    This function processes a given structure to extract detailed node and edge information,
    including conditions if applicable. These details are then saved into separate CSV files
    for nodes, edges, and any edge conditions, which are subsequently bundled into a ZIP file.

    Args:
        structure: An object representing the structure to be serialized. This structure should
                   have methods to return lists of nodes and edges.
        filename (str): The base name of the output ZIP file that will store the CSV files.

    Returns:
        None: This function does not return a value but outputs a ZIP file containing CSVs.
    """
    node_list, node_dict = output_node_list(structure)
    edge_list, edge_cls_list = output_edge_list(structure)

    _output_csv(node_list, node_dict, edge_list, edge_cls_list, filename)
