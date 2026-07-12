"""
github_fetch.py

Reusable GitHub PR fetching, built on PyGithub — same auth pattern you
already had working in your repo-scanner version of this file and in
pr_review.py (dotenv + Auth.Token).

This replaces the ad-hoc inline PyGithub calls that used to live directly
inside pr_review.py with one importable function, so pr_review.py, tests,
and the orchestrator can all reuse it.
"""

import os
from github import Github, Auth
from dotenv import load_dotenv

load_dotenv()


def _get_github_client() -> Github:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN not found. Add it to your .env file, e.g.\n"
            "GITHUB_TOKEN=ghp_xxxxxxxxxxxx"
        )
    auth = Auth.Token(token)
    return Github(auth=auth)


def get_pr_files(repo_name: str, pr_number: int) -> list[dict]:
    """
    Fetches the changed files for a PR and returns them as plain dicts
    (rather than PyGithub File objects) so file_filter.py and the
    orchestrator don't need to know about PyGithub at all.

    repo_name: "owner/repo", e.g. "RUPAL-bergbyte/heisenORIT"
    pr_number: PR number, e.g. 2

    Each dict looks like:
        {
            "filename": "ai-pr-reviewer/githubproject.py",
            "status": "modified",
            "additions": 12,
            "deletions": 3,
            "changes": 15,
            "patch": "@@ -1,4 +1,6 @@ ...",
        }
    """
    g = _get_github_client()

    print(f"Trying repo: {repo_name}")
    repo = g.get_repo(repo_name.strip())
    print(f"Repo found: {repo.full_name}")

    print(f"Trying PR: {pr_number}")
    pr = repo.get_pull(pr_number)
    print(f"PR found: {pr.title}")

    files = []
    for f in pr.get_files():
        files.append({
            "filename": f.filename,
            "status": f.status,
            "additions": f.additions,
            "deletions": f.deletions,
            "changes": f.changes,
            # f.patch can be None for binary files or files GitHub
            # doesn't generate a text diff for.
            "patch": f.patch or "",
        })

    return files


def get_pr(repo_name: str, pr_number: int):
    """
    Returns the raw PyGithub PullRequest object, for cases (like posting
    a review comment) where you need the live object rather than a dict.
    """
    g = _get_github_client()
    repo = g.get_repo(repo_name.strip())
    return repo.get_pull(pr_number)


if __name__ == "__main__":
    # Interactive smoke test, same UX as your original scripts.
    repo_name = input("Repo (owner/repo): ")
    pr_number = int(input("PR Number: "))

    files = get_pr_files(repo_name, pr_number)
    print(f"\nChanged files ({len(files)}):")
    for f in files:
        print(f"  - {f['filename']} ({f['status']}, +{f['additions']}/-{f['deletions']})")