"""
github_post.py

Posts the AI-generated combined review back to GitHub as a PR comment,
using PyGithub (same library/auth pattern as github_fetch.py) instead of
raw REST calls.
"""

from github_fetch import get_pr


def post_review_comment(repo_name: str, pr_number: int, body: str):
    """
    repo_name: "owner/repo", e.g. "RUPAL-bergbyte/heisenORIT"
    pr_number: the PR number
    body: Markdown text of the comment
    """
    pr = get_pr(repo_name, pr_number)
    comment = pr.create_issue_comment(body)
    return comment


if __name__ == "__main__":
    # Manual smoke test -- adjust repo/pr number, make sure GITHUB_TOKEN
    # is set in your .env first.
    comment = post_review_comment(
        repo_name="RUPAL-bergbyte/heisenORIT",
        pr_number=2,
        body="Test comment from github_post.py -- safe to delete.",
    )
    print("Posted comment:", comment.html_url)