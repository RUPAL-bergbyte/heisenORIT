"""
base_agent.py

Shared base class for all reviewer agents (Security, Performance, Style, Final).
Uses the `ollama` python package directly -- same pattern already proven to
work in githubproject.py and github_fetch.py, so no new connection method
to debug.
"""

import ollama

MODEL_NAME = "qwen2.5-coder:3b"


def call_ollama(system_prompt: str, user_content: str, model: str = MODEL_NAME, temperature: float = 0.2) -> str:
    """
    Shared low-level call used by every agent (including the final merge
    agent, which doesn't review raw code but still needs to call the model).
    """
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            options={"temperature": temperature},
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return f"ERROR calling Ollama: {e}"


class BaseReviewAgent:
    """
    Subclass this and set `name` + `system_prompt` to create a new agent.
    """

    name: str = "BaseAgent"
    system_prompt: str = "You are a helpful code reviewer."

    def __init__(self, model: str = MODEL_NAME, temperature: float = 0.2):
        self.model = model
        self.temperature = temperature

    def build_user_prompt(self, filename: str, code: str) -> str:
        return (
            f"File: {filename}\n\n"
            f"Review the following code/diff. Be specific and reference "
            f"line content where possible. If you find nothing relevant "
            f"to your focus area, say so briefly instead of inventing issues.\n\n"
            f"```\n{code}\n```"
        )

    def review(self, filename: str, code: str) -> str:
        user_prompt = self.build_user_prompt(filename, code)
        result = call_ollama(self.system_prompt, user_prompt, self.model, self.temperature)
        if result.startswith("ERROR calling Ollama"):
            return f"[{self.name}] {result} -- is `ollama serve` running and is the model pulled?"
        return result