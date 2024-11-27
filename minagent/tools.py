import asyncio
from dataclasses import dataclass


@dataclass
class ExecResult:
    exit_code: int | None
    stdout: str
    stderr: str


def bash(container_name: str = "agent_container", timeout: int | None = None):
    async def execute(command: str) -> str:
        full_cmd = f"cd $( cat ~/.last_dir ) >/dev/null; source ~/.last_env 2> /dev/null && {command}; pwd > ~/.last_dir; declare -p > ~/.last_env"  # stateful bash
        result = await _docker_exec(
            container_name=container_name,
            cmd=["bash", "-c", full_cmd],
            timeout=timeout,
        )

        output = ""
        if result.stderr:
            output = f"{result.stderr}\n"
        return f"{output}{result.stdout}"

    return execute


def python(container_name: str = "agent_container", timeout: int | None = None):
    async def execute(script: str) -> str:
        result = await _docker_exec(
            container_name=container_name,
            cmd=["python3", script],
            timeout=timeout,
        )

        output = ""
        if result.stderr:
            output = f"{result.stderr}\n"
        return f"{output}{result.stdout}"

    return execute


async def _docker_exec(
    container_name: str, cmd: list, timeout: int | None = 30
) -> ExecResult:
    """
    Execute a command in a running container using docker exec

    Args:
        container_name: Name/ID of the container
        cmd: Command to execute
        timeout: Optional timeout in seconds
    """
    docker_cmd = ["docker", "exec", "-i", container_name] + cmd

    try:
        process = await asyncio.create_subprocess_exec(
            docker_cmd[0],
            *docker_cmd[1:],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

        return ExecResult(
            exit_code=process.returncode,
            stdout=stdout.decode().strip(),
            stderr=stderr.decode().strip(),
        )

    except asyncio.TimeoutError:
        raise TimeoutError(f"Command timed out after {timeout} seconds")
