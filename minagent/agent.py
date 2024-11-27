# pyright: ignore-file -- Using dict format for OpenAI messages which is valid but causes type errors

import subprocess
from openai import OpenAI

from openai.types.chat.chat_completion_message import ChatCompletionMessage


class Agent:
    MESSAGE_LIMIT = 10

    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 1.0):
        self.model = model
        self.history = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Use 'ls' and then stop.",
            }
        ]
        self.temperature = temperature
        self.messages = 0

        self.client = OpenAI()

    def get_response(self) -> ChatCompletionMessage:
        response = self.client.chat.completions.create(
            model=self.model, messages=self.history, temperature=self.temperature
        )
        return response.choices[0].message

    def reply(self, msg: str):
        self.history.append({"role": "user", "content": msg})
        while True:
            response = self.get_response()
            self.history.append(response)
            if "<bash>" in response.content:
                self.execute(response.content)
            else:
                return response.content

            self.messages += 1
            if self.messages >= self.MESSAGE_LIMIT:
                break

    def execute(self, response_str: str):
        """Execute the command in the response and add the output to the history"""
        cmd = response_str.split("<bash>")[1].split("</bash>")[0]
        print("Executing:", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = f"Output: \n{result.stdout}"
        if result.stderr:
            output += f"\nError captured:\n{result.stderr}"
        print("Output", output)
        self.history.append({"role": "user", "content": output})


if __name__ == "__main__":
    agent = Agent()
    agent.reply("Complete the task.")
