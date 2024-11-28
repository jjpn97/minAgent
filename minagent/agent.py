import json
from asyncio import Semaphore
from typing import Literal

from openai import AsyncOpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage

from .tools import bash, python

BASH_FUNCTION = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Run commands in a bash shell.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to run in a bash shell.",
                }
            },
            "required": ["command"],
        },
    },
}

PYTHON_FUNCTION = {
    "type": "function",
    "function": {
        "name": "python",
        "description": "Run a Python script.",
        "parameters": {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "The path to the Python script to run, e.g ./script.py.",
                }
            },
            "required": ["script"],
        },
    },
}

TOOLS = [BASH_FUNCTION, PYTHON_FUNCTION]


name2tool = {
    "bash": bash,
    "python": python,
}


class Agent:
    MESSAGE_LIMIT = 5

    def __init__(
        self,
        container_name: str,
        system_prompt: str,
        model: str = "gpt-4o-mini",
        temperature: float = 1.0,
        tools: list[Literal["bash", "python"]] = ["bash", "python"],
        semaphore: Semaphore | None = None,
    ):
        self.model = model
        self.history = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]
        self.temperature = temperature
        self.messages = 0

        self.client = AsyncOpenAI()
        self.semaphore = semaphore or Semaphore(3)
        self.tools = [tool for tool in TOOLS if tool["function"]["name"] in tools]
        self.container = container_name

        self.bash_tool = bash(container_name)
        self.python_tool = python(container_name)

    async def get_response(self) -> ChatCompletionMessage:
        async with self.semaphore:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self.history,
                temperature=self.temperature,
                tools=self.tools,
                tool_choice="auto",
            )
            return response.choices[0].message

    async def step(self, response: ChatCompletionMessage) -> None:
        if response.tool_calls:
            tool_outputs = []
            for tool_call in response.tool_calls:
                self.history.append(
                    {
                        "role": "assistant",
                        "content": response.content,
                        "tool_calls": response.tool_calls,
                    }
                )

                tool_result = await self.execute_tool(
                    tool_call.function.name, json.loads(tool_call.function.arguments)
                )

                tool_outputs.append(
                    {"tool_call_id": tool_call.id, "output": tool_result}
                )

            # Add the assistant's response and tool outputs to the history
            self.history.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_outputs[0]["tool_call_id"],
                    "content": tool_outputs[0]["output"],
                }
            )
        else:
            self.history.append({"role": "assistant", "content": response.content})

    async def rollout(self, msg: str):
        self.history.append({"role": "user", "content": msg})

        while True:
            response = await self.get_response()
            await self.step(response)

            self.messages += 1
            if self.messages >= self.MESSAGE_LIMIT:
                break
        return self.history

    async def execute_tool(self, tool_name: str, tool_args: dict[str, str]) -> str:
        tool = name2tool[tool_name](self.container)
        print(f"Executing {tool_name}:", tool_args)
        async with self.semaphore:
            result = await tool(**tool_args)
            output = f"Output: \n{result}"
            return output
