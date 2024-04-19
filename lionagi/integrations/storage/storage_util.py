import json
import inspect
import re

from lionagi.core import System, Instruction
from lionagi.core.tool import Tool
from lionagi.core.generic.action import ActionSelection
from lionagi.core.agent.base_agent import BaseAgent
from lionagi.core.generic.condition import Condition

from lionagi.core import func_to_tool


def output_node_list(structure):
    summary_list = []
    output = {}

    structure_output = {'id': structure.id_, 'timestamp': structure.timestamp, 'type': structure.class_name()}
    summary_list.append(structure_output.copy())
    structure_output['head_nodes'] = [i.id_ for i in structure.get_heads()]
    # structure_output['nodes'] = json.dumps([i for i in structure.internal_nodes.keys()])
    # structure_output['edges'] = json.dumps([i for i in structure.internal_edges.keys()])
    output[structure_output['type']] = [structure_output]
    for node in structure.internal_nodes.values():
        node_output = {'id': node.id_, 'timestamp': node.timestamp, 'type': node.class_name()}
        summary_list.append(node_output.copy())
        if isinstance(node, System) or isinstance(node, Instruction):
            node_output['content'] = json.dumps(node.content)
            node_output['sender'] = node.sender
            node_output['recipient'] = node.recipient
        elif isinstance(node, Tool):
            node_output['function'] = inspect.getsource(node.func)
            # node_output['manual'] = node.manual
            node_output['parser'] = inspect.getsource(node.parser) if node.parser else None
        elif isinstance(node, ActionSelection):
            node_output['action'] = node.action
            node_output['action_kwargs'] = json.dumps(node.action_kwargs)
        elif isinstance(node, BaseAgent):
            node_output['structure_id'] = node.structure.id_
            node_output['output_parser'] = inspect.getsource(node.output_parser)
        else:
            raise ValueError('Not supported node type detected')
        if node_output['type'] not in output:
            output[node_output['type']] = []
        output[node_output['type']].append(node_output)

    return summary_list, output


def output_edge_list(structure):
    edge_list = []
    edge_cls_dict = {}
    for edge in structure.internal_edges.values():
        edge_output = {'id': edge.id_,
                       'timestamp': edge.timestamp,
                       'head': edge.head,
                       'tail': edge.tail,
                       'label': edge.label,
                       'bundle': str(edge.bundle)}
        if edge.condition:
            cls_name = edge.condition.__class__.__qualname__
            cond = json.dumps({"class": cls_name, "args": edge.condition.model_dump()})
            cls = edge.string_condition()
            if cls is not None and cls_name not in edge_cls_dict:
                edge_cls_dict.update({cls_name: cls})
        else:
            cond = None
        edge_output['condition'] = cond
        edge_list.append(edge_output)

    edge_cls_list = []
    for key, value in edge_cls_dict.items():
        edge_cls_list.append({'class_name': key, 'class': value})

    return edge_list, edge_cls_list


class ParseNode:
    @staticmethod
    def convert_to_def(function_code):
        import re

        match = re.search(r"def (\w+)\(", function_code)
        if match:
            class_name = match.group(1)
            try:
                exec(function_code, globals())
                func = globals()[class_name]
                return func
            except Exception as e:
                raise ValueError(f"Failed to convert str to def. Error: {e}")
        else:
            raise ValueError("Failed to detect function name")

    @staticmethod
    def convert_to_class(cls_code):
        import re

        match = re.search(r"class (\w+)\s*(?:\(([^)]+)\))?:", cls_code)
        if match:
            class_name = match.group(1)
            try:
                exec(cls_code, globals())
                cls = globals()[class_name]
                return cls
            except Exception as e:
                raise ValueError(f"Failed to convert str to class. Error: {e}")
        else:
            raise ValueError("Failed to detect class name")

    @staticmethod
    def parse_system(info_dict):
        node = System(" ")
        node.id_ = info_dict['id']
        node.timestamp = info_dict['timestamp']
        node.content = json.loads(info_dict['content'])
        node.sender = info_dict['sender']
        node.recipient = info_dict['recipient']
        return node

    @staticmethod
    def parse_instruction(info_dict):
        node = Instruction(" ")
        node.id_ = info_dict['id']
        node.timestamp = info_dict['timestamp']
        node.content = json.loads(info_dict['content'])
        node.sender = info_dict['sender']
        node.recipient = info_dict['recipient']
        return node

    @staticmethod
    def parse_actionSelection(info_dict):
        node = ActionSelection()
        node.id_ = info_dict['id']
        node.action = info_dict['action']
        if 'action_kwargs' in info_dict:
            if info_dict['action_kwargs']:
                node.action_kwargs = json.loads(info_dict['action_kwargs'])
        elif 'actionKwargs' in info_dict:
            if info_dict['actionKwargs']:
                node.action_kwargs = json.loads(info_dict['actionKwargs'])
        return node

    @staticmethod
    def parse_tool(info_dict):
        func_code = info_dict['function']
        if "import os" in func_code or "__" in func_code or "import sys" in func_code:
            raise ValueError("Unsafe code detected in Tool function. Please double check or implement explicitly")

        func = ParseNode.convert_to_def(func_code)
        tool = func_to_tool(func)
        if func.__doc__:
            if re.search(r":param \w+:", func.__doc__):
                tool = func_to_tool(func, docstring_style="reST")

        tool = tool[0]
        tool.id_ = info_dict['id']
        tool.timestamp = info_dict['timestamp']
        return tool

    @staticmethod
    def parse_condition(condition, cls_code):
        args = condition["args"]
        cls = ParseNode.convert_to_class(cls_code)

        init_params = {}
        for key in inspect.signature(cls.__init__).parameters.keys():
            if key == "self":
                continue
            init_params[key] = args[key]
        return cls(**init_params)





