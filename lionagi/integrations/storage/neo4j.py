from neo4j import AsyncGraphDatabase

from lionagi.integrations.storage.storage_util import output_node_list, output_edge_list


class Neo4j:

    def __init__(self, uri, user, password, database):
        self.database = database
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    #---------------------to_neo4j---------------------------------
    @staticmethod
    async def add_structure_node(tx, node, name):
        query = """
            MERGE (n:Structure:LionNode {id:$id})
            SET n.timestamp = $timestamp
            SET n.name = $name
            """
        await tx.run(query,
                     id=node['id'],
                     timestamp=node['timestamp'],
                     name=name)
                     # heads=node['head_nodes'],
                     # nodes=node['nodes'],
                     # edges=node['edges'])

    @staticmethod
    async def add_system_node(tx, node):
        query = """
            MERGE (n:System:LionNode {id: $id})
            SET n.timestamp = $timestamp
            SET n.content = $content
            SET n.sender = $sender
            SET n.recipient = $recipient
            """
        await tx.run(query,
                     id=node['id'],
                     timestamp=node['timestamp'],
                     content=node['content'],
                     sender=node['sender'],
                     recipient=node['recipient'])

    @staticmethod
    async def add_instruction_node(tx, node):
        query = """
            MERGE (n:Instruction:LionNode {id: $id})
            SET n.timestamp = $timestamp
            SET n.content = $content
            SET n.sender = $sender
            SET n.recipient = $recipient
            """
        await tx.run(query,
                     id=node['id'],
                     timestamp=node['timestamp'],
                     content=node['content'],
                     sender=node['sender'],
                     recipient=node['recipient'])

    # TODO: tool.manual
    @staticmethod
    async def add_tool_node(tx, node):
        query = """
            MERGE (n:Tool:LionNode {id: $id})
            SET n.timestamp = $timestamp
            SET n.function = $function
            SET n.parser = $parser
            """
        await tx.run(query,
                     id=node['id'],
                     timestamp=node['timestamp'],
                     function=node['function'],
                     parser=node['parser'])

    @staticmethod
    async def add_actionSelection_node(tx, node):
        query = """
            MERGE (n:ActionSelection:LionNode {id: $id})
            SET n.action = $action
            SET n.actionKwargs = $actionKwargs
            """
        await tx.run(query,
                     id=node['id'],
                     action=node['action'],
                     actionKwargs=node['action_kwargs'])

    @staticmethod
    async def add_baseAgent_node(tx, node):
        query = """
            MERGE (n:Agent:LionNode {id:$id})
            SET n.timestamp = $timestamp
            SET n.structureId = $structureId
            SET n.outputParser = $outputParser
            """
        await tx.run(query,
                     id=node['id'],
                     timestamp=node['timestamp'],
                     structureId=node['structure_id'],
                     outputParser=node['output_parser'])

    @staticmethod
    async def add_forward_edge(tx, edge):
        query = """
            MATCH (m:LionNode) WHERE m.id = $head
            MATCH (n:LionNode) WHERE n.id = $tail
            MERGE (m)-[r:FORWARD]->(n)
            SET r.id = $id
            SET r.timestamp = $timestamp
            SET r.label = $label
            SET r.condition = $condition
            """
        await tx.run(query,
                     id=edge['id'],
                     timestamp=edge['timestamp'],
                     head=edge['head'],
                     tail=edge['tail'],
                     label=edge['label'],
                     condition=edge['condition'])

    @staticmethod
    async def add_bundle_edge(tx, edge):
        query = """
            MATCH (m:LionNode) WHERE m.id = $head
            MATCH (n:LionNode) WHERE n.id = $tail
            MERGE (m)-[r:BUNDLE]->(n)
            SET r.id = $id
            SET r.timestamp = $timestamp
            SET r.label = $label
            SET r.condition = $condition
            """
        await tx.run(query,
                     id=edge['id'],
                     timestamp=edge['timestamp'],
                     head=edge['head'],
                     tail=edge['tail'],
                     label=edge['label'],
                     condition=edge['condition'])

    @staticmethod
    async def add_head_edge(tx, structure):
        for head in structure.get_heads():
            head_id = head.id_
            query = """
                MATCH (m:Structure) WHERE m.id = $structureId
                MATCH (n:LionNode) WHERE n.id = $headId
                MERGE (m)-[:HEAD]->(n)
                """
            await tx.run(query,
                         structureId=structure.id_,
                         headId=head_id)

    @staticmethod
    async def add_single_condition_cls(tx, condCls):
        query = """
            MERGE (n:Condition:LionNode {className: $className})
            SET n.code = $code
            """
        await tx.run(query,
                     className=condCls['class_name'],
                     code=condCls['class'])

    async def add_node(self, tx, node_dict, structure_name):
        for node in node_dict:
            node_list = node_dict[node]
            if node == 'StructureExecutor':
                [await self.add_structure_node(tx, i, structure_name) for i in node_list]
            elif node == 'System':
                [await self.add_system_node(tx, i) for i in node_list]
            elif node == 'Instruction':
                [await self.add_instruction_node(tx, i) for i in node_list]
            elif node == 'Tool':
                [await self.add_tool_node(tx, i) for i in node_list]
            elif node == 'ActionSelection':
                [await self.add_actionSelection_node(tx, i) for i in node_list]
            elif node == 'BaseAgent':
                [await self.add_baseAgent_node(tx, i) for i in node_list]
            else:
                raise ValueError('Not supported node type detected')

    async def add_edge(self, tx, edge_list):
        for edge in edge_list:
            if edge['bundle'] == 'True':
                await self.add_bundle_edge(tx, edge)
            else:
                await self.add_forward_edge(tx, edge)

    async def add_condition_cls(self, tx, edge_cls_list):
        for cls in edge_cls_list:
            await self.add_single_condition_cls(tx, cls)

    @staticmethod
    async def check_id_constraint(tx):
        query = """
            CREATE CONSTRAINT node_id IF NOT EXISTS
            FOR (n:LionNode) REQUIRE (n.id) IS UNIQUE
            """
        await tx.run(query)

    @staticmethod
    async def check_structure_name_constraint(tx):
        query = """
            CREATE CONSTRAINT structure_name IF NOT EXISTS
            FOR (n:Structure) REQUIRE (n.name) IS UNIQUE
            """
        await tx.run(query)

    async def store(self, structure, structure_name):
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
                    raise ValueError(f"transaction rolled back due to exception: {e}")
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
                    raise ValueError(f"transaction rolled back due to exception: {e}")
                finally:
                    await tx.close()

    #---------------------frpm_neo4j---------------------------------
    @staticmethod
    async def match_node(tx, node_id):
        query = """
            MATCH (n:LionNode) WHERE n.id = $id
            RETURN labels(n), n{.*}
            """
        result = await tx.run(query,
                              id=node_id)
        result = [record.values() async for record in result]
        if result:
            return result[0]
        else:
            return None

    @staticmethod
    async def match_structure_id(tx, name):
        query = """
            MATCH (n:Structure) WHERE n.name = $name
            RETURN n.id
            """
        result = await tx.run(query,
                              name=name)
        result = [record.values() async for record in result]
        result = sum(result, [])
        return result

    @staticmethod
    async def head(tx, node_id):
        query = """
            MATCH (n:Structure)-[r:HEAD]->(m) WHERE n.id = $nodeId
            RETURN r{.*}, labels(m), m{.*}
            """
        result = await tx.run(query,
                              nodeId=node_id)
        result = [record.values() async for record in result]
        return result

    @staticmethod
    async def forward(tx, node_id):
        query = """
            MATCH (n:LionNode)-[r:FORWARD]->(m) WHERE n.id = $nodeId
            RETURN r{.*}, labels(m), m{.*}
            """
        result = await tx.run(query,
                              nodeId=node_id)
        result = [record.values() async for record in result]
        return result

    @staticmethod
    async def bundle(tx, node_id):
        query = """
            MATCH (n:LionNode)-[r:BUNDLE]->(m) WHERE n.id = $nodeId
            RETURN labels(m), m{.*}
            """
        result = await tx.run(query,
                              nodeId=node_id)
        result = [record.values() async for record in result]
        return result

    @staticmethod
    async def match_condition_class(tx, name):
        query = """
            MATCH (n:Condition) WHERE n.className = $name
            RETURN n.code
            """
        result = await tx.run(query,
                              name=name)
        result = [record.values() async for record in result]
        if result:
            return result[0][0]
        else:
            return None

    async def locate_structure(self, tx, structure_name: str = None, structure_id: str = None):
        if not structure_name and not structure_id:
            raise ValueError("Please provide the structure name or id")
        if structure_name:
            id = await self.match_structure_id(tx, structure_name)
            if not id:
                raise ValueError(f"Structure: {structure_name} is not found")
            elif structure_id is not None and structure_id not in id:
                raise ValueError(f"{structure_name} and id {structure_id} does not match")
            return id[0]
        else:
            result = await self.match_node(tx, structure_id)
            if result:
                return structure_id
            else:
                raise ValueError(f"Structure id {structure_id} is invalid")

    async def get_heads(self, structure_name: str = None, structure_id: str = None):
        async with self.driver as driver:
            async with driver.session(database=self.database) as session:
                id = await session.execute_read(self.locate_structure, structure_name, structure_id)
                result = await session.execute_read(self.head, id)
                return id, result

    async def get_bundle(self, node_id):
        async with self.driver as driver:
            async with driver.session(database=self.database) as session:
                result = await session.execute_read(self.bundle, node_id)
                return result

    async def get_forwards(self, node_id):
        async with self.driver as driver:
            async with driver.session(database=self.database) as session:
                result = await session.execute_read(self.forward, node_id)
                return result

    async def get_condition_cls_code(self, class_name):
        async with self.driver as driver:
            async with driver.session(database=self.database) as session:
                result = await session.execute_read(self.match_condition_class, class_name)
                return result

    async def node_exist(self, node_id):
        async with self.driver as driver:
            async with driver.session(database=self.database) as session:
                result = await session.execute_read(self.match_node, node_id)
                if result:
                    return True
                else:
                    return False