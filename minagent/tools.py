import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable


@dataclass
class ExecResult:
    success: bool
    exit_code: int | None
    stdout: str
    stderr: str


def bash(
    container_name: str = "agent_container", timeout: int | None = None
) -> Callable[[str], Awaitable[str]]:
    async def execute(command: str) -> str:
        full_cmd = f"cd $( cat ~/.last_dir ) >/dev/null; source ~/.last_env 2> /dev/null && {command}; pwd > ~/.last_dir; declare -p > ~/.last_env"  # stateful bash
        result = await docker_exec(
            container_name=container_name,
            cmd=["bash", "-c", full_cmd],
            timeout=timeout,
        )

        output = ""
        if result.stderr:
            output = f"{result.stderr}\n"
        return f"{output}{result.stdout}"

    return execute


def python(
    container_name: str = "agent_container", timeout: int | None = None
) -> Callable[[str], Awaitable[str]]:
    async def execute(script: str) -> str:
        result = await docker_exec(
            container_name=container_name,
            cmd=["python3", script],
            timeout=timeout,
        )

        output = ""
        if result.stderr:
            output = f"{result.stderr}\n"
        return f"{output}{result.stdout}"

    return execute


async def docker_subprocess_exec(cmd: list, timeout: int | None = 30) -> ExecResult:
    """
    Execute a docker command using asyncio subprocess

    Args:
        container_name: Name/ID of the container
        cmd: Command to execute
        timeout: Optional timeout in seconds
    """

    try:
        process = await asyncio.create_subprocess_exec(
            "docker",
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

        return ExecResult(
            success=(process.returncode == 0),
            exit_code=process.returncode,
            stdout=stdout.decode().strip(),
            stderr=stderr.decode().strip(),
        )

    except asyncio.TimeoutError:
        raise TimeoutError(f"Command timed out after {timeout} seconds")


async def docker_exec(
    container_name: str, cmd: list, timeout: int | None = 30
) -> ExecResult:
    """
    Execute a command in a running container using docker exec

    Args:
        container_name: Name/ID of the container
        cmd: Command to execute
        timeout: Optional timeout in seconds
    """
    docker_cmd = ["exec", "-i", container_name] + cmd
    result = await docker_subprocess_exec(docker_cmd, timeout=timeout)
    return result
