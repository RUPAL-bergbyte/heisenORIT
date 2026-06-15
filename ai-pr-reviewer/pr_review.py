from github import Github, Auth
from dotenv import load_dotenv
import os


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

    print(
        file.filename
    )

    print(
        "\nPATCH:\n"
    )

    print(
        file.patch
    )

    print(
        "\n=================\n"
    )