# # %%
# from dataclasses import dataclass


# @dataclass
# class Task:
#     name: str
#     system_prompt: str
#     task_prompt: str
#     tools: list[str]


# task = Task(
#     name="dontcare",
#     system_prompt="You are a helpful, harmless, and honest AI assistant.",
#     task_prompt="Write a Python script called addition.py that performs simple addition. Check with one test case that the result is correct. I will run 'python addition.py' and check that 'SUCCESS' is printed.",
#     tools=["bash", "python"],
# )

# # Build image and start agent's Docker container
# from docker_manager import DockerManager

# container_manager = DockerManager()
# container_manager.build_image()
# container_manager.start_container()

# # %%
# from agent import Agent

# container_manager.start_container()
# # %%

# agent = Agent(container_manager.container.name, task.system_prompt, tools=task.tools)

# print(agent.tools)
# # %%

# agent.history
# # %%
# await agent.rollout(task.task_prompt)

# # %%
# print(agent.history)

# container_manager.stop_and_remove_container()
# # %%
