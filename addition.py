import asyncio

from minagent.agent import Agent
from minagent.environment import DockerEnvironment, Task
from minagent.tools import docker_exec


# Define task that determines whether we have AGI.
async def addition_score(agent: Agent) -> int:
    result = await docker_exec(agent.container, ["python3", "addition.py"])
    return 1 if "SUCCESS" in result.stdout else 0


task = Task(
    name="Addition",
    system_prompt="You are a helpful, harmless, and honest AI assistant.",
    task_prompt="Write a Python script called addition.py that performs simple addition. Check with one test case that the result is correct. I will run 'python addition.py' and check that 'SUCCESS' is printed.",
    score_fn=addition_score,
    tools=["bash", "python"],
)

CONCURRENT_AGENTS = 5

if __name__ == "__main__":
    env = DockerEnvironment()
    result = asyncio.run(
        env.run_task(
            task,
            model="gpt-4o-mini",
            agent_count=CONCURRENT_AGENTS,
            semaphore=asyncio.Semaphore(CONCURRENT_AGENTS),
        )
    )

    pass_rate = sum([r["score"] for r in result]) / len(result)
    print("AGI Achieved!" if pass_rate == 1 else "AGI Not Achieved.")
