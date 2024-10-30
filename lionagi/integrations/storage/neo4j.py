from neo4j import AsyncGraphDatabase

from lionagi.integrations.storage.storage_util import (
    output_edge_list,
    output_node_list,
)


class Neo4j:
    """
    Manages interactions with a Neo4j graph database, facilitating the creation, retrieval, and management
    of graph nodes and relationships asynchronously.

    Provides methods to add various types of nodes and relationships, query the graph based on specific criteria,
    and enforce database constraints to ensure data integrity.

    Attributes:
        database (str): The name of the database to connect to.
        driver (neo4j.AsyncGraphDatabase.driver): The Neo4j driver for asynchronous database operations.
    """

    def __init__(self, uri, user, password, database):
        """
        Initializes the Neo4j database connection using provided credentials and database information.

        Args:
            uri (str): The URI for the Neo4j database.
            user (str): The username for database authentication.
            password (str): The password for database authentication.
            database (str): The name of the database to use.
        """
        self.database = database
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    # ---------------------to_neo4j---------------------------------
    @staticmethod
    async def add_structure_node(tx, node, name):
        """
        Asynchronously adds a structure node to the graph.

        Args:
            tx: The Neo4j transaction.
            node (dict): The properties of the node to be added, including 'ln_id' and 'timestamp'.
            name (str): The name of the structure, which is set on the node.
        """
        query = """
            MERGE (n:Structure:LionNode {ln_id:$ln_id})
            SET n.timestamp = $timestamp
            SET n.name = $name
            """
        await tx.run(
            query, ln_id=node["ln_id"], timestamp=node["timestamp"], name=name
        )
        # heads=node['head_nodes'],
        # nodes=node['nodes'],
        # edges=node['edges'])

    @staticmethod
    async def add_system_node(tx, node):
        """
        Asynchronously adds a system node to the graph.

        Args:
            tx: The Neo4j transaction.
            node (dict): The properties of the system node including 'ln_id', 'timestamp', 'content', 'sender', and 'recipient'.
        """
        query = """
            MERGE (n:System:LionNode {ln_id: $ln_id})
            SET n.timestamp = $timestamp
            SET n.content = $content
            """
        await tx.run(
            query,
            ln_id=node["ln_id"],
            timestamp=node["timestamp"],
            content=node["content"],
        )

    @staticmethod
    async def add_instruction_node(tx, node):
        """
        Asynchronously adds an instruction node to the graph.

        Args:
            tx: The Neo4j transaction.
            node (dict): The properties of the instruction node including 'ln_id', 'timestamp', 'content', 'sender', and 'recipient'.
        """
        query = """
            MERGE (n:Instruction:LionNode {ln_id: $ln_id})
            SET n.timestamp = $timestamp
            SET n.content = $content
            """
        await tx.run(
            query,
            ln_id=node["ln_id"],
            timestamp=node["timestamp"],
            content=node["content"],
        )

    # TODO: tool.manual
    @staticmethod
    async def add_tool_node(tx, node):
        """
        Asynchronously adds a tool node to the graph.

        Args:
            tx: The Neo4j transaction.
            node (dict): The properties of the tool node including 'ln_id', 'timestamp', 'function', and 'parser'.
        """
        query = """
            MERGE (n:Tool:LionNode {ln_id: $ln_id})
            SET n.timestamp = $timestamp
            SET n.function = $function
            SET n.parser = $parser
            """
        await tx.run(
            query,
            ln_id=node["ln_id"],
            timestamp=node["timestamp"],
            function=node["function"],
            parser=node["parser"],
        )

    @staticmethod
    async def add_directiveSelection_node(tx, node):
        """
        Asynchronously adds an directive selection node to the graph.

        Args:
            tx: The Neo4j transaction.
            node (dict): The properties of the directive selection node including 'ln_id', 'directive', and 'directiveKwargs'.
        """
        query = """
            MERGE (n:DirectiveSelection:LionNode {ln_id: $ln_id})
            SET n.directive = $directive
            SET n.directiveKwargs = $directiveKwargs
            """
        await tx.run(
            query,
            ln_id=node["ln_id"],
            directive=node["directive"],
            directiveKwargs=node["directive_kwargs"],
        )

    @staticmethod
    async def add_baseAgent_node(tx, node):
        """
        Asynchronously adds an agent node to the graph.

        Args:
            tx: The Neo4j transaction.
            node (dict): The properties of the agent node including 'ln_id', 'timestamp', 'structureId', and 'outputParser'.
        """
        query = """
            MERGE (n:Agent:LionNode {ln_id:$ln_id})
            SET n.timestamp = $timestamp
            SET n.structureId = $structureId
            SET n.outputParser = $outputParser
            """
        await tx.run(
            query,
            ln_id=node["ln_id"],
            timestamp=node["timestamp"],
            structureId=node["structure_id"],
            outputParser=node["output_parser"],
        )

    @staticmethod
    async def add_forward_edge(tx, edge):
        """
        Asynchronously adds a forward relationship between two nodes in the graph.

        Args:
            tx: The Neo4j transaction.
            edge (dict): The properties of the edge including 'ln_id', 'timestamp', 'head', 'tail', 'label', and 'condition'.
        """
        query = """
            MATCH (m:LionNode) WHERE m.ln_id = $head
            MATCH (n:LionNode) WHERE n.ln_id = $tail
            MERGE (m)-[r:FORWARD]->(n)
            SET r.ln_id = $ln_id
            SET r.timestamp = $timestamp
            SET r.label = $label
            SET r.condition = $condition
            """
        await tx.run(
            query,
            ln_id=edge["ln_id"],
            timestamp=edge["timestamp"],
            head=edge["head"],
            tail=edge["tail"],
            label=edge["label"],
            condition=edge["condition"],
        )

    @staticmethod
    async def add_bundle_edge(tx, edge):
        """
        Asynchronously adds a bundle relationship between two nodes in the graph.

        Args:
            tx: The Neo4j transaction.
            edge (dict): The properties of the edge including 'ln_id', 'timestamp', 'head', 'tail', 'label', and 'condition'.
        """
        query = """
            MATCH (m:LionNode) WHERE m.ln_id = $head
            MATCH (n:LionNode) WHERE n.ln_id = $tail
            MERGE (m)-[r:BUNDLE]->(n)
            SET r.ln_id = $ln_id
            SET r.timestamp = $timestamp
            SET r.label = $label
            SET r.condition = $condition
            """
        await tx.run(
            query,
            ln_id=edge["ln_id"],
            timestamp=edge["timestamp"],
            head=edge["head"],
            tail=edge["tail"],
            label=edge["label"],
            condition=edge["condition"],
        )

    @staticmethod
    async def add_head_edge(tx, structure):
        """
        Asynchronously adds head relationships from a structure node to its head nodes.

        Args:
            tx: The Neo4j transaction.
            structure: The structure node from which head relationships are established.
        """
        for head in structure.get_heads():
            head_id = head.ln_id
            query = """
                MATCH (m:Structure) WHERE m.ln_id = $structureId
                MATCH (n:LionNode) WHERE n.ln_id = $headId
                MERGE (m)-[:HEAD]->(n)
                """
            await tx.run(query, structureId=structure.ln_id, headId=head_id)

    @staticmethod
    async def add_single_condition_cls(tx, condCls):
        """
        Asynchronously adds a condition class node to the graph.

        Args:
            tx: The Neo4j transaction.
            condCls (dict): The properties of the condition class node including 'className' and 'code'.
        """
        query = """
            MERGE (n:EdgeCondition:LionNode {className: $className})
            SET n.code = $code
            """
        await tx.run(
            query, className=condCls["class_name"], code=condCls["class"]
        )

    async def add_node(self, tx, node_dict, structure_name):
        """
        Asynchronously adds various types of nodes to the Neo4j graph based on the provided dictionary of node lists.

        This method iterates through a dictionary where each key is a node type and each value is a list of nodes.
        It adds each node to the graph according to its type.

        Args:
            tx: The Neo4j transaction.
            node_dict (dict): A dictionary where keys are node type strings and values are lists of node properties dictionaries.
            structure_name (str): The name of the structure to which these nodes belong, used specifically for 'StructureExecutor' nodes.

        Raises:
            ValueError: If an unsupported node type is detected in the dictionary.
        """
        for node in node_dict:
            node_list = node_dict[node]
            if node == "GraphExecutor":
                [
                    await self.add_structure_node(tx, i, structure_name)
                    for i in node_list
                ]
            elif node == "System":
                [await self.add_system_node(tx, i) for i in node_list]
            elif node == "Instruction":
                [await self.add_instruction_node(tx, i) for i in node_list]
            elif node == "Tool":
                [await self.add_tool_node(tx, i) for i in node_list]
            elif node == "DirectiveSelection":
                [
                    await self.add_directiveSelection_node(tx, i)
                    for i in node_list
                ]
            elif node == "BaseAgent":
                [await self.add_baseAgent_node(tx, i) for i in node_list]
            else:
                raise ValueError("Not supported node type detected")

    async def add_edge(self, tx, edge_list):
        """
        Asynchronously adds edges to the Neo4j graph based on a list of edge properties.

        This method processes a list of edges, each represented by a dictionary of properties, and creates either
        'BUNDLE' or 'FORWARD' relationships in the graph based on the 'bundle' property of each edge.

        Args:
            tx: The Neo4j transaction.
            edge_list (list[dict]): A list of dictionaries where each dictionary contains properties of an edge including
                its type, identifiers of the head and tail nodes, and additional attributes like label and condition.

        Raises:
            ValueError: If an edge dictionary is missing required properties or contains invalid values.
        """
        for edge in edge_list:
            if edge["bundle"] == "True":
                await self.add_bundle_edge(tx, edge)
            else:
                await self.add_forward_edge(tx, edge)

    async def add_condition_cls(self, tx, edge_cls_list):
        """
        Asynchronously adds condition class nodes to the Neo4j graph.

        This method iterates over a list of condition class definitions and adds each as a node in the graph.
        Each condition class is typically used to define logic or conditions within the graph structure.

        Args:
            tx: The Neo4j transaction.
            edge_cls_list (list[dict]): A list of dictionaries where each dictionary represents the properties of a
                condition class, including the class name and its corresponding code.

        Raises:
            ValueError: If any condition class dictionary is missing required properties or the properties do not adhere
                to expected formats.
        """
        for cls in edge_cls_list:
            await self.add_single_condition_cls(tx, cls)

    @staticmethod
    async def check_id_constraint(tx):
        """
        Asynchronously applies a unique constraint on the 'ln_id' attribute for all nodes of type 'LionNode' in the graph.

        This constraint ensures that each node in the graph has a unique identifier.

        Args:
            tx: The Neo4j transaction.
        """
        query = """
            CREATE CONSTRAINT node_id IF NOT EXISTS
            FOR (n:LionNode) REQUIRE (n.ln_id) IS UNIQUE
            """
        await tx.run(query)

    @staticmethod
    async def check_structure_name_constraint(tx):
        """
        Asynchronously applies a unique constraint on the 'name' attribute for all nodes of type 'Structure' in the graph.

        This constraint ensures that each structure in the graph can be uniquely identified by its name.

        Args:
            tx: The Neo4j transaction.
        """
        query = """
            CREATE CONSTRAINT structure_name IF NOT EXISTS
            FOR (n:Structure) REQUIRE (n.name) IS UNIQUE
            """
        await tx.run(query)

    async def store(self, structure, structure_name):
        """
        Asynchronously stores a structure and its components in the Neo4j graph.

        This method orchestrates the storage of nodes, edges, and other related elements that make up a structure,
        ensuring all elements are added transactionally.

        Args:
            structure: The structure object containing the nodes and edges to be stored.
            structure_name (str): The name of the structure, used to uniquely identify it in the graph.

        Raises:
            ValueError: If the transaction fails due to an exception, indicating an issue with the data or constraints.
        """
        node_list, node_dict = output_node_list(structure)
        edge_list, edge_cls_list = output_edge_list(structure)

        async with self.driver as driver:
            async with driver.session(database=self.database) as session:
                # constraint
                tx = await session.begin_transaction()
                try:
                    await self.check_id_constraint(tx)
                    await self.check_structure_name_constraint(tx)
                    await tx.commit()
                except Exception as e:
                    raise ValueError(
                        f"transaction rolled back due to exception: {e}"
                    )
                finally:
                    await tx.close()

                # query
                tx = await session.begin_transaction()
                try:
                    await self.add_node(tx, node_dict, structure_name)
                    await self.add_edge(tx, edge_list)
                    await self.add_condition_cls(tx, edge_cls_list)
                    await self.add_head_edge(tx, structure)
                    await tx.commit()
                except Exception as e:
                    raise ValueError(
                        f"transaction rolled back due to exception: {e}"
                    )
                finally:
                    await tx.close()

    # ---------------------frpm_neo4j---------------------------------
    @staticmethod
    async def match_node(tx, node_id):
        """
        Asynchronously retrieves a node from the graph based on its identifier.

        Args:
            tx: The Neo4j transaction.
            node_id (str): The unique identifier of the node to retrieve.

        Returns:
            A dictionary containing the properties of the node if found, otherwise None.
        """
        query = """
            MATCH (n:LionNode) WHERE n.ln_id = $ln_id
            RETURN labels(n), n{.*}
            """
        result = await tx.run(query, ln_id=node_id)
        result = [record.values() async for record in result]
        if result:
            return result[0]
        else:
            return None

    @staticmethod
    async def match_structure_id(tx, name):
        """
        Asynchronously retrieves the identifier of a structure based on its name.

        Args:
            tx: The Neo4j transaction.
            name (str): The name of the structure to retrieve the identifier for.

        Returns:
            A list containing the identifier(s) of the matching structure(s).
        """
        query = """
            MATCH (n:Structure) WHERE n.name = $name
            RETURN n.ln_id
            """
        result = await tx.run(query, name=name)
        result = [record.values() async for record in result]
        result = sum(result, [])
        return result

    @staticmethod
    async def head(tx, node_id):
        """
        Asynchronously retrieves the head nodes associated with a structure node in the graph.

        Args:
            tx: The Neo4j transaction.
            node_id (str): The identifier of the structure node whose head nodes are to be retrieved.

        Returns:
            A list of dictionaries representing the properties and labels of each head node connected to the structure.
        """
        query = """
            MATCH (n:Structure)-[r:HEAD]->(m) WHERE n.ln_id = $nodeId
            RETURN r{.*}, labels(m), m{.*}
            """
        result = await tx.run(query, nodeId=node_id)
        result = [record.values() async for record in result]
        return result

    @staticmethod
    async def forward(tx, node_id):
        """
        Asynchronously retrieves all forward relationships and their target nodes for a given node.

        Args:
            tx: The Neo4j transaction.
            node_id (str): The identifier of the node from which to retrieve forward relationships.

        Returns:
            A list of dictionaries representing the properties and labels of each node connected by a forward relationship.
        """
        query = """
            MATCH (n:LionNode)-[r:FORWARD]->(m) WHERE n.ln_id = $nodeId
            RETURN r{.*}, labels(m), m{.*}
            """
        result = await tx.run(query, nodeId=node_id)
        result = [record.values() async for record in result]
        return result

    @staticmethod
    async def bundle(tx, node_id):
        """
        Asynchronously retrieves all bundle relationships and their target nodes for a given node.

        Args:
            tx: The Neo4j transaction.
            node_id (str): The identifier of the node from which to retrieve bundle relationships.

        Returns:
            A list of dictionaries representing the properties and labels of each node connected by a bundle relationship.
        """
        query = """
            MATCH (n:LionNode)-[r:BUNDLE]->(m) WHERE n.ln_id = $nodeId
            RETURN labels(m), m{.*}
            """
        result = await tx.run(query, nodeId=node_id)
        result = [record.values() async for record in result]
        return result

    @staticmethod
    async def match_condition_class(tx, name):
        """
        Asynchronously retrieves the code for a condition class based on its class name.

        Args:
            tx: The Neo4j transaction.
            name (str): The class name of the condition to retrieve the code for.

        Returns:
            The code of the condition class if found, otherwise None.
        """
        query = """
            MATCH (n:EdgeCondition) WHERE n.className = $name
            RETURN n.code
            """
        result = await tx.run(query, name=name)
        result = [record.values() async for record in result]
        if result:
            return result[0][0]
        else:
            return None

    async def locate_structure(
        self, tx, structure_name: str = None, structure_id: str = None
    ):
        """
        Asynchronously locates a structure by its name or ID in the Neo4j graph.

        This method is designed to find a structure either by its name or by a specific identifier,
        returning the identifier if found.

        Args:
            tx: The Neo4j transaction.
            structure_name (str, optional): The name of the structure to locate.
            structure_id (str, optional): The unique identifier of the structure to locate.

        Returns:
            str: The identifier of the located structure.

        Raises:
            ValueError: If neither structure name nor ID is provided, or if the provided name or ID does not correspond
                to any existing structure.
        """
        if not structure_name and not structure_id:
            raise ValueError("Please provide the structure name or ln_id")
        if structure_name:
            id = await self.match_structure_id(tx, structure_name)
            if not id:
                raise ValueError(f"Structure: {structure_name} is not found")
            elif structure_id is not None and structure_id not in id:
                raise ValueError(
                    f"{structure_name} and id {structure_id} does not match"
                )
            return id[0]
        else:
            result = await self.match_node(tx, structure_id)
            if result:
                return structure_id
            else:
                raise ValueError(f"Structure id {structure_id} is invalid")

    async def get_heads(
        self, structure_name: str = None, structure_id: str = None
    ):
        """
        Asynchronously retrieves the head nodes associated with a given structure in the graph.

        Args:
            structure_name (str, optional): The name of the structure whose head nodes are to be retrieved.
            structure_id (str, optional): The identifier of the structure whose head nodes are to be retrieved.

        Returns:
            tuple: A tuple containing the structure identifier and a list of dictionaries, each representing a head node
                connected to the structure.

        Raises:
            ValueError: If both structure name and ID are not provided, or if the specified structure cannot be found.
        """
        async with self.driver as driver:
            async with driver.session(database=self.database) as session:
                id = await session.execute_read(
                    self.locate_structure, structure_name, structure_id
                )
                result = await session.execute_read(self.head, id)
                return id, result

    async def get_bundle(self, node_id):
        """
        Asynchronously retrieves all nodes connected by a bundle relationship to a given node in the graph.

        Args:
            node_id (str): The identifier of the node from which bundle relationships are to be retrieved.

        Returns:
            list: A list of dictionaries representing each node connected by a bundle relationship from the specified node.
        """
        async with self.driver as driver:
            async with driver.session(database=self.database) as session:
                result = await session.execute_read(self.bundle, node_id)
                return result

    async def get_forwards(self, node_id):
        """
        Asynchronously retrieves all nodes connected by forward relationships to a given node in the graph.

        Args:
            node_id (str): The identifier of the node from which forward relationships are to be retrieved.

        Returns:
            list: A list of dictionaries representing each node connected by a forward relationship from the specified node.
        """
        async with self.driver as driver:
            async with driver.session(database=self.database) as session:
                result = await session.execute_read(self.forward, node_id)
                return result

    async def get_condition_cls_code(self, class_name):
        """
        Asynchronously retrieves the code associated with a specified condition class from the Neo4j graph.

        This method queries the graph to find the code that defines the behavior or logic of a condition class by its name.

        Args:
            class_name (str): The name of the condition class whose code is to be retrieved.

        Returns:
            str: The code of the condition class if found, or None if the class does not exist in the graph.

        Raises:
            ValueError: If the class_name is not provided or if the query fails due to incorrect syntax or database issues.
        """
        async with self.driver as driver:
            async with driver.session(database=self.database) as session:
                result = await session.execute_read(
                    self.match_condition_class, class_name
                )
                return result

    async def node_exist(self, node_id):
        """
        Asynchronously checks if a node with the specified identifier exists in the Neo4j graph.

        This method is useful for validation checks before attempting operations that assume the existence of a node.

        Args:
            node_id (str): The unique identifier of the node to check for existence.

        Returns:
            bool: True if the node exists in the graph, False otherwise.

        Raises:
            ValueError: If the node_id is not provided or if the query fails due to incorrect syntax or database issues.
        """
        async with self.driver as driver:
            async with driver.session(database=self.database) as session:
                result = await session.execute_read(self.match_node, node_id)
                if result:
                    return True
                else:
                    return False
