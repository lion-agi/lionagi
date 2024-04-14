# Chain of Thoughts and Chain of React

This API reference provides documentation for the `chain_of_thoughts` and `chain_of_react` functions, which are used for generating a chain of thoughts or a chain of reactions based on a given sentence or context using a language model and specified tools.

## Table of Contents

1. [chain_of_thoughts](#chain_of_thoughts)
   - [Parameters](#parameters)
   - [Returns](#returns)
2. [chain_of_react](#chain_of_react)
   - [Parameters](#parameters-1)
   - [Returns](#returns-1)

## chain_of_thoughts

```python
async def chain_of_thoughts(sentence=None, branch=None, instruction=None, reason=False, confidence_score=False, num_steps=3, directive_kwargs={}, return_branch=False, **kwargs)
```

Generates a chain of thoughts based on a given sentence or context using a language model. basing on a [[plan]]

### Parameters

- `sentence` (Optional[str | list | dict]): The given sentence(s) or context to generate a chain of thoughts for.
- `branch` (Optional[Branch]): The [[branch]] to use for chain of thoughts generation. If not provided, a new branch will be created.
- `instruction` (Optional[str]): The instruction for generating the chain of thoughts.
- `reason` (bool): Whether to include the reason for each thought in the output (default: False).
- `confidence_score` (bool): Whether to include the confidence score for each thought in the output (default: False).
- `num_steps` (int): The number of steps in the chain of thoughts (default: 3).
- `directive_kwargs` (dict): Additional keyword arguments for the directive used in each step of the chain.
- `return_branch` (bool): Whether to return the branch along with the chain of thoughts output (default: False).
- `**kwargs`: Additional keyword arguments for the API call.

### Returns

- `Tuple[PlanTemplate, Branch] | PlanTemplate`: The chain of thoughts output and optionally the branch if `return_branch` is True.

## chain_of_react

```python
async def chain_of_react(sentence=None, branch=None, instruction=None, num_steps=3, tools=None, directive_system=None, directive_kwargs={}, return_branch=False, **kwargs)
```

Generates a chain of [[react]] based on a given sentence or context using a language model and specified tools.

### Parameters

- `sentence` (Optional[str | list | dict]): The given sentence(s) or context to generate a chain of reactions for.
- `branch` (Optional[Branch]): The branch to use for chain of reactions generation. If not provided, a new branch will be created.
- `instruction` (Optional[str]): The instruction for generating the chain of reactions.
- `num_steps` (int): The number of steps in the chain of reactions (default: 3).
- `tools` (Optional[Any]): The tools to use for each step in the chain of reactions.
- `directive_system` (Optional[Any]): The system configuration for the directive used in each step of the chain.
- `directive_kwargs` (dict): Additional keyword arguments for the directive used in each step of the chain.
- `return_branch` (bool): Whether to return the branch along with the chain of reactions output (default: False).
- `**kwargs`: Additional keyword arguments for the API call.

### Returns

- `Tuple[PlanTemplate, Branch] | PlanTemplate`: The chain of reactions output and optionally the branch if `return_branch` is True.

