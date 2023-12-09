Understanding Session
=====================

.. code:: ipython3

    from IPython.display import Markdown
    import lionagi as li

The ``Session`` object is at the core of lionagi.

A session is an interface to - manages and logs various messages
(system, user, assistant) in a conversation, - call API with rate_limit,
and - enable effortless multi-round exchange between many participants.

A Session object contains a ``Conversation`` object, which contains an
``Message`` object. - ``Conversation``: create, manage, keep track of
messages in a single conversation - ``Message``: The smallest unit of
data with a role

**Note:** currently Session can only call ChatCompletion, also only
supports one assistant in a conversation.

1. Initiate and Followup
------------------------

Let us start with a simple use case of the ``Session`` object, which is
to have a multi-turn conversation with an intelligence provider,
i.e. OpenAI API service.

.. code:: ipython3

    # create some messages
    sys_comedian = "you are a famous comedian, you are sarcastically funny"
    instruct1 = {"tell a short joke": "a blue whale and a big shark meet at the bar and start dancing"}
    instruct2 = {"build the joke further": "the blue whale was confused why it was dancing with a shark"}

.. code:: ipython3

    # create a session with the comedian and generate some jokes in a multi-turn conversation
    comedian = li.Session(sys_comedian, dir="data/logs/comedian/")
    
    joke1 = await comedian.initiate(instruct1)
    joke2 = await comedian.followup(instruct2)

.. code:: ipython3

    Markdown(joke1)




So a blue whale and a big shark walk into a bar, right? And they start
dancing. But here’s the punchline: the real joke is the squid in the
corner taking bets on who’s going to break the dance floor first!



.. code:: ipython3

    Markdown(joke2)




So there’s this blue whale and a big shark cutting a rug at the bar, and
the whale is looking all kinds of confused. It leans in and whispers to
the shark, “I thought I signed up for ‘Whale Watching,’ not ‘Shark
Tango’!” The shark grins, showing all his teeth and says, “Don’t worry,
big guy, just think of this as a ‘fin’-tastic cultural exchange. And
besides, when was the last time you had a dance partner that didn’t try
to harpoon you halfway through the song?”



2. Using a second Session
-------------------------

.. code:: ipython3

    # some messages from the critic
    sys_critic = "you are a respected commentator, you are logically critical"
    instruct3 = {"briefly analyze the story":"the comedian is telling a joke, what do you think?"}
    instruct4 = {"concisely comment on the story":"give a score of the jokes, from 1-10, give artistic feedback"}
    
    critic = li.Session(sys_critic, dir="data/logs/critic/")

.. code:: ipython3

    # provide context for critic
    context = {
        "instructions": f"first {instruct1} secondly: {instruct2}",
        "response": f"first {joke1} secondly: {joke2}",
    }
    
    comment1 = await critic.initiate(instruct3, context=context)
    comment2 = await critic.followup(instruct4)

.. code:: ipython3

    Markdown(comment1)




Analyzing the structure and delivery of the joke provided, it is clear
that it relies on the absurdity and the anthropomorphism of the animals
involved. The initial setup of a blue whale and a big shark walking into
a bar and starting to dance is a play on the classic format of “a man
walks into a bar” jokes, but with an unexpected twist. This sets the
stage for a surreal and humorous imagery.

The punchline provided in the first part employs a third element, the
squid, which is not only unexpected but also adds a layer of complexity
to the joke by introducing the idea of gambling on a seemingly unrelated
outcome – which of the two large animals will break the dance floor.
This punchline plays on the common expectation that a joke involving a
bar will end with some witty comment or a pun, but instead offers a
scenario that is both comical and visually amusing.

In the second part of the joke, the confusion of the blue whale is used
as a device to build up to the punchline. The whale’s expectation of a
“Whale Watching” experience juxtaposed with the “Shark Tango” introduces
wordplay and sets the stage for the shark’s response, which contains
light-hearted puns such as “fin-tastic” and cultural exchange, adding
layers of humor.

The shark’s final remark about not being harpooned offers a darkly
comedic twist that plays on the real-life dangers whales face, while
also keeping in line with the light-hearted tone of the joke.

Overall, the joke’s humor is derived from the absurdity of the
situation, the playful use of language, and the subversion of
expectations. The anthropomorphic behavior of the animals, along with
the addition of the squid as a betting agent, creates a mini-narrative
that is engaging and humorous. However, the effectiveness of the joke
would largely depend on the delivery and timing of the comedian, as well
as the audience’s receptiveness to this type of humor.



.. code:: ipython3

    Markdown(comment2)




Score: 6/10

Artistic Feedback: The jokes presented employ a playful sense of the
absurd and anthropomorphism to create humor. The imagery of sea
creatures engaging in human activities like dancing and betting is
imaginative and whimsical, which can be quite appealing. The use of
wordplay and puns adds a layer of cleverness to the jokes, enhancing
their comedic value.

However, the jokes could benefit from tighter punchlines. The first
part’s punchline, while unexpected, might be a bit too detached from the
setup, which could lead to a disconnect for the audience. The second
part, while it builds on the initial scenario, might not deliver a
strong enough punchline to elicit a hearty laugh, as the humor is
somewhat niche and relies heavily on the audience’s appreciation for
puns.

To improve the jokes, consider refining the punchlines to more directly
tie back to the initial setup, and perhaps introduce a stronger element
of surprise or a twist that more clearly connects to the humorous
imagery of dancing sea creatures. Additionally, ensuring that the jokes
cater to a broader audience could help in increasing their overall
impact.



Save the logs
^^^^^^^^^^^^^

.. code:: ipython3

    # create seperate log for each session, and save both messages and llm api logs to seperate csv files
    
    comedian.messages_to_csv()
    comedian.log_to_csv()
    
    critic.messages_to_csv()
    critic.log_to_csv()


.. parsed-literal::

    4 logs saved to data/logs/comedian/2023-12-07T17_58_50_973798_messages.csv
    2 logs saved to data/logs/comedian/2023-12-07T17_58_50_974445_llmlog.csv
    4 logs saved to data/logs/critic/2023-12-07T17_58_50_974911_messages.csv
    2 logs saved to data/logs/critic/2023-12-07T17_58_50_975201_llmlog.csv


3. Use two Sessions in a workflow
---------------------------------


4. Customize Configuration
--------------------------

Changing the Rate Limit
^^^^^^^^^^^^^^^^^^^^^^^

The default rate limit set is **tier 1** of OpenAI
``gpt-4-1104-preview`` model, it might be not approapriate for your use
case. But in general, this is more than sufficient, you might be
spending multiple times quicker than you think. please check the usage
limit frequently.

For example, - During developments, you might want to set a lower limit,
so you don’t accidentally spend too much on testing. - When in actual
production, you might want to set to much higher, if you can, for high
throughput and fast execution. (for example, to go through large number
of files with established LLM procedure)

Notice: \* currently only enforce miniute token limit, not day limit nor
total usage limit yet.

