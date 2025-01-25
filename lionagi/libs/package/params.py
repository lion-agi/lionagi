# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field


class PackageParams(BaseModel):
    """Configuration for package import and installation operations.

    This model defines parameters used by package management functions to handle
    importing and installing Python packages with support for specific module
    and name imports.
    """

    package_name: str = Field(
        description="The name of the package to import or install"
    )
    module_name: str | None = Field(
        default=None,
        description="The specific module to import from the package (e.g., 'submodule')",
    )
    import_name: str | list[str] | None = Field(
        default=None,
        description="The specific name(s) to import from the module (e.g., 'ClassName' or ['Class1', 'Class2'])",
    )
    pip_name: str | None = Field(
        default=None,
        description="The package name to use for pip installation if different from package_name",
    )
