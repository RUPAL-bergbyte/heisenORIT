from github import Github
from dotenv import load_dotenv
import os


load_dotenv()

token = os.getenv("GITHUB_TOKEN")

if not token:
    print("Token not found")
    exit()


from github import Github, Auth

auth = Auth.Token(token)
g = Github(auth=auth)


repo_name = input(
    "Enter repo (username/repo): "
)

repo = g.get_repo(repo_name)


print("\nRepository files:\n")


contents = repo.get_contents("")


while contents:

    item = contents.pop(0)

    if item.type == "dir":

        contents.extend(
            repo.get_contents(
                item.path
            )
        )

    else:

        decoded = (
    item.decoded_content
    .decode("utf-8")
)

print("\n================")
print(item.path)
print("================")

print(
    decoded[:500]
)