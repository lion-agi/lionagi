=========================================
``libs.package`` Subpackage
=========================================

This subpackage provides utilities for **package management**—checking, installing, 
importing, and uninstalling Python packages at runtime. It is primarily 
used within LionAGI for dynamically ensuring dependencies are available. It also 
contains metadata retrieval for installed packages, CPU architecture detection, 
and more.



-------------------------
1) ``import_check.py``
-------------------------
.. module:: lionagi.libs.package.import_check
   :synopsis: Dynamic package import & installation

The main functionality here is to check if a package is installed, optionally install 
it if missing, then load it (similar to a dynamic “lazy import”).

**Key Functions**:

.. function:: check_import(package_name, module_name=None, import_name=None, pip_name=None, attempt_install=True, error_message="")

   Check if a package is installed. If not found and ``attempt_install=True``, 
   attempt to install it via pip (or `uv` if available). Once installed, the 
   package or module can be imported.  
   
   - **package_name**: The top-level package (e.g., "numpy").
   - **module_name**: If a submodule is needed (e.g., "linalg").
   - **import_name**: A symbol from the module to import (e.g., "inv" or ["inv", "det"]).
   - **pip_name**: The name used by pip if different from package_name (rare).
   - **attempt_install** (bool): Whether to try installing if missing.
   - **error_message**: Custom error message if not installed.

   Returns the imported module or symbol.

.. function:: import_module(package_name, module_name=None, import_name=None)

   A straightforward Python import, returning the specified module or symbol.

.. function:: install_import(package_name, module_name=None, import_name=None, pip_name=None)

   Attempt to import a package, installing it if not found. 
   Useful if you know the package is likely missing and want to do a direct install.

.. function:: is_import_installed(package_name) -> bool

   Check if importlib can find the given package.


----------------------------
2) ``list_uninstall_update.py``
----------------------------
.. module:: lionagi.libs.package.list_uninstall_update
   :synopsis: Listing, uninstalling, and updating packages

Utilities for enumerating installed packages, or removing/updating them.

**Key Functions**:

.. function:: list_installed_packages() -> list[str]

   Return a list of all installed package names, as reported by 
   :func:`importlib.metadata.distributions`.

.. function:: uninstall_package(package_name)

   Invoke pip/uv to remove a package with “uninstall -y”.

.. function:: update_package(package_name)

   Attempt to upgrade the package to the latest version with “install --upgrade”.


------------------------
3) ``schema.py``
------------------------
.. module:: lionagi.libs.package.schema
   :synopsis: Pydantic model for package import parameters

**Class**:

.. class:: PackageParams

   A Pydantic model that encapsulates parameters for specifying how to load 
   or install a Python package. This includes:

   - package_name (str)
   - module_name (str|None)
   - import_name (str|list[str]|None)
   - pip_name (str|None)

   Typically used in function calling contexts when you want to define a 
   schema for dynamic imports.


-------------------------
4) ``platform_info.py``
-------------------------
.. module:: lionagi.libs.package.platform_info
   :synopsis: CPU architecture detection

**Key Function**:

.. function:: get_cpu_architecture() -> str

   Check the system architecture (via `platform.machine()`). Returns `'arm64'` for 
   ARM-based systems, `'x86_64'` for Intel/AMD 64-bit, or the raw architecture 
   string if unrecognized.


----------------------
Basic Usage Example
----------------------
Below is a short demonstration of how you might use these tools to ensure 
a package is available, possibly installing it, and then import a symbol:

.. code-block:: python

   from lionagi.libs.package.import_check import check_import

   # Attempt to load 'requests', installing if missing
   requests_mod = check_import(
       package_name="requests",
       module_name=None,
       import_name=None,
       pip_name=None,
       attempt_install=True,
       error_message="Please install requests manually if you do not want auto-installation."
   )

   # Now we can use 'requests_mod' or just 'requests' 
   print(requests_mod.get("https://example.com"))

   # Or if we only want a specific symbol:
   session_class = check_import("requests", import_name="Session")
   s = session_class()
   s.get("https://example.com")


----------------------
Summary
----------------------
- **import_check.py**: Dynamically import and optionally install missing packages.
- **list_uninstall_update.py**: Utilities to list installed packages, uninstall, or 
  update them at runtime.
- **schema.py**: A Pydantic model describing parameters for package import logic.
- **platform_info.py**: Quick detection of CPU architecture (arm64 vs x86_64, etc.).

Together, these modules provide a safe and automated approach to 
dependency handling within LionAGI or other Python applications.
