import inspect
import json
import re

from lionagi.core.action import DirectiveSelection, Tool, func_to_tool
from lionagi.core.agent.base_agent import BaseAgent
from lionagi.core.generic.edge_condition import EdgeCondition
from lionagi.core.message import Instruction, RoledMessage, System


def output_node_list(structure):
    """
    Processes a structure object to extract and format all associated nodes into a summary list and detailed output dictionary.

    This function traverses a structure, extracting key properties of nodes and organizing them by type into a dictionary for easy access and manipulation.

    Args:
        structure: The structure object containing nodes and potentially other nested structures.

    Returns:
        tuple: A tuple containing a summary list of all nodes and a dictionary categorizing nodes by type.
    """
    summary_list = []
    output = {}

    structure_output = {
        "ln_id": structure.ln_id,
        "timestamp": structure.timestamp,
        "type": structure.class_name,
    }
    summary_list.append(structure_output.copy())
    structure_output["head_nodes"] = json.dumps(
        [i.ln_id for i in structure.get_heads()]
    )
    # structure_output['nodes'] = json.dumps([i for i in structure.internal_nodes.keys()])
    # structure_output['edges'] = json.dumps([i for i in structure.internal_edges.keys()])
    output[structure_output["type"]] = [structure_output]
    for node in structure.internal_nodes.values():
        node_output = {
            "ln_id": node.ln_id,
            "timestamp": node.timestamp,
            "type": node.class_name,
        }
        summary_list.append(node_output.copy())
        if isinstance(node, System) or isinstance(node, Instruction):
            node_output["content"] = json.dumps(node.content)
            # node_output["sender"] = node.sender
            # node_output["recipient"] = node.recipient
        elif isinstance(node, Tool):
            node_output["function"] = inspect.getsource(node.function)
            # node_output['manual'] = node.manual
            node_output["parser"] = (
                inspect.getsource(node.parser) if node.parser else None
            )
        elif isinstance(node, DirectiveSelection):
            node_output["directive"] = node.directive
            node_output["directive_kwargs"] = json.dumps(node.directive_kwargs)
        elif isinstance(node, BaseAgent):
            node_output["structure_id"] = node.structure.ln_id
            node_output["output_parser"] = (
                inspect.getsource(node.output_parser)
                if node.output_parser
                else None
            )
        else:
            raise ValueError("Not supported node type detected")
        if node_output["type"] not in output:
            output[node_output["type"]] = []
        output[node_output["type"]].append(node_output)

    return summary_list, output


def output_edge_list(structure):
    """
    Extracts and formats all edges from a given structure into a list and maps any associated condition classes.

    This function collects edge data from a structure, including identifiers, timestamps, labels, and conditions. It also compiles any unique condition classes associated with these edges.

    Args:
        structure: The structure object containing edges.

    Returns:
        tuple: A tuple containing a list of all edges with their details and a list of unique condition classes.
    """
    edge_list = []
    edge_cls_dict = {}
    for edge in structure.internal_edges.values():
        edge_output = {
            "ln_id": edge.ln_id,
            "timestamp": edge.timestamp,
            "head": edge.head,
            "tail": edge.tail,
            "label": edge.label,
            "bundle": str(edge.bundle),
        }
        if edge.condition:
            cls_name = edge.condition.__class__.__qualname__
            cond = json.dumps(
                {"class": cls_name, "args": edge.condition.model_dump()}
            )
            cls = edge.string_condition()
            if cls is not None and cls_name not in edge_cls_dict:
                edge_cls_dict.update({cls_name: cls})
        else:
            cond = None
        edge_output["condition"] = cond
        edge_list.append(edge_output)

    edge_cls_list = []
    for key, value in edge_cls_dict.items():
        edge_cls_list.append({"class_name": key, "class": value})

    return edge_list, edge_cls_list


class ParseNode:
    """
    Provides static methods for converting code strings to functional definitions, classes, and for parsing various types of structured nodes based on dictionary definitions.

    This utility class facilitates the dynamic execution of code and the instantiation of objects from serialized data.
    """

    @staticmethod
    def convert_to_def(function_code):
        """
        Converts a string containing a function definition into a callable function object.

        Args:
            function_code (str): The string code of the function to convert.

        Returns:
            function: The converted function as a callable.

        Raises:
            ValueError: If the function code is invalid or the function name cannot be detected.
        """
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
        """
        Converts a string containing a class definition into a class object.

        Args:
            cls_code (str): The string code of the class to convert.

        Returns:
            class: The converted class.

        Raises:
            ValueError: If the class code is invalid or the class name cannot be detected.
        """
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
        """
        Parses dictionary information into a System node object.

        Args:
            info_dict (dict): A dictionary containing properties of a system node.

        Returns:
            System: An instantiated System node filled with properties from info_dict.
        """
        info_dict["system"] = json.loads(info_dict.pop("content"))[
            "system_info"
        ]
        node = System.from_obj(info_dict)
        return node

    @staticmethod
    def parse_instruction(info_dict):
        """
        Parses dictionary information into an Instruction node object.

        Args:
            info_dict (dict): A dictionary containing properties of an instruction node.

        Returns:
            Instruction: An instantiated Instruction node filled with properties from info_dict.
        """
        info_dict["instruction"] = json.loads(info_dict.pop("content"))[
            "instruction"
        ]
        node = Instruction.from_obj(info_dict)
        return node

    @staticmethod
    def parse_directiveSelection(info_dict):
        """
        Parses dictionary information into an DirectiveSelection node object.

        Args:
            info_dict (dict): A dictionary containing properties of an action selection node.

        Returns:
            ActionSelection: An instantiated ActionSelection node filled with properties from info_dict.
        """
        node = DirectiveSelection(ln_id=info_dict["ln_id"])
        node.directive = info_dict["directive"]
        if "directive_kwargs" in info_dict:
            if info_dict["directive_kwargs"]:
                node.directive_kwargs = json.loads(
                    info_dict["directive_kwargs"]
                )
        elif "directiveKwargs" in info_dict:
            if info_dict["directiveKwargs"]:
                node.directive_kwargs = json.loads(
                    info_dict["directiveKwargs"]
                )
        return node

    @staticmethod
    def parse_tool(info_dict):
        """
        Parses dictionary information into a Tool node object, converting associated function code into a callable.

        Args:
            info_dict (dict): A dictionary containing properties and function code for a tool node.

        Returns:
            Tool: An instantiated Tool node with the function converted from code.

        Raises:
            ValueError: If unsafe code is detected in the function definition.
        """
        func_code = info_dict["function"]
        if (
            "import os" in func_code
            or "__" in func_code
            or "import sys" in func_code
        ):
            raise ValueError(
                "Unsafe code detected in Tool function. Please double check or implement explicitly"
            )

        func = ParseNode.convert_to_def(func_code)
        tool = func_to_tool(
            func, ln_id=info_dict["ln_id"], timestamp=info_dict["timestamp"]
        )
        if func.__doc__:
            if re.search(r":param \w+:", func.__doc__):
                tool = func_to_tool(
                    func,
                    docstring_style="reST",
                    ln_id=info_dict["ln_id"],
                    timestamp=info_dict["timestamp"],
                )

        tool = tool[0]
        return tool

    @staticmethod
    def parse_condition(condition, cls_code):
        """
        Parses a condition dictionary and corresponding class code into a class instance representing the condition.

        Args:
            condition (dict): A dictionary containing the serialized form of the condition's arguments.
            cls_code (str): The class code to instantiate the condition class.

        Returns:
            An instance of the condition class filled with properties from the condition dictionary.

        Raises:
            ValueError: If the condition or class code is invalid.
        """
        args = condition["args"]
        cls = ParseNode.convert_to_class(cls_code)

        init_params = {}
        for key in inspect.signature(cls.__init__).parameters.keys():
            if key == "self":
                continue
            init_params[key] = args[key]
        return cls(**init_params)
