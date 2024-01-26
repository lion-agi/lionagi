API Calls Configurations
===============================

The ``Session`` object can be fully customized, including models, model parameters and rate limits, to accustom various usecases.

.. warning::

   ❗❗Calling API with maximum throughput over large set of data with advanced models i.e. gpt-4 can
   get **EXPENSIVE IN JUST SECONDS**


Most usefully you can customize:

- ``llmconfig``: the default model parameters for every API call in the session
- ``service``:  rate limit LLM services

``llmconfig``
-----------------

Currently, our default llmconfig for Open AI API calls is

.. code-block:: python

   {'model': 'gpt-4-1106-preview',
   'frequency_penalty': 0,
   'max_tokens': None,
   'n': 1,
   'presence_penalty': 0,
   'response_format': {'type': 'text'},
   'seed': None,
   'stop': None,
   'stream': False,
   'temperature': 0.7,
   'top_p': 1,
   'tools': None,
   'tool_choice': 'none',
   'user': None}

if you wish to change the default behavior of a session

- you can either pass in a new llmconfig into the Session

.. code-block:: python

   llmconfig_ = {...}
   session = li.Session(system, llmconfig=llmconfig_)

- or update the config in the session directly

.. code-block:: python

   session.llmconfig.update(llmconfig_)

``service``
-----------

``service`` provides a foundation for seamless integration and utilization of the LLM service. By default, the
service is set to be OpenAI api service and the rate limits are set to be **tier 1** of OpenAI model ``gpt-4-1104-preview``.


You may modify rate limits to fit different cases. For example:

.. code-block:: python

   system = 'you are a helpful assistant'

   service = li.Services.OpenAI(max_requests=10, max_tokens=10_000, interval=60)
   session = li.Session(system, service=service)

.. note::

   For more information about rate limits, please check the `OpenAI usage limit documentation <https://platform.openai.com/docs/guides/rate-limits?context=tier-free)>`_

If you have more than one API key, please add them to the ``.env`` file. To use an API key other than the default
OPENAI_API_KEY, ensure it is appropriately specified in the configuration.

.. code-block:: python

   import os
   from dotenv import load_dotenv
   load_dotenv()

   # let's say you added the second API key OPENAI_API_KEY2
   api_key2 = os.getenv("OPENAI_API_KEY2")

   service = li.Services.OpenAI(api_key=api_key2)
   session = li.Session(system, service=service)

.. note::

   If you wish to apply the same ``service`` object across multiple sessions, make sure to pass it to each of these sessions.

   .. code-block::

      session2 = li.Session(system, service=service)
      session3 = li.Session(system, service=service)
