OpenAI API Calls Configurations
===============================

LionAGI natively supports OpenAI API calls. You have the flexibility to customize models, adjust model parameters, and
tailor API service settings.

.. warning::
   ❗❗Calling API with maximum throughput over large set of data with advanced models i.e. gpt-4 can
   get **EXPENSIVE IN JUST SECONDS**


Most usefully you can customize:

- ``oai_llmconfig``: the default model parameters for every API call
- ``OpenAIService``: the default settings for the API service

``oai_llmconfig``
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

If you wish to change the default behavior, you can update the configuration using ``lionagi.oai_llmconfig``.
For example:

.. code-block:: python

   import lionagi as li

   li.oai_llmconfig['model'] = 'gpt-3.5-turbo'

or

.. code-block:: python

   li.oai_llmconfig.update({'model': 'gpt-3.5-turbo'})

Alternatively, you can make changes in the ``Session``.

- Pass in a new llmconfig into the ``Session``. (Recommended for completely different config)

For example:

.. code-block:: python

   import lionagi as li

   system = 'you are a helpful assistant'
   customized_llmconfig = {...} # your customized llmconfig setting

   session = li.Session(system=system, llmconfig=customized_llmconfig)

Or

- Update directly in the session.

For example:

.. code-block:: python

   import lionagi as li

   system = 'you are a helpful assistant'

   session = li.Session(system)
   session.llmconfig.update({"model": "gpt-3.5-turbo", "temperature": 0.5})

``OpenAIService``
-----------

``OpenAIService`` provides a foundation for seamless integration and utilization of the API service. By default, the
rate limits are set to be **tier 1** of OpenAI model `gpt-4-1104-preview`.


You can modify rate limits to fit different cases. For example:

.. code-block:: python

   import lionagi as li

   system = 'you are a helpful assistant'

   api_service = li.OpenAIService(max_requests_per_minute=10, max_tokens_per_minute=10000)
   session = li.Session(system, api_service)

.. note::

   For more information about rate limits, please check the `OpenAI usage limit documentation <https://platform.openai.com/docs/guides/rate-limits?context=tier-free)>`_

If you have more than one API key, please add them to the `.env` file. To use an API key other than the default
OPENAI_API_KEY, ensure it is appropriately specified in the configuration.

.. code-block:: python

   import os
   from dotenv import load_dotenv
   load_dotenv()

   # let's say you added the second API key OPENAI_API_KEY2
   api_key2 = os.getenv("OPENAI_API_KEY2")

   api_service = li.OpenAIService(api_key=api_key2)
   session = li.Session(system, api_service=api_service)

.. note::

   If you wish to apply the same ``api_service`` setting across multiple sessions, make sure to pass it to each of these sessions.