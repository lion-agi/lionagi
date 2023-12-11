Example: Calculator
===================

Let's construct a simple conditional calculator.

In this example, we will have two steps in the instruction:

#. Choose between sum or diff based on a case number

#. Choose between times or plus based on the sign of the first step

.. code-block:: python

   system = "You are asked to perform as a calculator. Think step by step, but return only a numeric value, i.e. int or float, no text."

   instruct1 = {
        "sum the absolute values": "provided with 2 numbers, return the sum of their absolute values. i.e. |x|+|y|",}

   instruct2 = {
        "diff the absolute values": "provided with 2 numbers, return the difference of absolute values. i.e. |x|-|y|",}

   instruct3 = {
        "if previous response is positive": "times 2. i.e. *2",
        "else": "plus 2. i.e. +2",
   }

Let's create a case and context:

.. code-block:: python

   case = 0
   context = {"x": 7, "y": 3}
   instruct = instruct1 if case == 0 else instruct2

Now, we are ready to create our first session:

.. code-block:: python

   import lionagi as li

   calculator = li.Session(system)
   step1 = await calculator.initiate(instruct, context=context)
   step2 = await calculator.followup(instruct3, temperature=0.5)

In this case, we initialize two numbers, ``x=7`` and ``y=3``. By setting ``case=0``, we opt to follow ``instruct1``, which instructs
the calculation of the sum of absolute values: ``|x|+|y|``. Given that ``|7|+|3|=10`` resulting in a positive outcome,
we should execute the first instruction in ``instruct3``, ``"times 2. i.e. \*2"``. Consequently, we expect the final result
to be ``20``.

.. code-block:: python

   print(f"step1 result: {step1}")
   print(f"step2 result: {step2}")

.. parsed-literal::

   step1 result: 10
   step2 result: 20
