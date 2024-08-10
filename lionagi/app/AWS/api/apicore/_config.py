# from collections import defaultdict
# from yaml import safe_load
# from api.apiutils import _util_file as _util_file_


# class ConfigSingleton:
#     def __new__(cls, config_loc: str | None = None):
#         """
#         Create a new instance of the ConfigSingleton class if one doesn't already exist.
#         If an instance already exists, return the existing instance. This ensures that
#         there's only ever one instance of this class (singleton pattern). The configuration
#         can be initialized or updated from a specified file location if provided.

#         The configuration file is expected to be non-empty and in a format that can be
#         parsed by `safe_load`, such as YAML.

#         Args:
#             config_loc (str, optional): The path to the configuration file. If the file
#                 is specified and not empty, it will be used to update the configuration.
#                 Defaults to None, which means no configuration file will be loaded.

#         Returns:
#             ConfigSingleton: The singleton instance of the ConfigSingleton class.
#         """
#         if not hasattr(cls, "instance"):
#             cls.config = defaultdict(str)
#             cls.instance = super(ConfigSingleton, cls).__new__(cls)

#             if config_loc and not _util_file_.is_file_empty(config_loc):
#                 for name, val in safe_load(config_loc).items():
#                     cls.config[name] = val
#         return cls.instance
