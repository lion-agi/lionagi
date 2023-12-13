Quick Start
===========

Start your LionAGI experience with our demo example.

.. code-block:: python

  import lionagi as li

  # define system messages, context and user instruction
  system = "You are a helpful assistant designed to perform calculations."
  instruction = {"Addition":"Add the two numbers together i.e. x+y"}
  context = {"x": 10, "y": 5}

  # Initialize a session with a system message
  calculator = li.Session(system=system)

  # run a LLM API call
  result = await calculator.initiate(instruction=instruction,
                                     context=context)

  print(f"Calculation Result: {result}")

Define your own system message, context, and instruction to initiate interactions with the language model.

Check out examples in the following sections to explore more diverse applications of LionAGI.