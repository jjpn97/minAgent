import asyncio
from typing import Optional


class ExecResult:
    def __init__(self, success: bool, stdout: str, stderr: str):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr

    def __repr__(self):
        return f"ExecResult(success={self.success}, stdout={self.stdout}, stderr={self.stderr})"


async def docker_exec(
    container_name: str, cmd: list, timeout: Optional[int] = 30
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
            success=(process.returncode == 0),
            stdout=stdout.decode().strip(),
            stderr=stderr.decode().strip(),
        )

    except asyncio.TimeoutError:
        raise TimeoutError(f"Command timed out after {timeout} seconds")


def bash(timeout: int | None = None):
    async def execute(cmd: str) -> str:
        full_cmd = f" cd $( cat ~/.last_dir ) >/dev/null; source ~/.last_env 2> /dev/null && {cmd}; pwd > ~/.last_dir; declare -p > ~/.last_env"  # stateful bash
        result = await docker_exec(
            container_name="agent_container",
            cmd=["bash", "-c", full_cmd],
            timeout=timeout,
        )
        # return output (including stderr if any)
        output = ""
        if result.stderr:
            output = f"{result.stderr}\n"
        return f"{output}{result.stdout}"

    return execute


def python(timeout: int | None = None):
    async def execute(code: str) -> str:
        result = await docker_exec(
            container_name="agent_container",
            cmd=["python3"],
            timeout=timeout,
        )
        # return output (including stderr if any)
        output = ""
        if result.stderr:
            output = f"{result.stderr}\n"
        return f"{output}{result.stdout}"

    return execute


if __name__ == "__main__":
    pass
