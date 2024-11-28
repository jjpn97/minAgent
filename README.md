# minAgent

A minimal framework for evaluating LLM agents in isolated Docker environments with concurrent execution.

## Overview

minAgent provides Docker containers with (interactive) Bash and Python for testing LLM agents on simple tasks. It uses async/await for efficient concurrent evaluation and is based on [UK AISI's Inspect framework](https://github.com/UKGovernmentBEIS/inspect_ai).

This was mainly for my understanding of (some of) UK AISI's codebase, particularly Docker.

## Example (addition.py)

Evaluates a model on a simple task using 5 Docker containers at once.

```python
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
            task, model="gpt-4o-mini", agent_count=CONCURRENT_AGENTS, semaphore=asyncio.Semaphore(CONCURRENT_AGENTS)
        )
    )

    pass_rate = sum([r["score"] for r in result]) / len(result)
    print("AGI Achieved!" if pass_rate == 1 else "AGI Not Achieved.")
```

### agent.py

A basic GPT agent with access to Bash and Python tools. The agent is assigned a Docker container with working directory `~/home/agent`. Tool calls are handled using OpenAI's function-calling API.

### environment.py

`DockerEnvironment` handles Docker image creation (details of which are in `docker/Dockerfile`) container handling (startup, cleanup), and the running of tasks on these containers. 

### tools.py

Functions for asynchronous execution of commands on Docker containers.

### TODO:

- [ ] More sophisticated environment setup (i.e. define agent's directory)
- [ ] Support non-GPT models
- [ ] Basic agent improvements: finish command, scaffolding, e.g. ReAct
- [ ] API backoffs
- [ ] Storage of agent rollouts and scores
- [ ] Write tests
- [ ] Sanity checking parts of implementation and cleanup
