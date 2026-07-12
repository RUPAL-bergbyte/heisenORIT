"""
pr_review.py

Full end-to-end pipeline:

    GitHub PR
        |
    Fetch changed files          (github_fetch.py)
        |
    Filter to real source files  (file_filter.py)
        |
    Security / Performance / Style agents in parallel   (orchestrator.py)
        |
    Merge into final review      (orchestrator.py -> FinalReviewAgent)
        |
    Print + optionally post back to GitHub   (github_post.py)

Run interactively (same UX as your original scripts):
    python pr_review.py

Or non-interactively:
    python pr_review.py --repo RUPAL-bergbyte/heisenORIT --pr 2
    python pr_review.py --repo RUPAL-bergbyte/heisenORIT --pr 2 --post
"""

import argparse

from github_fetch import get_pr_files
from file_filter import filter_pr_files
from orchestrator import review_file
from github_post import post_review_comment

OUTPUT_FOLDER = "review-output"


def run_pipeline(repo_name: str, pr_number: int, post: bool = False):
    print(f"\nFetching PR #{pr_number} from {repo_name}...")
    files = get_pr_files(repo_name, pr_number)
    print(f"Found {len(files)} total file(s) in PR.")

    reviewable_files = filter_pr_files(files)
    if not reviewable_files:
        print("\nNo reviewable source files found in this PR. Nothing to do.")
        return

    all_final_reviews = []

    for f in reviewable_files:
        filename = f["filename"]
        # "patch" is the unified diff GitHub gives per file. Reviewing the
        # diff (not the full file) keeps prompts small enough for the 3b
        # model and matches what a human reviewer looks at on a PR anyway.
        code = f.get("patch", "")
        if not code:
            print(f"Skipping {filename}: no diff content available (binary or too large).")
            continue

        print(f"\nReviewing {filename}...")
        result = review_file(filename, code)

        print(f"\n--- {filename}: SECURITY ---\n{result['security_review']}")
        print(f"\n--- {filename}: PERFORMANCE ---\n{result['performance_review']}")
        print(f"\n--- {filename}: STYLE ---\n{result['style_review']}")
        print(f"\n=== {filename}: FINAL MERGED REVIEW ===\n{result['final_review']}")

        all_final_reviews.append((filename, result["final_review"]))

    combined_body = build_combined_comment(all_final_reviews)
    save_local_copy(repo_name, pr_number, combined_body)

    if post:
        print("\nPosting combined review to GitHub...")
        comment = post_review_comment(repo_name, pr_number, combined_body)
        print(f"Done: {comment.html_url}")
    else:
        print("\n(Run with --post to publish this review as a PR comment.)")


def build_combined_comment(all_final_reviews: list[tuple[str, str]]) -> str:
    """
    Combines all per-file final reviews into one Markdown comment body,
    suitable for posting as a single PR comment.
    """
    header = (
        "## AI Multi-Agent PR Review\n\n"
        "Reviewed by Security, Performance, and Style agents, "
        "merged by a Final Review agent.\n"
    )
    sections = [header]
    for filename, review in all_final_reviews:
        sections.append(f"\n---\n### `{filename}`\n\n{review}\n")
    return "\n".join(sections)


def save_local_copy(repo_name: str, pr_number: int, body: str):
    import os
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    safe_name = repo_name.replace("/", "_")
    output_path = os.path.join(OUTPUT_FOLDER, f"{safe_name}_pr{pr_number}_review.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"\nSaved local copy -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI multi-agent PR reviewer")
    parser.add_argument("--repo", help="e.g. RUPAL-bergbyte/heisenORIT")
    parser.add_argument("--pr", type=int, help="PR number")
    parser.add_argument("--post", action="store_true", help="Post the final review back to GitHub")
    args = parser.parse_args()

    repo_name = args.repo or input("Repo (owner/repo): ")
    pr_number = args.pr or int(input("PR Number: "))

    run_pipeline(repo_name, pr_number, post=args.post)