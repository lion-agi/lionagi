


Let\'s construct a simple conditional calculator.

In this example, we will have two steps in the instruction:

1.  Choose between sum or diff based on a case number
2.  Choose between times or plus based on the sign of the first step

``` python
system =
'''
You are asked to perform as a calculator.
Think step by step, but return only a numeric value, i.e. int or float, no text.
'''

instruct1 = {
     "sum the absolute values":
     "provided with 2 numbers, return the sum of their absolute values. i.e. |x|+|y|",}

instruct2 = {
     "diff the absolute values":
     "provided with 2 numbers, return the difference of absolute values. i.e. |x|-|y|",}

instruct3 = {
     "if previous response is positive": "times 2. i.e. *2",
     "else": "plus 2. i.e. +2",
}
```

Let\'s create a case and context:

``` python
case = 0
context = {"x": 7, "y": 3}
instruct = instruct1 if case == 0 else instruct2
```

Now, we are ready to create our first session:

``` python
from lionagi import Session

calculator = Session([[system#^2711f6|System]])
step1 = await calculator.chat(instruct, context=context)
step2 = await calculator.chat(instruct3, temperature=0.5)
```

In this case, we initialize two numbers, `x=7` and `y=3`. By setting
`case=0`, we opt to follow `instruct1`, which instructs the calculation
of the sum of absolute values: `|x|+|y|`. Given that `|7|+|3|=10`
resulting in a positive outcome, we should execute the first instruction
in `instruct3`, `"times 2. i.e. \*2"`. Consequently, we expect the final
result to be `20`.

``` python
print(f"step1 result: {step1}")
print(f"step2 result: {step2}")
```

``` markdown
step1 result: 10
step2 result: 20
```

Instead of dealing with a single set of numbers, let\'s expand to five
sets.

Assume we have a list of xs:

``` python
xs = [1, 2, 3, 4, 5]
```

To get their corresponding ys, we\'d like to apply the following
functions:

``` python
# Expected Results
f1 = lambda x: x*2       # y1 = x1 * 2 = 1 * 2 = 2
f2 = lambda x: x**2      # y2 = x2 ** 2 = 2 ** 2 = 4
f3 = lambda x: x+2       # y3 = x3 + 2 = 3 + 2 = 5
f4 = lambda x: x//2      # y4 = x4 // 2 = 4 // 2 = 2
f5 = lambda x: x-2       # y5 = x5 - 2 = 5 - 2 = 3
```

LionAGI has a helper function `mcall` (map call) to streamline the
execution of element-wise functions. Rather than explicitly executing
each function on every element, you can achieve it in a single call.

``` python
import lionagi.libs.ln_func_call as func_call

f = [f1,f2,f3,f4,f5]
ys = await func_call.mcall(xs, f)
```

Suppose the cases for each pair of x and y are:

``` python
cases = [1, 0, 1, 0, 1]
```

Now, with all the necessary information in hand, let\'s organize it into
contexts. LionAGI provides a utility function `lcall` (list call) to
streamline the application of a single function across an entire input
list.

``` python
f = lambda i: {
	"x": str(xs[i]),
	"y": str(ys[i]),
	"case": str(cases[i])
}

contexts = func_call.lcall(range(5), f)
```

If you print out the `contexts`, it would be like this:

``` markdown
{'x': '1', 'y': '2', 'case': '1'}
{'x': '2', 'y': '4', 'case': '0'}
{'x': '3', 'y': '5', 'case': '1'}
{'x': '4', 'y': '2', 'case': '0'}
{'x': '5', 'y': '3', 'case': '1'}
```

We are ready to establish another calculator session resembling the
previous one. This time, we will design a workflow for concurrent
execution, running five scenarios in parallel.

``` python
async def calculator_workflow(context):

     calculator = Session([[system#^2711f6|System]])       # construct a session instance
     context = context.copy()
     case = int(context.pop("case"))
     instruct = instruct1 if case == 0 else instruct2

     step1 = await calculator.chat(instruct, context=context)
     step2 = await calculator.chat(instruct3, temperature=0.5)

     return (step1, step2)

# al_call (async list call): async version of l_call
outs = await func_call.alcall(contexts, calculator_workflow)
```

Let's check our results:

``` python
for idx, out in enumerate(outs):
     print(f"Inputs: {a[idx]}, {b[idx]}, case: {cases[idx]}\n")
     print(f"Outputs: {out}")
     print("------\n")
```

``` markdown
Inputs: 1, 2, case: 1

Outputs: ('-1', '1')

------

Inputs: 2, 4, case: 0

Outputs: ('6', '12')

------

Inputs: 3, 5, case: 1

Outputs: ('-2', '0')

------

Inputs: 4, 2, case: 0

Outputs: ('6', '12')

------

Inputs: 5, 3, case: 1

Outputs: ('2', '4')

------
```
