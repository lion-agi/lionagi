import { Card, Label, Input } from 'reactstrap';
import styles from './ToolNode.module.css'

import { Handle, useReactFlow, useStoreApi, Position } from 'reactflow';

const options = [
    {   
        value: 'tool1',
        label: 'Tool 1',
    },
    {
        value: 'tool2',
        label: 'Tool 2',
    },
    {
        value: 'tool3',
        label: 'Tool 3',
    }
];

function ToolNode() {
    return (
        <div className={styles.ToolNode}>
            <Card className='mb-1'>
                <Label>Tool</Label>
                <Input id='select' name='select' type='select' bsSize="sm" className={"nodrag nowheel"}>
                    {options.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </Input>
            </Card>
          <Handle type="target" position={Position.Left} id="ToolLeft" isValidConnection={(connection) => connection.sourceHandle === 'AgentRight'}/>
        </div>
      );
    }

export default ToolNode;