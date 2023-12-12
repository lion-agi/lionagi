Comedian
========

Let's do something fun!

In this example, we are going to have two roles, a comedian and a commentator. The comedian will start by making two
jokes. Following that, the commentator will provide the comments. Finally, the comedian will revise the jokes based on
the feedback.

.. code-block:: python

   sys_comedian = "As a comedian, you are sarcastically funny"
   instruct1 = "very short joke: a blue whale and a big shark meet at the bar and start dancing"
   instruct2 = "continue the short joke: the blue whale was confused why it was dancing with a shark"

In the first step, we create a session with the comedian and generate some jokes in a multi-turn conversation

.. code-block:: python

   import lionagi as li

   comedian = li.Session(sys_comedian)

   joke1 = await comedian.initiate(instruct1)
   joke2 = await comedian.followup(instruct2)

Here are the two jokes we get:

.. code-block:: markdown

   Why did the blue whale and the big shark get kicked out of the bar?
   Because every time they hit the dance floor,it turned into a splash mob!

.. code-block:: markdown

   The blue whale turned to the shark and said, "I must have had one too many plankton cocktails
   because I'm pretty sure we're supposed to be natural enemies, not dance partners!"

Now, let's construct a commentator to critique these two jokes.

.. code-block:: python

   sys_critic = "you are a respected commentator, you are artistically logical"
   instruct3 = "short comments, what do you think about the first joke?"
   instruct4 = "provide a concise artistic critique on both jokes, and rate from 1-10"

   context = {
    "joke1": {"prompt": instruct1, "response": joke1},
    "joke2": {"prompt": instruct2, "response": joke2}
   }

.. code-block:: python

   critic = li.Session(sys_critic)

   # you only need to provide same context once in a conversation
   comment1 = await critic.initiate(instruct3, context=context)
   comment2 = await critic.followup(instruct4)

We have received two comments:

.. code-block:: markdown

   The whimsy of the first joke hinges on a clever play on words, transforming a common social
   phenomenon into an aquatic pun. It's a light-hearted jab at the chaos that might ensue when
   two large sea creatures attempt to groove together, effectively tickling the imagination.

.. code-block:: markdown

   Joke 1 offers an amusing visual of a seemingly impossible scenario, blending the mundane
   with the extraordinary to create a scene ripe for comedy. The punchline delivers an unexpected
   twist, playing on the term "flash mob" and adapting it to the characters involved. The joke's
   strength lies in its brevity and the surprise element of the pun. Rating: 7/10

   Joke 2 builds on the absurdity of the first by adding a layer of self-awareness from the whale's
   perspective, which invites the audience into the whale's internal monologue. This joke leans on the
   incongruity of a predator-prey relationship turned into a partnership, which is a classic foundation
   for humor. However, the punchline lacks the sharpness of the first. Rating: 6/10

Let's take a look at the comedian's responses.

.. code-block:: python

   # messages for comedian again
   instruct5 = "your jokes were evaluated by a critic, does it make sense to you? why?"
   instruct6 = "based on your reflection, write joke1 again"
   instruct7 = "write joke2 again"

   # provide context for the comedian
   context2 = {"comments": critic.conversation.responses}

   # run the instructions
   reflect = await comedian.followup(instruct5, context=context2)
   joke11 = await comedian.followup(instruct6)
   joke22 = await comedian.followup(instruct7)

Reflection:

.. code-block:: markdown

   As the comedian behind the jokes, it makes perfect sense to me that a critic would evaluate them
   in such a way. The detailed analysis of the first joke captures the essence of what I was going
   for—a playful use of words and a situation that's both absurd and visually engaging. The critic's
   appreciation for the wordplay and the surprise factor aligns with the aim to entertain and delight
   the audience quickly and effectively.

   The second joke's critique also resonates with my intent. It's designed to give the characters depth,
   allowing the audience to wonder what a sea creature might think when placed in a human-like scenario.
   The rating suggests that while the joke does a good job of expanding the narrative and adding humor
   through the unexpected, it doesn't quite match the punch of the first joke's concise wit. The
   discrepancy in ratings between the two jokes is understandable, as humor can often be hit or miss,
   and the impact of a joke can vary depending on the delivery and audience engagement.

   In conclusion, the critic's feedback is valuable and provides insight into how the jokes are perceived
   from an objective standpoint. It's a reminder that as a comedian, there's always a balance to be struck
   between cleverness, relatability, and the element of surprise.

Revised Joke 1:

.. code-block:: markdown

   Why did the blue whale and the big shark get kicked out of the bar? Because they turned the dance floor
   into a literal "wave pool"!

Revised Joke 2:

.. code-block:: markdown

   The blue whale looked at the shark in bewilderment and blurted out, "This is fin-tastic, but if we keep
   this up, we're going to need a bigger sea-quarium!"

If you want to save these messages or llm api logs, do not forget:

.. code-block:: python

   comedian.messages_to_csv(dir=<target_output_directory>)
   comedian.log_to_csv(dir=<target_output_directory>)

   critic.messages_to_csv(dir=<target_output_directory>)
   critic.log_to_csv(dir=<target_output_directory>)

Instead of defining the directory the last step, you can also set it when initializing the sessions. For example,

.. code-block:: python

   comedian = li.Session(sys_comedian, dir="data/logs/comedian/")

   critic = li.Session(sys_critic, dir="data/logs/critic/")

Next time, if you wish to retrieve these saved data, you can use:

.. code-block:: python

   li.dir_to_files(<directory>, <file_extension>)

For example:

.. code-block:: python

   files = li.dir_to_files("data/logs", ".csv")