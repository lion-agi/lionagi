# from lionagi.libs.ln_convert import is_same_dtype
# from collections.abc import Mapping, Generator


# def validate_keys(keys):
#     """
#     choices can be provided from various sources:
#     - mapping such as dict, their keys will be used as choices
#     - iterables including list, tuple, set, generator, enum, etc.
#     - strings, comma separated values
#     """

#     try:
#         if isinstance(keys, Mapping):
#             keys = list(keys.keys())

#         elif isinstance(keys, (list, tuple, set, Generator)):
#             keys = set(keys)

#         elif isinstance(keys, str):
#             if "," in keys:
#                 keys = list({i.strip() for i in keys.split(",")})
#             else:
#                 keys = [keys.strip()]

#         else:
#             keys = [i.value for i in keys]

#     except Exception as e:
#         raise ValueError(f"invalid choices {keys}") from e

#     if not is_same_dtype(keys):
#         raise ValueError(f"choices must be of the same type, got {keys}")

#     return keys
