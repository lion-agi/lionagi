LionAGI introduction 3 - LLM sessions
=====================================

.. code:: ipython3

    # we will use numpy to generate random numbers for this notebook
    # %pip install numpy

.. code:: ipython3

    import lionagi as li

.. code:: ipython3

    from timeit import default_timer as timer
    start = timer()

.. code:: ipython3

    system = """
    You are a helpful assistant. You are asked to perform as a calculator. Return as an integer.
    """
    
    calculator = li.Session(system=system)

.. code:: ipython3

    a = -3
    b = 4
    
    context = {
        "number1": a,
        "number2": b,
    }
    
    instruct1 = {
        "sum the absolute values": "provided with 2 numbers, return the sum of their absolute values",}
    
    instruct2 = {
        "multiplication": "provided with 2 numbers, return their multiplication",}
    
    instruct3 = {
        "case positive": "if the result from previous step is positive, times 2 to the previous step's result",
        "case negative": "elif the result from previous step is negative, plus 2 to the previous step's result",
        "case zero": "elif the result from previous step is zero, return the previous step's result",}


.. code:: ipython3

    await calculator.initiate(instruction=instruct1, context=context)




.. parsed-literal::

    '7'



.. code:: ipython3

    cal1 = await calculator.initiate(instruction=instruct1, context=context)
    cal2 = await calculator.followup(instruction=instruct3, temperature=0.5)
    
    print(f"Given {a} and {b}, the sum of absolute values is {cal1}")
    print(f"Since the step 1 result is {'positive' if int(cal1)>0 else 'negative'}, the second step result is {cal2}")


.. parsed-literal::

    Given -3 and 4, the sum of absolute values is 7
    Since the step 1 result is positive, the second step result is 14


.. code:: ipython3

    cal1 = await calculator.initiate(instruction=instruct2, context=context)
    cal2 = await calculator.followup(instruction=instruct3, temperature=0.5)
    
    print(f"Given {a} and {b}, the multiplication product is {cal1}")
    print(f"Since the step 1 result is {'positive' if int(cal1)>0 else 'negative'}, the second step result is {cal2}")


.. parsed-literal::

    Given -3 and 4, the multiplication product is -12
    Since the step 1 result is negative, the second step result is -10


.. code:: ipython3

    #### ok now let's see how we can make it more interesting
    import numpy as np
    num_iterations = 5
    
    ints1 = np.random.randint(-10, 10, size=num_iterations)
    ints2 = np.random.randint(0, 10, size=num_iterations)
    cases = np.random.randint(0,2, size=num_iterations)
    # let's define a simple parser function
    
    f = lambda i: {"number1": str(ints1[i]), "number2": str(ints2[i]), "case_": str(cases[i])}
    contexts = li.l_call(range(num_iterations), f)

.. code:: ipython3

    system = """
    You are a helpful assistant. You are asked to perform as a calculator. Return as an integer.
    """
    
    context = {
        "number1": a,
        "number2": b,
    }
    
    instruct1 = {
        "sum the absolute values": "provided with 2 numbers, return the sum of their absolute values. i.e. |x|+|y|",}
    
    instruct2 = {
        "diff the absolute values": "provided with 2 numbers, return the difference of absolute values. i.e. |x|-|y|",}
    
    instruct3 = {
        "if previous response is positive": "times 2. i.e. *2", # case 1
        "else": "plus 2. i.e. +2",                              # case 2
    }

.. code:: ipython3

    dir="/Users/lion/Documents/GitHub/gitco/notebooks/logs/"

.. code:: ipython3

    async def calculator_workflow(context_):
        calculator = li.Session(system=system)
        context = context_.copy()
        case = int(context.pop("case_"))
        
        if case == 0:
            await calculator.initiate(instruction=instruct1, context=context, temperature=0.5)
        elif case == 1:
            await calculator.initiate(instruction=instruct2, context=context, temperature=0.5)
        
        await calculator.followup(instruction=instruct3, temperature=0.3)
        calculator.conversation.append_last_response()
        calculator.conversation.msg.logger.to_csv(dir=dir, filename = "calculator_messages.csv")
        return li.l_call(calculator.conversation.responses, lambda i: i['content'])

.. code:: ipython3

    start1 = timer()
    
    outs = await li.al_call(contexts, calculator_workflow)
    
    elapsed_time = timer() - start1
    print(f"num_workload: {num_iterations}")
    print(f"run clock time: {elapsed_time:0.2f} seconds")


.. parsed-literal::

    5 logs saved to /Users/lion/Documents/GitHub/gitco/notebooks/logs/2023-12-07T16_32_56_153769calculator_messages.csv
    5 logs saved to /Users/lion/Documents/GitHub/gitco/notebooks/logs/2023-12-07T16_32_56_413532calculator_messages.csv
    5 logs saved to /Users/lion/Documents/GitHub/gitco/notebooks/logs/2023-12-07T16_32_56_429292calculator_messages.csv
    5 logs saved to /Users/lion/Documents/GitHub/gitco/notebooks/logs/2023-12-07T16_32_56_437149calculator_messages.csv
    5 logs saved to /Users/lion/Documents/GitHub/gitco/notebooks/logs/2023-12-07T16_33_00_931785calculator_messages.csv
    num_workload: 5
    run clock time: 7.55 seconds


.. code:: ipython3

    for idx, out in enumerate(outs):
        print(f"Inputs: {ints1[idx]}, {ints2[idx]}, case: {cases[idx]}\n")
        print(f"Outputs: {out}")
        print("------\n")


.. parsed-literal::

    Inputs: -9, 6, case: 1
    
    Outputs: ['3', '6']
    ------
    
    Inputs: -1, 8, case: 0
    
    Outputs: ['9', '18']
    ------
    
    Inputs: 3, 5, case: 0
    
    Outputs: ['8', '16']
    ------
    
    Inputs: 6, 3, case: 1
    
    Outputs: ['3', '6']
    ------
    
    Inputs: -4, 6, case: 1
    
    Outputs: ['The difference of the absolute values of -4 and 6 is |(-4)| - |6| which equals 4 - 6. The result is -2. However, since you requested an integer without specifying the need for an absolute value, the result is -2.', 'Since the previous response was -2, which is not positive, we will follow the "else" instruction and add 2.\n\n-2 + 2 = 0\n\nThe result is 0.']
    ------
    


.. code:: ipython3

    elapsed_time = timer() - start

.. code:: ipython3

    print(f"Notebook total runtime {elapsed_time:0.2f} seconds")


.. parsed-literal::

    Notebook total runtime 15.49 seconds

