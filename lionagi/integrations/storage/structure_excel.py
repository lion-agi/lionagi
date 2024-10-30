import json
from pathlib import Path

import pandas as pd

from lionagi.core.agent.base_agent import BaseAgent
from lionagi.core.engine.instruction_map_engine import InstructionMapEngine
from lionagi.core.executor.base_executor import BaseExecutor
from lionagi.core.executor.graph_executor import GraphExecutor
from lionagi.integrations.storage.storage_util import ParseNode


def excel_reload(
    structure_name=None, structure_id=None, dir="structure_storage"
):
    """
    Loads a structure from an Excel file into a StructureExecutor instance.

    This function uses the StructureExcel class to handle the reloading process. It identifies the
    Excel file based on the provided structure name or ID and reloads the structure from it.

    Args:
        structure_name (str, optional): The name of the structure to reload.
        structure_id (str, optional): The unique identifier of the structure to reload.
        dir (str): The directory path where the Excel files are stored.

    Returns:
        StructureExecutor: An instance of StructureExecutor containing the reloaded structure.

    Raises:
        ValueError: If neither structure_name nor structure_id is provided, or if multiple or no files
                    are found matching the criteria.
    """
    excel_structure = StructureExcel(structure_name, structure_id, dir)
    excel_structure.reload()
    return excel_structure.structure


class StructureExcel:
    """
    Manages the reloading of structures from Excel files.

    This class handles the identification and parsing of structure data from an Excel workbook. It supports
    loading from specifically named Excel files based on the structure name or ID.

    Attributes:
        structure (StructureExecutor): The loaded structure, ready for execution.
        default_agent_executable (BaseExecutor): The default executor for agents within the structure.

    Methods:
        get_heads(): Retrieves the head nodes of the loaded structure.
        parse_node(info_dict): Parses a node from the structure based on the provided dictionary.
        get_next(node_id): Gets the next nodes connected by outgoing edges from a given node.
        relate(parent_node, node): Relates two nodes within the structure based on the edge definitions.
        parse(node_list, parent_node=None): Recursively parses nodes and their relationships from the structure.
        reload(): Reloads the structure from the Excel file based on the initially provided parameters.
    """

    structure: GraphExecutor = GraphExecutor()
    default_agent_executable: BaseExecutor = InstructionMapEngine()

    def __init__(
        self,
        structure_name=None,
        structure_id=None,
        file_path="structure_storage",
    ):
        """
        Initializes the StructureExcel class with specified parameters.

        This method sets up the paths and reads the Excel file, preparing the internal dataframes used for
        structure parsing.

        Args:
            structure_name (str, optional): The name of the structure to reload.
            structure_id (str, optional): The unique identifier of the structure to reload.
            file_path (str): The base path where the Excel files are stored.

        Raises:
            ValueError: If both structure_name and structure_id are provided but do not correspond to a valid file,
                        or if multiple or no files are found when one of the identifiers is provided.
        """
        self.file_path = file_path
        if not structure_name and not structure_id:
            raise ValueError("Please provide the structure name or id")
        if structure_name and structure_id:
            self.filename = f"{file_path}/{structure_name}_{structure_id}.xlsx"
            self.file = pd.read_excel(self.filename, sheet_name=None)
        elif structure_name and not structure_id:
            dir_path = Path(file_path)
            files = list(dir_path.glob(f"{structure_name}*.xlsx"))
            filename = []
            for file in files:
                try:
                    name = file.name
                    name = name.rsplit("_", 1)[0]
                    if name == structure_name:
                        filename.append(file.name)
                except:
                    continue
            if len(filename) > 1:
                raise ValueError(
                    f"Multiple files starting with the same structure name {structure_name} has found, please specify the structure id"
                )
            self.filename = f"{file_path}/{filename[0]}"
            self.file = pd.read_excel(self.filename, sheet_name=None)
        elif structure_id and not structure_name:
            dir_path = Path(file_path)
            files = list(dir_path.glob(f"*{structure_id}.xlsx"))
            filename = [file.name for file in files]
            if len(filename) > 1:
                raise ValueError(
                    f"Multiple files with the same structure id {structure_id} has found, please double check the stored structure"
                )
            self.filename = f"{file_path}/{filename[0]}"
            self.file = pd.read_excel(self.filename, sheet_name=None)
        self.nodes = self.file["Nodes"]
        self.edges = self.file["Edges"]

    def get_heads(self):
        """
        Retrieves the list of head node identifiers from the loaded structure data.

        This method parses the 'StructureExecutor' sheet in the loaded Excel file to extract the list of head nodes.

        Returns:
            list: A list of identifiers for the head nodes in the structure.
        """
        structure_df = self.file["GraphExecutor"]
        head_list = json.loads(structure_df["head_nodes"].iloc[0])
        return head_list

    def _reload_info_dict(self, node_id):
        """
        Retrieves detailed information about a specific node from the Excel file based on its identifier.

        This method looks up a node's information within the loaded Excel sheets and returns a dictionary
        containing all the relevant details.

        Args:
            node_id (str): The identifier of the node to look up.

        Returns:
            dict: A dictionary containing the properties and values for the specified node.
        """
        node_type = self.nodes[self.nodes["ln_id"] == node_id]["type"].iloc[0]
        node_file = self.file[node_type]
        row = node_file[node_file["ln_id"] == node_id].iloc[0]
        info_dict = row.to_dict()
        return info_dict

    def parse_agent(self, info_dict):
        """
        Parses an agent node from the structure using the agent's specific details provided in a dictionary.

        This method creates an agent instance based on the information from the dictionary, which includes
        dynamically loading the output parser code.

        Args:
            info_dict (dict): A dictionary containing details about the agent node, including its class, structure ID,
                              and output parser code.

        Returns:
            BaseAgent: An initialized agent object.
        """
        output_parser = ParseNode.convert_to_def(info_dict["output_parser"])

        structure_excel = StructureExcel(
            structure_id=info_dict["structure_id"], file_path=self.file_path
        )
        structure_excel.reload()
        structure = structure_excel.structure
        agent = BaseAgent(
            structure=structure,
            executable=self.default_agent_executable,
            output_parser=output_parser,
            ln_id=info_dict["ln_id"],
            timestamp=info_dict["timestamp"],
        )
        return agent

    def parse_node(self, info_dict):
        """
        Parses a node from its dictionary representation into a specific node type like System, Instruction, etc.

        This method determines the type of node from the info dictionary and uses the appropriate parsing method
        to create an instance of that node type.

        Args:
            info_dict (dict): A dictionary containing node data, including the node type and associated properties.

        Returns:
            Node: An instance of the node corresponding to the type specified in the info_dict.
        """
        if info_dict["type"] == "System":
            return ParseNode.parse_system(info_dict)
        elif info_dict["type"] == "Instruction":
            return ParseNode.parse_instruction(info_dict)
        elif info_dict["type"] == "Tool":
            return ParseNode.parse_tool(info_dict)
        elif info_dict["type"] == "DirectiveSelection":
            return ParseNode.parse_directiveSelection(info_dict)
        elif info_dict["type"] == "BaseAgent":
            return self.parse_agent(info_dict)

    def get_next(self, node_id):
        """
        Retrieves the list of identifiers for nodes that are directly connected via outgoing edges from the specified node.

        This method searches the 'Edges' DataFrame for all entries where the specified node is a head and returns
        a list of the tail node identifiers.

        Args:
            node_id (str): The identifier of the node whose successors are to be found.

        Returns:
            list[str]: A list of identifiers for the successor nodes.
        """
        return self.edges[self.edges["head"] == node_id]["tail"].to_list()

    def relate(self, parent_node, node):
        """
        Establishes a relationship between two nodes in the structure based on the Excel data for edges.

        This method looks up the edge details connecting the two nodes and applies any conditions associated
        with the edge to the structure being rebuilt.

        Args:
            parent_node (Node): The parent node in the relationship.
            node (Node): The child node in the relationship.

        Raises:
            ValueError: If there are issues with the edge data such as multiple undefined edges.
        """
        if not parent_node:
            return
        row = self.edges[
            (self.edges["head"] == parent_node.ln_id)
            & (self.edges["tail"] == node.ln_id)
        ]
        if len(row) > 1:
            raise ValueError(
                f"currently does not support handle multiple edges between two nodes, Error node: from {parent_node.ln_id} to {node.ln_id}"
            )
        if row["condition"].isna().any():
            self.structure.add_edge(parent_node, node)
        else:
            cond = json.loads(row["condition"].iloc[0])
            cond_cls = cond["class"]
            cond_row = self.file["EdgesCondClass"][
                self.file["EdgesCondClass"]["class_name"] == cond_cls
            ]
            cond_code = cond_row["class"].iloc[0]
            condition = ParseNode.parse_condition(cond, cond_code)
            self.structure.add_edge(parent_node, node, condition=condition)

    def parse(self, node_list, parent_node=None):
        """
        Recursively parses a list of nodes and establishes their interconnections based on the Excel data.

        This method processes each node ID in the list, parsing individual nodes and relating them according
        to their connections defined in the Excel file.

        Args:
            node_list (list[str]): A list of node identifiers to be parsed.
            parent_node (Node, optional): The parent node to which the nodes in the list are connected.

        Raises:
            ValueError: If an error occurs during parsing or relating nodes.
        """
        for node_id in node_list:
            info_dict = self._reload_info_dict(node_id)
            node = self.parse_node(info_dict)

            if node.ln_id not in self.structure.internal_nodes:
                self.structure.add_node(node)
            self.relate(parent_node, node)

            next_node_list = self.get_next(node_id)
            self.parse(next_node_list, node)

    def reload(self):
        """
        Reloads the entire structure from the Excel file.

        This method initializes a new StructureExecutor and uses the Excel data to rebuild the entire structure,
        starting from the head nodes and recursively parsing and connecting all nodes defined within.
        """
        self.structure = GraphExecutor()
        heads = self.get_heads()
        self.parse(heads)
