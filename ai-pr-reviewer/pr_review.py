import ollama
import os

from github import Github, Auth
from dotenv import load_dotenv

load_dotenv()

token = os.getenv(
    "GITHUB_TOKEN"
)

auth = Auth.Token(token)

g = Github(
    auth=auth
)


repo_name = input(
    "Repo (owner/repo): "
)

pr_number = int(
    input(
        "PR Number: "
    )
)


repo = g.get_repo(
    repo_name
)

pr = repo.get_pull(
    pr_number
)

print(
    "\nChanged files:\n"
)


for file in pr.get_files():

    if not (
        file.filename.endswith(".py")
        or file.filename.endswith(".js")
        or file.filename.endswith(".cpp")
        or file.filename.endswith(".java")
    ):
        continue


    print(
        file.filename
    )

    if not file.patch:
        continue


    clean_patch = file.patch


ignore_words = [
    "PROMPT",
    "Review only",
    "Focus on:"
]


lines = []


for line in clean_patch.split("\n"):

    skip = False

    for word in ignore_words:

        if word in line:
            skip = True

    if not skip:
        lines.append(line)


clean_patch = "\n".join(lines)


if len(clean_patch) > 2500:

    clean_patch = clean_patch[:2500]


    if len(clean_patch) > 3000:

        clean_patch = (
            clean_patch[:3000]
        )


    print(
        "\nPATCH:\n"
    )

    print(
        clean_patch
    )


    print(
        "\n=================\n"
    )


    response = ollama.chat(

        model="qwen2.5-coder:3b",

        messages=[

            {
                "role": "system",

                "content": """
Review ONLY changed code.

Ignore:
- prompts
- generated files
- README
- comments

Focus on:
- bugs
- security
- quality
- performance
"""
            },

            {
                "role": "user",

                "content": clean_patch
            }

        ]
    )


    print(
        "\n========== REVIEW ==========\n"
    )


    print(
        response["message"]["content"]
    )