"""
file_filter.py

Fixes the "reviewer is reviewing junk files" bug.

Given a list of PR files (as returned by the GitHub API / github_fetch.py),
this module filters down to only real source-code files worth sending to
the AI reviewer agents.
"""

import os

# Extensions we consider "reviewable source code".
# Add to this list as your hackathon demo needs more languages.
ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".cpp", ".c", ".h", ".hpp",
    ".go", ".rs", ".rb", ".php",
    ".cs", ".swift", ".kt",
}

# Exact filenames to always ignore, regardless of extension.
IGNORED_FILENAMES = {
    ".gitignore",
    ".gitattributes",
    ".dockerignore",
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "Pipfile.lock",
}

# Path fragments — if any of these appear anywhere in the file's path,
# the file is skipped. Covers __pycache__, node_modules, build dirs, etc.
IGNORED_PATH_FRAGMENTS = {
    "__pycache__",
    "node_modules",
    ".venv",
    "venv/",
    "dist/",
    "build/",
    ".git/",
    ".pytest_cache",
    ".mypy_cache",
    "coverage/",
}

# Extensions that are always binary/compiled/non-reviewable.
IGNORED_EXTENSIONS = {
    ".pyc", ".pyo", ".pyd",
    ".so", ".dll", ".dylib", ".exe", ".o", ".a",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".pdf", ".zip", ".tar", ".gz", ".7z",
    ".lock",
    ".min.js", ".min.css",
    ".map",
}

# Safety cap: skip files that are absurdly large (usually generated/vendored
# code, or diffs so big the 3b model can't meaningfully review them anyway).
MAX_FILE_SIZE_BYTES = 200_000  # ~200KB of changed content


def _has_ignored_fragment(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(fragment in normalized for fragment in IGNORED_PATH_FRAGMENTS)


def is_reviewable_file(file_info: dict) -> bool:
    """
    file_info is expected to look like a GitHub API PR file entry, e.g.:
        {
            "filename": "ai-pr-reviewer/githubproject.py",
            "status": "modified",
            "additions": 12,
            "deletions": 3,
            "changes": 15,
            "patch": "...",
            ...
        }
    Returns True if this file should be sent to the AI reviewer agents.
    """
    filename = file_info.get("filename", "")
    if not filename:
        return False

    basename = os.path.basename(filename)
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    # Removed files have nothing to review.
    if file_info.get("status") == "removed":
        return False

    # Exact filename blocklist.
    if basename in IGNORED_FILENAMES:
        return False

    # Path-based blocklist (build artifacts, caches, deps).
    if _has_ignored_fragment(filename):
        return False

    # Explicit binary/compiled/generated extension blocklist.
    if ext in IGNORED_EXTENSIONS:
        return False

    # Must match a known source extension.
    if ext not in ALLOWED_EXTENSIONS:
        return False

    # Skip if the diff/patch is suspiciously huge.
    patch = file_info.get("patch", "") or ""
    if len(patch.encode("utf-8")) > MAX_FILE_SIZE_BYTES:
        return False

    return True


def filter_pr_files(files: list[dict]) -> list[dict]:
    """
    Takes the raw list of files from github_fetch.py and returns only the
    ones worth sending to the AI reviewers.
    """
    reviewable = [f for f in files if is_reviewable_file(f)]
    skipped = [f for f in files if f not in reviewable]

    if skipped:
        print(f"[file_filter] Skipping {len(skipped)} non-source file(s):")
        for f in skipped:
            print(f"   - {f.get('filename')}")

    if reviewable:
        print(f"[file_filter] {len(reviewable)} file(s) queued for review:")
        for f in reviewable:
            print(f"   - {f.get('filename')}")

    return reviewable


if __name__ == "__main__":
    # Quick manual test
    sample_files = [
        {"filename": ".gitignore", "status": "modified", "patch": "x"},
        {"filename": "ai-pr-reviewer/__pycache__/githubproject.cpython-312.pyc", "status": "added", "patch": "x"},
        {"filename": "ai-pr-reviewer/githubproject.py", "status": "modified", "patch": "def foo(): pass"},
        {"filename": "demo-test/test1.py", "status": "added", "patch": "print('hi')"},
    ]
    result = filter_pr_files(sample_files)
    assert len(result) == 2
    print("\nfile_filter.py self-test passed ✅")