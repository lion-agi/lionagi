import pytest
import platform
import subprocess
from unittest.mock import patch, MagicMock
from lionagi.os.sys_utils import SysUtil

@pytest.fixture
def mock_platform_system():
    """Fixture to mock platform.system() for different OS tests."""
    with patch('platform.system') as mock_system:
        yield mock_system

@pytest.fixture
def mock_subprocess_check_output():
    """Fixture to mock subprocess.check_output for command simulations."""
    with patch('subprocess.check_output') as mock_output:
        yield mock_output

def test_get_cpu_architecture_basic():
    """Test basic functionality of get_cpu_architecture method."""
    arch_info = SysUtil.get_cpu_architecture()
    
    assert isinstance(arch_info, dict)
    assert 'machine' in arch_info
    assert 'processor' in arch_info
    assert 'architecture' in arch_info
    assert 'system' in arch_info
    assert 'python_bits' in arch_info
    assert 'is_arm' in arch_info

def test_get_cpu_architecture_consistency():
    """Test consistency of get_cpu_architecture with platform module."""
    arch_info = SysUtil.get_cpu_architecture()
    
    assert arch_info['machine'] == platform.machine()
    assert arch_info['processor'] == platform.processor()
    assert arch_info['architecture'] == platform.architecture()
    assert arch_info['system'] == platform.system()

def test_get_cpu_architecture_arm_detection():
    """Test ARM architecture detection."""
    with patch('platform.machine', return_value='aarch64'):
        arch_info = SysUtil.get_cpu_architecture()
        assert arch_info['is_arm'] == True

    with patch('platform.machine', return_value='x86_64'):
        arch_info = SysUtil.get_cpu_architecture()
        assert arch_info['is_arm'] == False

@pytest.mark.parametrize("system", ["Darwin", "Linux", "Windows"])
def test_get_cpu_architecture_os_specific(mock_platform_system, system):
    """Test OS-specific information gathering."""
    mock_platform_system.return_value = system
    
    with patch.object(SysUtil, f'_get_{system.lower()}_cpu_info', return_value={"test_key": "test_value"}):
        arch_info = SysUtil.get_cpu_architecture()
        assert "test_key" in arch_info
        assert arch_info["test_key"] == "test_value"

def test_get_macos_cpu_info(mock_subprocess_check_output):
    """Test MacOS CPU info gathering."""
    mock_subprocess_check_output.side_effect = [
        b"Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz\n",
        b"GenuineIntel\n",
        b"6\n",
        b"158\n"
    ]
    
    info = SysUtil._get_macos_cpu_info()
    
    assert info['brand'] == "Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz"
    assert info['vendor'] == "GenuineIntel"
    assert info['physical_cores'] == "6"
    assert info['model'] == "158"

def test_get_linux_cpu_info():
    """Test Linux CPU info gathering."""
    mock_cpuinfo = """
processor       : 0
model name      : AMD Ryzen 7 3700X 8-Core Processor
physical id     : 0
cores           : 8
    """
    
    with patch('builtins.open', MagicMock(return_value=MagicMock(read=MagicMock(return_value=mock_cpuinfo)))):
        with patch('os.cpu_count', return_value=8):
            info = SysUtil._get_linux_cpu_info()
    
    assert info['brand'] == "AMD Ryzen 7 3700X 8-Core Processor"
    assert info['physical_cores'] == 8

def test_get_windows_cpu_info(mock_subprocess_check_output):
    """Test Windows CPU info gathering."""
    mock_subprocess_check_output.return_value = b"Name=Intel(R) Core(TM) i5-10400F CPU @ 2.90GHz\n"
    
    with patch('os.cpu_count', return_value=6):
        info = SysUtil._get_windows_cpu_info()
    
    assert info['brand'] == "Intel(R) Core(TM) i5-10400F CPU @ 2.90GHz"
    assert info['physical_cores'] == "6"

def test_get_cpu_architecture_error_handling(mock_platform_system, mock_subprocess_check_output):
    """Test error handling in CPU info gathering."""
    mock_platform_system.return_value = "Darwin"  # Test with macOS
    mock_subprocess_check_output.side_effect = subprocess.CalledProcessError(1, "sysctl")
    
    info = SysUtil._get_macos_cpu_info()
    assert "error" in info
    assert "Failed to retrieve macOS CPU info" in info["error"]

@pytest.mark.parametrize("machine,expected", [
    ("arm64", True),
    ("aarch64", True),
    ("armv7l", True),
    ("x86_64", False),
    ("amd64", False),
])
def test_is_arm_detection(machine, expected):
    """Test ARM architecture detection for various machine types."""
    with patch('platform.machine', return_value=machine):
        arch_info = SysUtil.get_cpu_architecture()
        assert arch_info['is_arm'] == expected

def test_get_cpu_architecture_python_bits():
    """Test Python bits detection."""
    arch_info = SysUtil.get_cpu_architecture()
    assert arch_info['python_bits'] in ['32bit', '64bit']
    assert arch_info['python_bits'] == platform.architecture()[0]

@pytest.mark.parametrize("system", ["Darwin", "Linux", "Windows"])
def test_cpu_info_method_called(mock_platform_system, system):
    """Test that the correct OS-specific method is called."""
    mock_platform_system.return_value = system
    method_name = f'_get_{system.lower()}_cpu_info'
    
    with patch.object(SysUtil, method_name, return_value={}) as mock_method:
        SysUtil.get_cpu_architecture()
        mock_method.assert_called_once()

def test_get_cpu_architecture_unknown_os(mock_platform_system):
    """Test behavior with an unknown operating system."""
    mock_platform_system.return_value = "UnknownOS"
    
    arch_info = SysUtil.get_cpu_architecture()
    assert all(key in arch_info for key in ['machine', 'processor', 'architecture', 'system', 'python_bits', 'is_arm'])
    assert 'brand' not in arch_info
    assert 'vendor' not in arch_info
    assert 'physical_cores' not in arch_info