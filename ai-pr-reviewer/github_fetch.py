import os
import ollama

from github import Github, Auth
from dotenv import load_dotenv


# ---------- PROMPTS ----------

SECURITY_PROMPT = """
Review only security issues.
Focus on:
- secrets
- SQL injection
- auth
- unsafe execution
"""

QUALITY_PROMPT = """
Review only code quality.
Focus on:
- maintainability
- duplication
- readability
"""

PERFORMANCE_PROMPT = """
Review only performance.
Focus on:
- memory
- loops
- expensive operations
"""


# ---------- GITHUB ----------

load_dotenv()

token = os.getenv("GITHUB_TOKEN")

if not token:
    print("Token not found")
    exit()

auth = Auth.Token(token)

g = Github(auth=auth)


repo_name = input(
    "Enter repo (username/repo): "
)

repo = g.get_repo(repo_name)


review_folder = "github-review-output"

if not os.path.exists(review_folder):
    os.makedirs(review_folder)


agents = {
    "security": SECURITY_PROMPT,
    "quality": QUALITY_PROMPT,
    "performance": PERFORMANCE_PROMPT
}


print("\nRepository review started...\n")


contents = repo.get_contents("")


while contents:

    item = contents.pop(0)

    if item.type == "dir":

        contents.extend(
            repo.get_contents(item.path)
        )

        continue


    # REVIEW ONLY CODE FILES
    if not (
        item.path.endswith(".py")
        or item.path.endswith(".js")
        or item.path.endswith(".cpp")
        or item.path.endswith(".java")
    ):
        continue


    try:

        decoded = (
            item.decoded_content
            .decode("utf-8")
        )

    except:

        continue


    print(
        f"\nReviewing {item.path}"
    )

    review_text = ""


    for agent_name, prompt in agents.items():

        print(
            f"Running {agent_name}"
        )

        response = ollama.chat(
            model="qwen2.5-coder:3b",
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": decoded
                }
            ]
        )

        review_text += (
            f"\n\n========== "
            f"{agent_name.upper()} "
            f"==========\n\n"
        )

        review_text += (
            response["message"]["content"]
        )


    safe_name = (
        item.path
        .replace("/", "_")
    )


    output_file = os.path.join(
        review_folder,
        f"{safe_name}_review.txt"
    )


    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(review_text)


    print(
        f"Saved → {output_file}"
    )