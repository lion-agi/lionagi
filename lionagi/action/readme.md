#### Action

Conceptually, `action` drew inspiration from `runnable` in `langchain`. 

It is designed as an object to store, evaluate, manipulate a specific flow of tool usages
according to certain logic. 

It contains one or more `action_node`. 

An `action_node` object is an `evaluatable`, meaning, this object can be observed and 
evaluated by an `agent`.

Basing on the evaluation and consideration, an agent can choose to invoke one or more
action nodes in a custom set of logic. 

this logic, along with its corresponding input/output is called an action.



