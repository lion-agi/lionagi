import React from 'react';

import { Card, CardText, CardTitle, Container, Row, Col } from 'reactstrap';

import 'bootstrap/dist/css/bootstrap.min.css';

export default () => {
  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside>
      <Container className='mt-2'>
        <Card>
          <Row>
            <CardTitle className='text-center'>Options</CardTitle>
          </Row>
          <Row className='mb-2'>
            <Col>
              <Card className="text-center" color='warning' outline>
                <CardText onDragStart={(event) => onDragStart(event, 'Agent')} draggable>Agent</CardText>
              </Card>
            </Col>
            <Col>
              <Card className="text-center" color="sucess" outline>
                <CardText onDragStart={(event) => onDragStart(event, 'Prompt')} draggable>Prompt</CardText>
              </Card>
            </Col>
            <Col>
              <Card className="text-center" color='primary' outline>
                <CardText onDragStart={(event) => onDragStart(event, 'Tool')} draggable>Tool</CardText>
              </Card>
            </Col>
          </Row>
        </Card>
      </Container>
    </aside>
  );
};





{/* <div className="styles.description">You can drag these nodes to the pane on the right.</div>
<div className="styles.dndnode input" onDragStart={(event) => onDragStart(event, 'input')} draggable>
  Input Node
</div>
<div className="styles.dndnode" onDragStart={(event) => onDragStart(event, 'default')} draggable>
  Default Node
</div>
<div className="styles.dndnode output" onDragStart={(event) => onDragStart(event, 'output')} draggable>
  Output Node
</div> */}