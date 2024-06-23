import styles from './PromptNode.module.css'


import React, { useCallback } from 'react';
import { Handle, Position } from 'reactflow';
import { Card, Input, Label} from 'reactstrap'

function PromptNode() {
  const onChange = useCallback((evt) => {
    console.log(evt.target.value);
  }, []);

  return (
    <div className={styles.PromptNode}>
      <Card className={'mb-1'}>
        <Label>Prompt</Label>
        <Input id="text" type={'textarea'} name="text" bsSize="sm" rows={5} onChange={onChange} className={"nodrag nowheel"}/>
      </Card>
      <Handle type="target" position={Position.Right} id="PromptRight" isValidConnection={(connection) => connection.sourceHandle === "AgentLeft"}/>
    </div>
  );
}

export default PromptNode;
