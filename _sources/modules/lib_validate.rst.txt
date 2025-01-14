========================================
``libs.validate`` Subpackage
========================================

This subpackage provides a variety of **validation utilities**. It includes:

- **Boolean validation** (e.g. parse "true"/"yes"/"1" to Python `bool`).
- **String similarity**-based key matching (fuzzy validation).
- **Model field validators** (suitable for Pydantic usage).
- **High-level mapping validation** (turn arbitrary data into a valid dictionary with expected keys).


---------------------------
1) ``validate_boolean.py``
---------------------------
.. module:: lionagi.libs.validate.validate_boolean
   :synopsis: Strict conversion of inputs to a Python bool

**Key Exports**:

.. function:: validate_boolean(x) -> bool

   Attempt to convert an arbitrary input (None, bool, numeric, str, etc.) into a 
   Python boolean. Recognizes many common textual representations (e.g. "yes", 
   "no", "on", "off", etc.). Raises an error if conversion is not possible.

   **Examples**::

      from lionagi.libs.validate.validate_boolean import validate_boolean

      assert validate_boolean("yes") is True
      assert validate_boolean(0j) is False
      validate_boolean(None)  # raises TypeError

   - **TRUE_VALUES**: a frozenset of recognized "true" strings (case-insensitive).
   - **FALSE_VALUES**: a frozenset of recognized "false" strings.


-----------------------------------------
2) ``common_field_validators.py`` (alias)
-----------------------------------------
.. module:: lionagi.libs.validate.common_field_validators
   :synopsis: Often used in Pydantic model validators

A collection of small helper functions typically used as class validators in Pydantic 
models.

**Highlights**:

.. function:: validate_boolean_field(cls, value, default=None) -> bool | None

   Wraps `validate_boolean`, returning a default if conversion fails.

.. function:: validate_same_dtype_flat_list(cls, value, dtype, default=[], dropna=True) -> list

   Ensure `value` can be interpreted as a list of a single data type `dtype`.  
   Useful for Pydantic fields that must be homogeneous lists.

.. function:: validate_nullable_string_field(cls, value, field_name, strict=True) -> str | None

   Check if `value` is a string or empty, or allow `None`. 

.. function:: validate_nullable_jsonvalue_field(cls, value) -> JsonValue | None

   For fields that can be JSON or None.

.. function:: validate_dict_kwargs_params(cls, value) -> dict

   Ensure a dict for validator kwargs.

.. function:: validate_callable(cls, value, undefind_able=True, check_name=False) -> callable

   Check if `value` is callable.

.. function:: validate_model_to_type(cls, value)

   Return a valid Pydantic model or raise.

.. function:: validate_list_dict_str_keys(cls, value)

   Confirm that a list/dict is purely string-based keys.

.. function:: validate_str_str_dict(cls, value)

   Confirm a dictionary is \{str -> str\}.


---------------------
3) ``string_similarity.py``
---------------------
.. module:: lionagi.libs.validate.string_similarity
   :synopsis: Core string-similarity functions (Levenshtein, Jaro-Winkler, etc.)

**Key Exports**:

.. function:: string_similarity(word, correct_words, algorithm="jaro_winkler", threshold=0.0, case_sensitive=False, return_most_similar=False) -> str | list[str] | None

   Compare a single `word` to a list of `correct_words` using various similarity 
   metrics. Return either the single best match or all matches above `threshold`.  

   Supported built-in algorithms:
   
   - "jaro_winkler" (default)
   - "levenshtein"
   - "sequence_matcher" (Python stdlib)
   - "hamming" (only if strings are same length)
   - "cosine"

.. function:: jaro_winkler_similarity(s, t, scaling=0.1) -> float

   A popular measure of string distance, returning [0..1].

.. function:: levenshtein_similarity(s1, s2) -> float

   Convert the edit distance to a similarity.  

Plus other lower-level distance measures (Hamming, Cosine, etc.).


-------------------------
4) ``fuzzy_match_keys.py``
-------------------------
.. module:: lionagi.libs.validate.fuzzy_match_keys
   :synopsis: Fuzzy dictionary key validation

**Key Exports**:

.. function:: fuzzy_match_keys(d_, keys, similarity_algo="jaro_winkler", similarity_threshold=0.85, fuzzy_match=True, handle_unmatched="ignore", fill_value=None, fill_mapping=None, strict=False) -> dict

   Given a dictionary `d_` and an expected list of keys (or dict), attempt to 
   align actual keys to expected keys, possibly using string similarity.  Various 
   ways to handle unmatched or missing keys are supported.

   - **handle_unmatched** can be:
     
     * "ignore" : keep unmatched as-is
     * "raise"  : raise ValueError on unmatched
     * "remove" : discard unmatched
     * "fill"   : fill missing with `fill_value` or `fill_mapping`
     * "force"  : combine "fill" + "remove"

.. class:: FuzzyMatchKeysParams

   Pydantic-friendly parameter class that calls `fuzzy_match_keys()`.


---------------------------
5) ``fuzzy_validate_mapping.py``
---------------------------
.. module:: lionagi.libs.validate.fuzzy_validate_mapping
   :synopsis: Convert arbitrary data to a dictionary with expected keys

**Key Exports**:

.. function:: fuzzy_validate_mapping(d, keys, similarity_algo="jaro_winkler", similarity_threshold=0.85, fuzzy_match=True, handle_unmatched="ignore", fill_value=None, fill_mapping=None, strict=False, suppress_conversion_errors=False) -> dict

   1) Convert `d` to a dictionary if possible (string -> parse JSON, etc.).  
   2) Then apply fuzzy key validation using `fuzzy_match_keys`.

.. class:: FuzzyValidateMappingParams

   Parameter model for the above function.


--------------------------
6) ``validate_boolean.py``
--------------------------
(*Already covered above.*)


-----------------------------
Usage Example: Fuzzy Key Matching
-----------------------------
Here's a minimal snippet showing how to fix up user-provided JSON 
with slight typos in keys:

.. code-block:: python

   from lionagi.libs.validate.fuzzy_match_keys import fuzzy_match_keys

   user_data = {
       "Namme": "Alice",
       "Agee": 30,
       "desc": "Test"
   }
   expected_keys = ["Name", "Age", "Description"]

   corrected = fuzzy_match_keys(
       user_data,
       expected_keys,
       similarity_threshold=0.8,
       fuzzy_match=True,
       handle_unmatched="remove"
   )

   print(corrected)  
   # might yield: {"Name": "Alice", "Age": 30} 
   # "desc" was removed as unmatched, "Name" was corrected from "Namme"


-----------------------------
Usage Example: Field Validators
-----------------------------
In a Pydantic model you can do:

.. code-block:: python

   from pydantic import BaseModel, field_validator
   from lionagi.libs.validate.common_field_validators import (
       validate_same_dtype_flat_list,
       validate_boolean_field
   )

   class MyModel(BaseModel):
       tags: list[str] = []
       is_active: bool = True

       @field_validator("tags", pre=True)
       def validate_tags(cls, v):
           return validate_same_dtype_flat_list(cls, v, str, dropna=True)

       @field_validator("is_active", pre=True)
       def validate_is_active(cls, v):
           return validate_boolean_field(cls, v, default=True)


-------------
Summary
-------------
The ``lionagi.libs.validate`` subpackage centralizes common validation tasks:

- **Convert** arbitrary data into booleans or dicts.
- **Fuzzy match** and correct dictionary keys (typos).
- **Distance metrics** for string similarity.
- **Pydantic**-friendly field validators.

This is especially handy in user-facing contexts where partial correctness 
(e.g. key spelling) or flexible data formatting must be accepted and 
normalized. 
