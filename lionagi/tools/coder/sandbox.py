"""
Secure code execution environments.
Provides local and container-based sandboxes.
"""

import asyncio
import os
import shutil
import signal
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import psutil
from pydantic import BaseModel, Field

from .base import Sandbox, SandboxConfig, SandboxError


class LocalSandboxConfig(SandboxConfig):
    """
    Configuration for local sandbox.

    Attributes:
        temp_dir: Temporary directory path
        cleanup_temp: Whether to cleanup temp files
        inherit_env: Environment variables to inherit
        nice: Process nice value
    """

    temp_dir: Optional[str] = Field(
        None, description="Temporary directory path"
    )
    cleanup_temp: bool = Field(True, description="Cleanup temp files")
    inherit_env: Set[str] = Field(
        default_factory=set, description="Environment variables to inherit"
    )
    nice: Optional[int] = Field(None, description="Process nice value")


class LocalSandbox(Sandbox):
    """
    Local process-based sandbox.

    Features:
    - Process isolation
    - Resource limits
    - Environment control
    - Temporary directory management
    """

    def __init__(self, config: LocalSandboxConfig):
        super().__init__(config)
        self.config: LocalSandboxConfig = config
        self._temp_dir: Optional[Path] = None
        self._processes: Set[psutil.Process] = set()

    async def _setup_impl(self) -> None:
        """Setup local sandbox."""
        # Create temporary directory
        if self.config.temp_dir:
            self._temp_dir = Path(self.config.temp_dir)
            self._temp_dir.mkdir(parents=True, exist_ok=True)
        else:
            self._temp_dir = Path(tempfile.mkdtemp())

        # Set working directory
        if not self.config.working_dir:
            self.config.working_dir = str(self._temp_dir)

    async def _cleanup_impl(self) -> None:
        """Cleanup local sandbox."""
        # Terminate any running processes
        for proc in self._processes:
            try:
                proc.terminate()
            except psutil.NoSuchProcess:
                pass

        # Wait for processes to exit
        if self._processes:
            psutil.wait_procs(self._processes, timeout=5)

            # Force kill any remaining processes
            for proc in self._processes:
                try:
                    proc.kill()
                except psutil.NoSuchProcess:
                    pass

        self._processes.clear()

        # Cleanup temporary directory
        if self._temp_dir and self.config.cleanup_temp:
            try:
                shutil.rmtree(self._temp_dir)
            except OSError:
                pass

    async def _run_command_impl(
        self, command: str, env: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Run command in local sandbox.

        Args:
            command: Command to execute
            env: Environment variables

        Returns:
            Dict with stdout, stderr, and exit code
        """
        # Prepare environment
        cmd_env = os.environ.copy() if self.config.inherit_env else {}
        cmd_env.update(env)

        # Create process
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=cmd_env,
            cwd=self.config.working_dir,
            preexec_fn=self._setup_process,
        )

        # Track process
        self._processes.add(psutil.Process(process.pid))

        try:
            # Wait for completion
            stdout, stderr = await process.communicate()

            return {
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "exit_code": process.returncode,
            }

        finally:
            # Cleanup process
            try:
                self._processes.remove(psutil.Process(process.pid))
            except (psutil.NoSuchProcess, KeyError):
                pass

    def _setup_process(self):
        """Setup process limits and isolation."""
        # Set nice value
        if self.config.nice is not None:
            os.nice(self.config.nice)

        # Set memory limit
        if self.config.max_memory:
            import resource

            mem_bytes = self.config.max_memory * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))


class ContainerConfig(SandboxConfig):
    """
    Configuration for container sandbox.

    Attributes:
        image: Container image name
        platform: Container platform
        network: Network access type
        volumes: Volume mounts
        capabilities: Container capabilities
    """

    image: str = Field(..., description="Container image")
    platform: str = Field("linux/amd64", description="Container platform")
    network: str = Field("none", description="Network access")
    volumes: Dict[str, Dict[str, str]] = Field(
        default_factory=dict, description="Volume mounts"
    )
    capabilities: Set[str] = Field(
        default_factory=set, description="Container capabilities"
    )


class ContainerSandbox(Sandbox):
    """
    Container-based sandbox using Docker/Podman.

    Features:
    - Container isolation
    - Network controls
    - Volume mounting
    - Resource limits
    """

    def __init__(self, config: ContainerConfig):
        super().__init__(config)
        self.config: ContainerConfig = config
        self._container_id: Optional[str] = None
        self._temp_dir: Optional[Path] = None

    async def _setup_impl(self) -> None:
        """Setup container sandbox."""
        try:
            import docker
        except ImportError:
            raise SandboxError("Docker SDK required for container sandbox")

        # Create client
        self._client = docker.from_env()

        # Create temporary directory
        self._temp_dir = Path(tempfile.mkdtemp())

        # Create container
        container = self._client.containers.run(
            self.config.image,
            command="tail -f /dev/null",  # Keep container running
            detach=True,
            platform=self.config.platform,
            network_mode=self.config.network,
            volumes=self.config.volumes,
            working_dir=self.config.working_dir,
            cap_drop="ALL",
            cap_add=list(self.config.capabilities),
            mem_limit=f"{self.config.max_memory}m",
            environment=self.config.env,
        )

        self._container_id = container.id

    async def _cleanup_impl(self) -> None:
        """Cleanup container sandbox."""
        if self._container_id:
            try:
                container = self._client.containers.get(self._container_id)
                container.remove(force=True)
            except:
                pass
            self._container_id = None

        # Cleanup temporary directory
        if self._temp_dir:
            try:
                shutil.rmtree(self._temp_dir)
            except OSError:
                pass
            self._temp_dir = None

    async def _run_command_impl(
        self, command: str, env: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Run command in container sandbox.

        Args:
            command: Command to execute
            env: Environment variables

        Returns:
            Dict with stdout, stderr, and exit code
        """
        if not self._container_id:
            raise SandboxError("Container not initialized")

        try:
            container = self._client.containers.get(self._container_id)
            result = container.exec_run(
                command,
                environment=env,
                workdir=self.config.working_dir,
            )

            return {
                "stdout": result.output.decode(),
                "stderr": "",
                "exit_code": result.exit_code,
            }

        except Exception as e:
            raise SandboxError(f"Container command failed: {e}")


# Register available sandbox implementations
SANDBOX_TYPES = {"local": LocalSandbox, "container": ContainerSandbox}


def create_sandbox(
    type: str, config: Union[LocalSandboxConfig, ContainerConfig]
) -> Sandbox:
    """
    Create sandbox instance.

    Args:
        type: Sandbox type
        config: Sandbox configuration

    Returns:
        Configured sandbox instance
    """
    if type not in SANDBOX_TYPES:
        raise ValueError(f"Unknown sandbox type: {type}")

    sandbox_class = SANDBOX_TYPES[type]
    return sandbox_class(config)
