

# SysUtil Class API Reference

The `SysUtil` class offers utility functions for managing package imports and installations programmatically, enhancing the flexibility and robustness of Python applications in handling dependencies.

## get_cpu_architecture

Returns the CPU architecture of the system, useful for determining compatibility, especially with binary packages.

### Usage

```python
cpu_architecture = SysUtil.get_cpu_architecture()
```

### Returns

- A string representing the CPU architecture (`"apple_silicon"` for ARM-based CPUs, `"other_cpu"` for all others).

## install_import

Attempts to import a module, installing the package via pip if the import fails.

### Usage

```python
SysUtil.install_import(package_name, module_name=None, import_name=None, pip_name=None)
```

### Parameters

- `package_name`: The name of the package to import.
- `module_name`: Optional; the module to import from the package.
- `import_name`: Optional; a specific attribute or class to import from the module/package.
- `pip_name`: Optional; the pip package name if different from `package_name`.

## is_package_installed

Checks if a package is installed.

### Usage

```python
is_installed = SysUtil.is_package_installed(package_name)
```

### Parameters

- `package_name`: The name of the package to check.

### Returns

- `True` if the package is installed, `False` otherwise.

## check_import

Checks if a package is installed and attempts to install it if not found.

### Usage

```python
SysUtil.check_import(package_name, module_name=None, import_name=None, pip_name=None)
```

### Parameters

- Same as `install_import`.

## list_installed_packages

Lists all installed packages in the environment.

### Usage

```python
installed_packages = SysUtil.list_installed_packages()
```

### Returns

- A list of installed package names.

## uninstall_package

Uninstalls a specified package.

### Usage

```python
SysUtil.uninstall_package(package_name)
```

### Parameters

- `package_name`: The name of the package to uninstall.

## update_package

Updates a specified package to the latest version.

### Usage

```python
SysUtil.update_package(package_name)
```

### Parameters

- `package_name`: The name of the package to update.

## Conclusion

The `SysUtil` class simplifies the dynamic management of Python packages, facilitating automatic installation, update, and verification of dependencies. This utility is particularly useful in developing applications that require flexibility in handling external libraries or in environments where dependencies need to be managed programmatically.
