# class APIObjectSingleton:
#     object_registration = {}

#     def __new__(cls):
#         if not hasattr(cls, "instance"):
#             cls.instance = super(APIObjectSingleton, cls).__new__(cls)
#         return cls.instance


# class APIObjectMeta(type):
#     def __new__(cls, class_name, bases, attrs):
#         """
#         A metaclass for automatically registering API object classes in a central registry.

#         Upon the creation of a new class that uses `APIObjectMeta` as its metaclass, this metaclass
#         intercepts the class creation process. It inspects the class attributes, looking for a specific
#         naming pattern (`APIObject` prefix in the class' `__qualname__`). If such a pattern is found,
#         the class is registered with its name (excluding the `APIObject` prefix) in a singleton registry.
#         This allows for centralized management and easy access to all API object classes defined in the
#         application.

#         Args:
#             class_name (str): The name of the class being created.
#             bases (tuple): A tuple containing the base classes of the class being created.
#             attrs (dict): A dictionary of attributes and methods defined on the class.

#         Returns:
#             type: The newly created class, now registered in the API object registry if it matches the
#                   naming criteria.
#         """
#         object_register = APIObjectSingleton()
#         new_attrs, object_name, orig_object_name = {}, None, None
#         for attr_name, attr_value in attrs.items():
#             new_attrs[attr_name] = attr_value
#             if attr_name == "__qualname__" and attr_value.startswith("APIObject"):
#                 object_name = attr_value[len("APIObject") :]
#                 orig_object_name = attr_value

#         obj = type(class_name, bases, new_attrs)
#         if object_name:
#             object_register.object_registration[object_name] = {
#                 "object_name": orig_object_name,
#                 "object_ptr": obj,
#             }
#         return object
