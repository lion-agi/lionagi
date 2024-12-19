# Lion Coding Convention

1. names should be exported in folder.types module
2. only import to the module that needs it
3. only fill init if the folder is used very widely, utils, protocols
4. each class a file
5. each global utility a file
6. google style docstring
7. complex methods/functions should have interface params model (from lionagi.utils.params)
8. if importing from a file in same level, use relative import
9. if importing from a file in a lower level, use relative import
10. if importing from a file in a higher level, use absolute import (never more than one dot)
11. type hints is mandatory
12. python 3.11+ type hints and coding convention, no Union/Optional ...etc
13. pep-8, 79 chars per line and flake8
14. black, isort, and run pre-commit before commit
15. absolutely no extra dependencies unless explicitly approved
16. `__all__` should use `tuple` not `list`
17. only modules with many names should use `__all__`, if it's very clear what the module is for, don't use `__all__` within module, just export to folder.types
18. every public method should have a docstring, unless too simple and obvious
