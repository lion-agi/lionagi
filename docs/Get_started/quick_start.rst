Quick Start
===========

Start your LionAGI experience with our demo example.

.. code-block:: python

  # define system messages, context and user instruction
  system = "You are a helpful assistant designed to perform calculations."
  instruction = {"Addition":"Add the two numbers together i.e. x+y"}
  context = {"x": 10, "y": 5}

.. code-block:: python

   # in interactive environment (.ipynb for example)
   import lionagi as li

   calculator = li.Session(system=system)
   result = await calculator.chat(instruction=instruction,
                                  context=context,
                                  model="gpt-4-1106-preview")

   print(f"Calculation Result: {result}")

.. code-block:: python

   # or otherwise, you can use
   import asyncio
   from dotenv import loadenv
   load_dotenv()

   import lionagi as li

   async def main():
       calculator = li.Session(system=system)
       result = await calculator.chat(instruction=instruction,
                                      context=context,
                                      model="gpt-4-1106-preview")
       print(f"Calculation Result: {result}")

   if __name__ == "__main__":
       asyncio.run(main())

Define your own system message, context, and instruction to initiate interactions with the language model.

Check out examples in the following sections to explore more diverse applications of LionAGI.