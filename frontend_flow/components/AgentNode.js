import { Card, Label } from 'reactstrap';
import { Handle, Position } from 'reactflow';

import styles from './AgentNode.module.css'

function AgentNode() {
    return (
      <div className={styles.AgentNode}>
        <Handle type="target" position={Position.Top} id="AgentTop" />
        <Card className={'mb-1'}>
          <Label>Agent</Label>
        </Card>
        <Handle type="source" position={Position.Bottom} id="AgentBottom" />
        <Handle type="source" position={Position.Left} id="AgentLeft" isValidConnection={(connection) => connection.targetHandle === "PromptRight"}/>
        <Handle type="source" position={Position.Right} id="AgentRight" isValidConnection={(connection) => connection.targetHandle === "ToolLeft"}/>
      </div>
    );
  }
  
  export default AgentNode;