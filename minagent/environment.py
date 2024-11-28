import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

from .agent import Agent
from .tools import ExecResult, docker_subprocess_exec


@dataclass
class Task:
    name: str
    system_prompt: str
    task_prompt: str
    score_fn: Callable
    tools: list[Literal["bash", "python"]]


async def docker_compose(cmd: list[str], timeout: int | None = None) -> ExecResult:
    """Run a Docker Compose command."""
    compose_cmd = ["compose"] + cmd
    result = await docker_subprocess_exec(compose_cmd, timeout=timeout)
    return result


class DockerEnvironment:
    def __init__(self, compose_file: str | None = None):
        self.compose_file = compose_file or str(
            Path(__file__).parent.parent / "docker" / "docker-compose.yml"
        )

    async def run_task(
        self, task: Task, model: str, agent_count: int, semaphore: asyncio.Semaphore
    ) -> list[dict]:
        try:
            # build the image (docker uses caching so should be fast)
            await self.build_image()

            # create containers of this image
            await self.start_agent_containers(agent_count)

            container_names = await self.get_container_names()

            self.agents = [
                Agent(
                    container,
                    task.system_prompt,
                    model,
                    tools=task.tools,
                    semaphore=semaphore,
                )
                for container in container_names
            ]

            rollout_tasks = [agent.rollout(task.task_prompt) for agent in self.agents]
            rollouts = await asyncio.gather(*rollout_tasks, return_exceptions=True)

            score_tasks = [task.score_fn(agent) for agent in self.agents]
            rollout_scores = await asyncio.gather(*score_tasks, return_exceptions=True)

            return [
                {"agent": agent, "score": score, "rollout": rollout}
                for agent, score, rollout in zip(self.agents, rollout_scores, rollouts)
            ]

        finally:
            await self.stop_agent_containers()

    async def build_image(self) -> ExecResult:
        cmd = ["-f", self.compose_file, "build"]
        result = await docker_compose(cmd)
        return result

    async def start_agent_containers(
        self, count: int = 1, timeout: int | None = None
    ) -> ExecResult:
        cmd = [
            "-f",
            self.compose_file,
            "up",
            "-d",
            "--wait",
            "--scale",
            f"agent={count}",
        ]
        result = await docker_compose(cmd, timeout=timeout)
        return result

    async def stop_agent_containers(self, timeout: int | None = None) -> ExecResult:
        cmd = ["-f", self.compose_file, "down"]
        result = await docker_compose(cmd, timeout=timeout)
        return result

    async def get_container_names(self) -> list[str]:
        cmd = ["-f", self.compose_file, "ps", "--format", "{{.Name}}"]
        result = await docker_compose(cmd)
        return result.stdout.splitlines()
