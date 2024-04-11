import { useState, useCallback, useRef } from 'react';
import ReactFlow, {
  addEdge,
  Controls,
  Background,
  applyNodeChanges,
  applyEdgeChanges,
  MiniMap,
  ReactFlowProvider,
  useReactFlow,
  getOutgoers,
} from 'reactflow';
import 'reactflow/dist/style.css';

import PromptNode from '../components/PromptNode';
import ToolNode from '../components/ToolNode'
import Sidebar from '../components/sidebar';
import AgentNode from '../components/AgentNode';

const nodeTypes = { 
  Agent: AgentNode,
  Prompt: PromptNode,
  Tool: ToolNode
};

let id = 0;
const getId = () => `dndnode_${id++}`;

function Flow() {
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);

  const { getNodes, getEdges } = useReactFlow();

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [],
  );
  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [],
  );

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [],
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');

      // check if the dropped element is valid
      if (typeof type === 'undefined' || !type) {
        return;
      }
      // reactFlowInstance.project was renamed to reactFlowInstance.screenToFlowPosition
      // and you don't need to subtract the reactFlowBounds.left/top anymore
      // details: https://reactflow.dev/whats-new/2023-11-10
      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });
      const newNode = {
        id: getId(),
        type,
        position,
        data: { label: `${type} node` },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance],
  );

  const isValidConnection = useCallback(
    (connection) => {
      // we are using getNodes and getEdges helpers here
      // to make sure we create isValidConnection function only once
      const nodes = getNodes();
      const edges = getEdges();
      const target = nodes.find((node) => node.id === connection.target);
      const hasCycle = (node, visited = new Set()) => {
        if (visited.has(node.id)) return false;

        visited.add(node.id);

        for (const outgoer of getOutgoers(node, nodes, edges)) {
          if (outgoer.id === connection.source) return true;
          if (hasCycle(outgoer, visited)) return true;
        }
      };

      if (target.id === connection.source) return false;
      return !hasCycle(target);
    },
    [getNodes, getEdges],
  );

  return (
          <ReactFlow
            nodes={nodes}
            onNodesChange={onNodesChange}
            edges={edges}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            isValidConnection={isValidConnection}
            // fitView
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
  );
}

export default () => (
  <div>
    <ReactFlowProvider>
      <div style={{ height: '80vh' }}>
        <Flow />
      </div>
      <Sidebar />
    </ReactFlowProvider>
  </div>
);







































































// import { useState, useCallback, useRef} from 'react';
// import ReactFlow, {
//   useNodesState, 
//   useEdgesState, 
//   Controls,
//   Background,
//   applyNodeChanges,
//   applyEdgeChanges,
//   addEdge,
//   ReactFlowProvider,
// } from 'reactflow';

// import {Label, Row, Col, Card, CardTitle} from 'reactstrap'
// import 'reactflow/dist/style.css';

// import styles from '../styles/Home.module.css'

// import Sidebar from '../components/Sidebar'


// let id = 0;
// const getId = () => `dndnode_${id++}`;

// const styling = {
//   background: 'red',
//   width: '100%'
// };




// const DnDFlow = () => {
//   const reactFlowWrapper = useRef(null);
//   const [nodes, setNodes, onNodesChange] = useNodesState([]);
//   const [edges, setEdges, onEdgesChange] = useEdgesState([]);
//   const [reactFlowInstance, setReactFlowInstance] = useState(null);

//   const onConnect = useCallback(
//     (params) => setEdges((eds) => addEdge(params, eds)),
//     [],
//   );

//   const onDragOver = useCallback((event) => {
//     event.preventDefault();
//     event.dataTransfer.dropEffect = 'move';
//   }, []);

//   const onDrop = useCallback(
//     (event) => {
//       event.preventDefault();

//       const type = event.dataTransfer.getData('application/reactflow');

//       // check if the dropped element is valid
//       if (typeof type === 'undefined' || !type) {
//         return;
//       }

//       // reactFlowInstance.project was renamed to reactFlowInstance.screenToFlowPosition
//       // and you don't need to subtract the reactFlowBounds.left/top anymore
//       // details: https://reactflow.dev/whats-new/2023-11-10
//       const position = reactFlowInstance.screenToFlowPosition({
//         x: event.clientX,
//         y: event.clientY,
//       });
//       const newNode = {
//         id: getId(),
//         type,
//         position,
//         data: { label: `${type} node` },
//       };

//       setNodes((nds) => nds.concat(newNode));
//     },
//     [reactFlowInstance],
//   );

//   return (
//     <div className="dndflow">
//       <ReactFlowProvider>
//         <div className="reactflow-wrapper" ref={reactFlowWrapper} style={{ height: '80vh', width: '100vw' }}>
//           <ReactFlow
//             nodes={nodes}
//             edges={edges}
//             onNodesChange={onNodesChange}
//             onEdgesChange={onEdgesChange}
//             onConnect={onConnect}
//             onInit={setReactFlowInstance}
//             onDrop={onDrop}
//             onDragOver={onDragOver}
//             fitView
//           >
//             <Background />
//             <Controls />
//           </ReactFlow>
//         </div>
//         <Sidebar className="styles.dndflow"/>
//       </ReactFlowProvider>
//     </div>
//   );
// };

// export default DnDFlow;






































// import Head from 'next/head';
// import styles from '../styles/Home.module.css';

// export default function Home() {
//   return (
//     <div className={styles.container}>
//       <Head>
//         <title>Create Next App</title>
//         <link rel="icon" href="/favicon.ico" />
//       </Head>

//       <main>
//         <h1 className={styles.title}>
//           Welcome to <a href="https://nextjs.org">Next.js!</a>
//         </h1>

//         <p className={styles.description}>
//           Get started by editing <code>pages/index.js</code>
//         </p>

//         <div className={styles.grid}>
//           <a href="https://nextjs.org/docs" className={styles.card}>
//             <h3>Documentation &rarr;</h3>
//             <p>Find in-depth information about Next.js features and API.</p>
//           </a>

//           <a href="https://nextjs.org/learn" className={styles.card}>
//             <h3>Learn &rarr;</h3>
//             <p>Learn about Next.js in an interactive course with quizzes!</p>
//           </a>

//           <a
//             href="https://github.com/vercel/next.js/tree/canary/examples"
//             className={styles.card}
//           >
//             <h3>Examples &rarr;</h3>
//             <p>Discover and deploy boilerplate example Next.js projects.</p>
//           </a>

//           <a
//             href="https://vercel.com/import?filter=next.js&utm_source=create-next-app&utm_medium=default-template&utm_campaign=create-next-app"
//             className={styles.card}
//           >
//             <h3>Deploy &rarr;</h3>
//             <p>
//               Instantly deploy your Next.js site to a public URL with Vercel.
//             </p>
//           </a>
//         </div>
//       </main>

//       <footer>
//         <a
//           href="https://vercel.com?utm_source=create-next-app&utm_medium=default-template&utm_campaign=create-next-app"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Powered by{' '}
//           <img src="/vercel.svg" alt="Vercel" className={styles.logo} />
//         </a>
//       </footer>

//       <style jsx>{`
//         main {
//           padding: 5rem 0;
//           flex: 1;
//           display: flex;
//           flex-direction: column;
//           justify-content: center;
//           align-items: center;
//         }
//         footer {
//           width: 100%;
//           height: 100px;
//           border-top: 1px solid #eaeaea;
//           display: flex;
//           justify-content: center;
//           align-items: center;
//         }
//         footer img {
//           margin-left: 0.5rem;
//         }
//         footer a {
//           display: flex;
//           justify-content: center;
//           align-items: center;
//           text-decoration: none;
//           color: inherit;
//         }
//         code {
//           background: #fafafa;
//           border-radius: 5px;
//           padding: 0.75rem;
//           font-size: 1.1rem;
//           font-family:
//             Menlo,
//             Monaco,
//             Lucida Console,
//             Liberation Mono,
//             DejaVu Sans Mono,
//             Bitstream Vera Sans Mono,
//             Courier New,
//             monospace;
//         }
//       `}</style>

//       <style jsx global>{`
//         html,
//         body {
//           padding: 0;
//           margin: 0;
//           font-family:
//             -apple-system,
//             BlinkMacSystemFont,
//             Segoe UI,
//             Roboto,
//             Oxygen,
//             Ubuntu,
//             Cantarell,
//             Fira Sans,
//             Droid Sans,
//             Helvetica Neue,
//             sans-serif;
//         }
//         * {
//           box-sizing: border-box;
//         }
//       `}</style>
//     </div>
//   );
// }
