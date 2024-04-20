import pandas as pd
from lionagi.libs import SysUtil

from lionagi.integrations.storage.storage_util import output_node_list, output_edge_list


def _output_excel(
    node_list, node_dict, edge_list, edge_cls_list, filename="structure_storage"
):
    """
    Writes provided node and edge data into multiple sheets of a single Excel workbook.

    This helper function takes lists and dictionaries of nodes and edges, converts them into pandas DataFrames,
    and then writes each DataFrame to a distinct sheet in an Excel workbook. This includes a separate sheet
    for each type of node and edge, as well as edge conditions if they exist.

    Args:
        node_list (list): A list of dictionaries where each dictionary contains attributes of a single node.
        node_dict (dict): A dictionary of lists where each key represents a node type and the value is a list of
                          node attributes for nodes of that type.
        edge_list (list): A list of dictionaries where each dictionary contains attributes of a single edge.
        edge_cls_list (list): A list of dictionaries where each dictionary contains attributes of edge conditions.
        filename (str): The base name for the output Excel file. The '.xlsx' extension will be added
                        automatically if not included.

    Returns:
        None: This function does not return a value but writes data directly to an Excel workbook.

    Raises:
        ImportError: If the required 'openpyxl' library is not installed, which is necessary for pandas to write Excel files.
    """
    SysUtil.check_import("openpyxl")

    tables = {"Nodes": pd.DataFrame(node_list), "Edges": pd.DataFrame(edge_list)}
    if edge_cls_list:
        tables["EdgesCondClass"] = pd.DataFrame(edge_cls_list)
    for i in node_dict:
        tables[i] = pd.DataFrame(node_dict[i])

    filename = filename + ".xlsx"

    with pd.ExcelWriter(filename) as writer:
        for i in tables:
            tables[i].to_excel(writer, sheet_name=i, index=False)


def to_excel(structure, filename="structure_storage"):
    """
    Converts a structure into a series of Excel sheets within a single workbook.

    This function processes the specified structure to extract detailed node and edge information,
    including conditions if applicable. These details are then saved into separate sheets within an
    Excel workbook for nodes, edges, and any edge conditions.

    Args:
        structure: An object representing the structure to be serialized. This should have methods
                   to return lists of nodes and edges suitable for output.
        filename (str): The base name of the output Excel file. The '.xlsx' extension will be added
                        automatically if not included.

    Returns:
        None: This function does not return a value but outputs an Excel workbook with multiple sheets.
    """
    node_list, node_dict = output_node_list(structure)
    edge_list, edge_cls_list = output_edge_list(structure)

    _output_excel(node_list, node_dict, edge_list, edge_cls_list, filename)
