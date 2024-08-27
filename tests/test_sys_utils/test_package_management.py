import pytest
import subprocess
import importlib
import sys
from unittest.mock import patch, MagicMock
from lionagi.os.sys_utils import SysUtil

@pytest.fixture
def mock_subprocess_run():
    """Fixture to mock subprocess.run for pip command simulations."""
    with patch('subprocess.run') as mock_run:
        yield mock_run

@pytest.fixture
def mock_importlib():
    """Fixture to mock importlib for import simulations."""
    with patch('importlib.import_module') as mock_import:
        yield mock_import

@pytest.fixture
def mock_pkg_resources():
    """Fixture to mock pkg_resources for version checking."""
    with patch('pkg_resources.get_distribution') as mock_dist:
        yield mock_dist

@pytest.fixture
def mock_requests():
    """Fixture to mock requests for GitHub API calls."""
    with patch('requests.get') as mock_get:
        yield mock_get

def test_is_package_installed():
    """Test package installation check."""
    assert SysUtil.is_package_installed("pytest")
    assert not SysUtil.is_package_installed("non_existent_package_12345")

def test_import_module(mock_importlib):
    """Test module import functionality."""
    mock_importlib.return_value = MagicMock()
    
    # Test basic import
    SysUtil.import_module("test_package")
    mock_importlib.assert_called_with("test_package")
    
    # Test import with module name
    SysUtil.import_module("test_package", "test_module")
    mock_importlib.assert_called_with("test_package.test_module")
    
    # Test import with specific names
    SysUtil.import_module("test_package", "test_module", ["func1", "func2"])
    mock_importlib.assert_called_with("test_package.test_module", fromlist=["func1", "func2"])

def test_import_module_error(mock_importlib):
    """Test error handling in module import."""
    mock_importlib.side_effect = ImportError("Module not found")
    
    with pytest.raises(ImportError):
        SysUtil.import_module("non_existent_package")

@pytest.mark.parametrize("package_installed", [True, False])
def test_install_import(mock_subprocess_run, mock_importlib, package_installed):
    """Test install and import functionality."""
    mock_importlib.side_effect = [ImportError("Not installed")] if not package_installed else None
    
    SysUtil.install_import("test_package")
    
    if not package_installed:
        mock_subprocess_run.assert_called_once()
    mock_importlib.assert_called()

def test_install_import_with_version(mock_subprocess_run):
    """Test installation with specific version."""
    SysUtil.install_import("test_package", version="==1.0.0")
    mock_subprocess_run.assert_called_once_with(
        [sys.executable, "-m", "pip", "install", "test_package==1.0.0"],
        check=True,
        capture_output=True
    )

def test_install_import_with_extras(mock_subprocess_run):
    """Test installation with extras."""
    SysUtil.install_import("test_package", extras=["extra1", "extra2"])
    mock_subprocess_run.assert_called_once_with(
        [sys.executable, "-m", "pip", "install", "test_package[extra1,extra2]"],
        check=True,
        capture_output=True
    )

def test_install_import_editable(mock_subprocess_run):
    """Test editable installation."""
    SysUtil.install_import("test_package", editable=True)
    mock_subprocess_run.assert_called_once_with(
        [sys.executable, "-m", "pip", "install", "-e", "test_package"],
        check=True,
        capture_output=True
    )

def test_uninstall_package(mock_subprocess_run):
    """Test package uninstallation."""
    SysUtil.uninstall_package("test_package")
    mock_subprocess_run.assert_called_once_with(
        [sys.executable, "-m", "pip", "uninstall", "test_package", "-y"],
        check=True,
        capture_output=True
    )

def test_uninstall_package_error(mock_subprocess_run):
    """Test error handling in package uninstallation."""
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "pip uninstall")
    
    with pytest.raises(subprocess.CalledProcessError):
        SysUtil.uninstall_package("test_package")

def test_check_package_version(mock_pkg_resources):
    """Test package version checking."""
    mock_dist = MagicMock()
    mock_dist.version = "1.0.0"
    mock_pkg_resources.return_value = mock_dist
    
    meets_spec, installed_version = SysUtil.check_package_version("test_package", ">=1.0.0,<2.0.0")
    assert meets_spec
    assert installed_version == "1.0.0"
    
    meets_spec, installed_version = SysUtil.check_package_version("test_package", ">=2.0.0")
    assert not meets_spec
    assert installed_version == "1.0.0"

def test_check_package_version_not_installed(mock_pkg_resources):
    """Test version check for non-installed package."""
    mock_pkg_resources.side_effect = importlib.metadata.PackageNotFoundError
    
    meets_spec, installed_version = SysUtil.check_package_version("non_existent_package", ">=1.0.0")
    assert not meets_spec
    assert installed_version is None

def test_list_installed_packages():
    """Test listing of installed packages."""
    packages = SysUtil.list_installed_packages()
    assert isinstance(packages, list)
    assert len(packages) > 0
    assert all(isinstance(pkg, str) for pkg in packages)

    packages_with_version = SysUtil.list_installed_packages(include_version=True)
    assert all("==" in pkg for pkg in packages_with_version)

@pytest.mark.parametrize("repo_url, branch, expected_url", [
    ("https://github.com/user/repo", None, "git+https://github.com/user/repo"),
    ("user/repo", "dev", "git+https://github.com/user/repo@dev"),
    ("https://github.com/user/repo", "feature", "git+https://github.com/user/repo@feature"),
])
def test_install_from_github(mock_subprocess_run, mock_requests, repo_url, branch, expected_url):
    """Test installation from GitHub repository."""
    mock_requests.return_value.status_code = 200
    
    SysUtil.install_from_github(repo_url, branch=branch)
    
    mock_subprocess_run.assert_called_once_with(
        [sys.executable, "-m", "pip", "install", expected_url],
        check=True,
        capture_output=True
    )

def test_install_from_github_with_extras(mock_subprocess_run, mock_requests):
    """Test GitHub installation with extras."""
    mock_requests.return_value.status_code = 200
    
    SysUtil.install_from_github("user/repo", extras=["extra1", "extra2"])
    
    mock_subprocess_run.assert_called_once_with(
        [sys.executable, "-m", "pip", "install", "git+https://github.com/user/repo[extra1,extra2]"],
        check=True,
        capture_output=True
    )

def test_install_from_github_nonexistent_repo(mock_requests):
    """Test error handling for non-existent GitHub repository."""
    mock_requests.return_value.status_code = 404
    
    with pytest.raises(ValueError, match="Repository not found"):
        SysUtil.install_from_github("user/nonexistent-repo")

def test_install_from_github_nonexistent_branch(mock_requests):
    """Test error handling for non-existent branch in GitHub repository."""
    mock_requests.side_effect = [
        MagicMock(status_code=200),  # Repository exists
        MagicMock(status_code=404),  # Branch does not exist
    ]
    
    with pytest.raises(ValueError, match="Branch not found"):
        SysUtil.install_from_github("user/repo", branch="nonexistent-branch")

def test_check_github_branch(mock_requests):
    """Test GitHub branch existence check."""
    mock_requests.side_effect = [
        MagicMock(status_code=200),  # Repository exists
        MagicMock(status_code=200),  # Branch exists
    ]
    
    assert SysUtil.check_github_branch("user/repo", "main")
    
    mock_requests.side_effect = [
        MagicMock(status_code=200),  # Repository exists
        MagicMock(status_code=404),  # Branch does not exist
    ]
    
    assert not SysUtil.check_github_branch("user/repo", "nonexistent-branch")

def test_list_github_branches(mock_requests):
    """Test listing of GitHub repository branches."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"name": "main"},
        {"name": "dev"},
        {"name": "feature-branch"},
    ]
    mock_requests.return_value = mock_response
    
    branches = SysUtil.list_github_branches("user/repo")
    assert branches == ["main", "dev", "feature-branch"]

def test_list_github_branches_error(mock_requests):
    """Test error handling in GitHub branch listing."""
    mock_requests.return_value.status_code = 404
    
    with pytest.raises(ValueError, match="Failed to fetch branches"):
        SysUtil.list_github_branches("user/nonexistent-repo")