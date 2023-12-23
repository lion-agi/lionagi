RAG Assisted Auto Developer Continued -- Nested Sessions
=============================

Building upon the insights gained from our previous tutorial, `RAG Assisted Auto Developer -- with LionAGI, LlamaIndex,
AutoGen and OAI Code Interpreter <https://lionagi.readthedocs.io/en/latest/Get_started/Examples/coder.html>`_, we can
extend our capabilities by incorporating sessions within sessions that automatically improve our prompts. We are going
to give the coder a prompt bettering tool, so it can instruct the code interpreter more effectively.

Continuing from our exploration in the previous tutorial, let's build another tool using `Session`:

.. code-block:: python

   output_dir2 = "data/log/prompter/"

   system2 = """
        Your primary role is to refine AI bot prompts, ensuring they are clear and
        effective. Start by understanding the interaction context in detail. Analyze
        the initial prompts and the bot's responses. When improving a prompt, adopt
        a step-by-step approach, breaking down complex scenarios into simpler,
        more manageable tasks. Explain each step of your reasoning for the changes
        you propose, focusing on how they enhance clarity and effectiveness.
   """

   instruct4 = """
        Examine the responses from the AI bot, identifying areas where the original
        prompts could be causing confusion or inefficiency. When revising, consider
        how different tools, like query engines or coding bots, are used. For query
        engines, suggest breaking down complex queries into multiple smaller queries,
        possibly using parallel function calls for efficiency. For coding bots, provide
        clear, sequential instructions, ensuring each step is well-defined and
        understandable. Include specific prompting techniques that can improve the
        bot's effectiveness. For each modification, offer a comprehensive explanation
        detailing the rationale behind the change, how it addresses issues in the
        original prompt, and how it enhances the bot's response quality and relevance.
   """

   async def improve_prompts(context):
        prompter = li.Session(system=system2, dir=output_dir2)
        await prompter.initiate(instruction=instruct4, context=context, temperature=0.3)

        prompter.messages_to_csv()
        prompter.log_to_csv()
        return prompter.conversation.messages[-1]['content']

.. code-block:: python

   tool3 = [
    {
        "type": "function",
        "function": {
            "name": "improve_prompts",
            "description": """
                perform prompts improvements for an AI bot
                """,
            "parameters": {
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "prompts to improve",
                    }
                },
                "required": ["context"],
            }}}]

   tools2 = [tool2[0], tool3[0]]
   funcs2 = [code_pure_python, improve_prompts]

We also need to make adjustments to the previous instruction3 to integrate the capabilities of our new tool.

.. code-block:: python

   function_call3 = {
        "notice": """
            Use 'improve_prompts' with a focus on detail and structure:
            1. Prompt Identification: Highlight the specific part of the prompt that needs
               refinement. Use line numbers or quote the text directly.
            2. Issue Description: Describe what makes the current prompt unclear or ineffective.
            3. Suggested Improvements: Propose specific changes or enhancements. This could
               include rephrasing, adding context, or breaking down complex instructions.
            4. Expected Outcome: Explain how your suggested improvements will aid in better
               understanding or response accuracy from the AI bot.
            5. Test Scenarios: Suggest possible scenarios or questions to test the improved
               prompts effectiveness.
            By providing these details, you guide the AI bot towards creating more precise,
            understandable, and effective prompts.
        """
   }

   instruct3.update({"function_call2": function_call3})

Let's update our workflow and run it.

.. code-block:: python

   # solve a coding task in pure python
   async def solve_issue(context):

        coder = li.Session(system, dir=output_dir)
        coder.register_tools(tools=tools2, funcs=funcs2)

        await coder.initiate(instruct1, context=context, temperature=0.7)
        await coder.auto_followup(instruct2, num=num, temperature=0.6, tools=tool1,
                                   tool_parser=lambda x: x.response)

        # auto_followup with code interpreter tool
        await coder.auto_followup(instruct3, num=5, temperature=0.5, tools=[tool2[0], tool3[0]])

        # save to csv
        coder.messages_to_csv()
        coder.log_to_csv()

        # return codes
        return coder.conversation.messages[-1]['content']

.. code-block:: python

   # this one takes even longer: 15-25 mins
   # you can decrease num, the maximum number of tool use allowed per api call, to speed up
   response = await solve_issue(issue)

Check the new output:

.. code-block:: python

   class File:
        """
        A simple representation of a file that has a name, size, extension, and content.

        Attributes:
            name (str): The name of the file.
            size (int): The size of the file content in bytes.
            extension (str): The file extension indicating the file type.
            content (str): The content of the file, represented as a string.
        """

        def __init__(self, name, size, extension, content):
            """
            Initializes a new File instance with the provided attributes.

            Parameters:
                name (str): The name for the file.
                size (int): The size of the file content in bytes.
                extension (str): The file extension indicating the file type.
                content (str): The initial content of the file.
            """
            self.name = name
            self.size = size
            self.extension = extension
            self.content = content

        def read(self):
            """
            Returns the content of the file.

            Returns:
                str: The content of the file.

            Example:
                file = File("example", 12, ".txt", "Hello World!")
                content = file.read()
                print(content)  # Outputs: Hello World!
            """
            return self.content

        def write(self, new_content):
            """
            Updates the content of the file with new content and adjusts the file size.

            Parameters:
                new_content (str): The new content to write to the file.

            Example:
                file = File("example", 12, ".txt", "Hello World!")
                file.write("Goodbye World!")
                content = file.read()
                print(content)  # Outputs: Goodbye World!
                print(file.size)  # Outputs the size of the new content in bytes
            """
            self.content = new_content
            self.size = len(new_content)

   import hashlib

   class Chunk:
        """
        A class to represent a chunk of data with its index, content, and checksum.

        Attributes
        ----------
        index : int
            The index of the chunk in the sequence of chunks.
        data : str
            The string content of the chunk.
        checksum : str
            The SHA-256 checksum of the data content for verification purposes.

        Methods
        -------
        __init__(index: int, data: str, checksum: str)
            Initializes the Chunk with an index, data, and expected checksum.
        verify() -> bool
            Verifies if the actual checksum of the data matches the expected checksum.
        """

        def __init__(self, index: int, data: str, checksum: str):
            """
            Constructs all the necessary attributes for the Chunk object.

            Parameters
            ----------
            index : int
                The index of the chunk in the sequence of chunks.
            data : str
                The string content of the chunk.
            checksum : str
                The SHA-256 checksum of the data content for verification purposes.
            """
            self.index = index
            self.data = data
            self.checksum = checksum

        def verify(self) -> bool:
            """
            Verifies if the actual checksum of the data matches the expected checksum.

            Returns
            -------
            bool
                True if the actual and expected checksums match, False otherwise.
            """
            actual_checksum = hashlib.sha256(self.data.encode()).hexdigest()  # Calculate the SHA-256 checksum of the data
            return actual_checksum == self.checksum  # Compare calculated checksum with the expected checksum


   # Example Usage:
   # Given data and correct checksum calculated using SHA-256 hashing.
   chunk_data = "some data"
   correct_checksum = hashlib.sha256(chunk_data.encode()).hexdigest()
   chunk = Chunk(1, chunk_data, correct_checksum)

   # Testing the verify method.
   print(chunk.verify())  # Would print 'True' because the checksum matches the data.
