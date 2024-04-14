# Vote

This API reference provides documentation for the `vote` function, which generates and scores multiple outputs and selects the top-ranked ones based on the scores.

## vote

```python
async def vote(sentence, directive=predict, num_generations=5, num_output=1, num_scorer=5, score_range=(0, 100), num_digit=2, scorer_instruction=None, **kwargs)
```

Generates and [[score]] multiple outputs and returns the top-ranked output(s).

### Parameters

- `sentence` (str): The input sentence or context.
- `directive` (function): The function used to generate outputs (default: `predict`).
- `num_generations` (int): The number of outputs to generate (default: 5).
- `num_output` (int): The number of top-ranked outputs to return (default: 1).
- `num_scorer` (int): The number of scorers to use for scoring each output (default: 5).
- `score_range` (tuple): The range of scores to assign (default: (0, 100)).
- `num_digit` (int): The number of digits after the decimal point for scores (default: 2).
- `scorer_instruction` (str): The instruction for the scorers (default: None).
- `**kwargs`: Additional keyword arguments to pass to the directive function.

### Returns

- The top-ranked output if `num_output` is 1, or a list of top-ranked outputs if `num_output` is greater than 1.

### Description

The `vote` function generates and scores multiple outputs and selects the top-ranked ones based on the scores. It follows these steps:

1. It generates `num_generations` outputs using the specified `directive` function (default: `predict`).
2. For each generated output, it scores the output using the `score` function with `num_scorer` scorers and the specified `score_range` and `num_digit`.
3. It assigns the average score to each output.
4. It selects the top `num_output` outputs based on their scores.
5. If `num_output` is 1, it returns the top-ranked output. Otherwise, it returns a list of top-ranked outputs.

The `vote` function allows for customization of the number of generations, number of outputs to return, number of scorers, score range, and scorer instruction. It also accepts additional keyword arguments to pass to the directive function.

The `vote` function is useful when you want to generate multiple outputs and select the best ones based on scoring criteria. It can help improve the quality and relevance of the generated outputs by leveraging multiple scorers and ranking the outputs based on their scores.
