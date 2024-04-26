import pandas as pd
import json
from pathlib import Path

from lionagi.integrations.storage.storage_util import ParseNode
from lionagi.core.execute.structure_executor import StructureExecutor
from lionagi.core.agent.base_agent import BaseAgent
from lionagi.core.execute.base_executor import BaseExecutor
from lionagi.core.execute.instruction_map_executor import InstructionMapExecutor


def excel_reload(structure_name=None, structure_id=None, file_path="structure_storage"):
    excel_structure = StructureExcel(structure_name, structure_id, file_path)
    excel_structure.reload()
    return excel_structure.structure


class StructureExcel:
    structure: StructureExecutor = StructureExecutor()
    default_agent_executable: BaseExecutor = InstructionMapExecutor()

    def __init__(self, structure_name=None, structure_id=None, file_path="structure_storage"):
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
                    f"Multiple files starting with the same structure name {structure_name} has found, please specify the structure id")
            self.filename = f"{file_path}/{filename[0]}"
            self.file = pd.read_excel(self.filename, sheet_name=None)
        elif structure_id and not structure_name:
            dir_path = Path(file_path)
            files = list(dir_path.glob(f"*{structure_id}.xlsx"))
            filename = [file.name for file in files]
            if len(filename) > 1:
                raise ValueError(
                    f"Multiple files with the same structure id {structure_id} has found, please double check the stored structure")
            self.filename = f"{file_path}/{filename[0]}"
            self.file = pd.read_excel(self.filename, sheet_name=None)
        self.nodes = self.file["Nodes"]
        self.edges = self.file["Edges"]

    def get_heads(self):
        structure_df = self.file["StructureExecutor"]
        head_list = json.loads(structure_df["head_nodes"].iloc[0])
        return head_list

    def _reload_info_dict(self, node_id):
        node_type = self.nodes[self.nodes["id"] == node_id]["type"].iloc[0]
        node_file = self.file[node_type]
        row = node_file[node_file["id"] == node_id].iloc[0]
        info_dict = row.to_dict()
        return info_dict

    def parse_agent(self, info_dict):
        output_parser = ParseNode.convert_to_def(info_dict["output_parser"])

        structure_excel = StructureExcel(structure_id=info_dict["structure_id"], file_path=self.file_path)
        structure_excel.reload()
        structure = structure_excel.structure
        agent = BaseAgent(structure=structure, executable=self.default_agent_executable, output_parser=output_parser)
        agent.id_ = info_dict["id"]
        agent.timestamp = info_dict["timestamp"]
        return agent

    def parse_node(self, info_dict):
        if info_dict["type"] == "System":
            return ParseNode.parse_system(info_dict)
        elif info_dict["type"] == "Instruction":
            return ParseNode.parse_instruction(info_dict)
        elif info_dict["type"] == "Tool":
            return ParseNode.parse_tool(info_dict)
        elif info_dict["type"] == "ActionSelection":
            return ParseNode.parse_actionSelection(info_dict)
        elif info_dict["type"] == "BaseAgent":
            return self.parse_agent(info_dict)

    def get_next(self, node_id):
        return self.edges[self.edges["head"] == node_id]["tail"].to_list()

    def relate(self, parent_node, node):
        if not parent_node:
            return
        row = self.edges[(self.edges["head"] == parent_node.id_) & (self.edges["tail"] == node.id_)]
        if len(row) > 1:
            raise ValueError(
                f"currently does not support handle multiple edges between two nodes, Error node: from {parent_node.id_} to {node.id_}")
        if row['condition'].isna().any():
            self.structure.relate_nodes(parent_node, node)
        else:
            cond = json.loads(row["condition"].iloc[0])
            cond_cls = cond["class"]
            cond_row = self.file["EdgesCondClass"][self.file["EdgesCondClass"]["class_name"] == cond_cls]
            cond_code = cond_row["class"].iloc[0]
            condition = ParseNode.parse_condition(cond, cond_code)
            self.structure.relate_nodes(parent_node, node, condition=condition)

    def parse(self, node_list, parent_node=None):
        for node_id in node_list:
            info_dict = self._reload_info_dict(node_id)
            node = self.parse_node(info_dict)

            if node.id_ not in self.structure.internal_nodes:
                self.structure.add_node(node)
            self.relate(parent_node, node)

            next_node_list = self.get_next(node_id)
            self.parse(next_node_list, node)

    def reload(self):
        self.structure = StructureExecutor()
        heads = self.get_heads()
        self.parse(heads)