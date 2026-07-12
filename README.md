# heisenORIT — AI Multi-Agent PR Reviewer

An AI pull request reviewer that doesn't just run one model over your diff — it runs **three specialized agents** (Security, Performance, Code Quality) independently, then has a **Final Review agent** merge their findings, flag trade-offs between them, and hand down one verdict. Runs entirely on a local model via [Ollama](https://ollama.com), orchestrated with [LangGraph](https://github.com/langchain-ai/langgraph).

```
                              PR ON GITHUB
                                   |
                         Fetch changed files
                                   |
                    Filter out non-source files
                     (.pyc, __pycache__, .gitignore,
                      binaries, lockfiles, etc.)
                                   |
              ┌────────────────────────────────────────┐
              |                    |                    |
        SECURITY AGENT     PERFORMANCE AGENT      STYLE AGENT
        (injection,        (loops, caching,       (naming, length,
         secrets, auth)     blocking I/O)          duplication)
              |                    |                    |
              └────────────────────────────────────────┘
                                   |
                          FINAL REVIEW AGENT
                    (merges, de-dupes, flags trade-offs,
                        issues APPROVE / REQUEST CHANGES)
                                   |
                       Posted back as a PR comment
```

## Why

Most AI PR reviewers are a single model with one long prompt trying to think about security, performance, and style all at once. Splitting that into independent specialist agents produces more focused findings per category, and the merge step catches something a single-pass reviewer can't: **when two concerns trade off against each other** (e.g. a performance fix that introduces a security risk), the Final Review agent calls it out explicitly instead of silently picking a side.

## Features

- 🔍 **Three independent reviewer agents** — Security, Performance, Code Quality/Style — each with a tightly scoped prompt so they don't step on each other's findings.
- 🧩 **LangGraph orchestration** — true parallel fan-out to the three agents, fan-in to a merge node.
- 🧹 **Smart file filtering** — only reviews real source files; automatically skips `.pyc`, `__pycache__`, `.gitignore`, lockfiles, and other non-review-worthy diffs.
- 🖥️ **Runs fully locally** — uses `qwen2.5-coder:3b` via Ollama, so no API keys or per-token costs for the AI itself.
- 💬 **Posts directly to GitHub** — the merged review is published as a PR comment via the GitHub API.

## Tech Stack

| Layer | Tool |
|---|---|
| LLM runtime | Ollama (`qwen2.5-coder:3b`) |
| Agent orchestration | LangGraph |
| GitHub integration | PyGithub |
| Language | Python 3.12 |

## Project Structure

```
heisenORIT/
│
├── ai-pr-reviewer/
│   ├── agents/
│   │   ├── base_agent.py        # shared Ollama-calling logic
│   │   ├── security_agent.py
│   │   ├── performance_agent.py
│   │   ├── style_agent.py
│   │   └── final_agent.py       # merges the three reviews
│   ├── orchestrator.py          # LangGraph wiring (fan-out / fan-in)
│   ├── file_filter.py           # source-file filtering
│   ├── github_fetch.py          # fetch PR + changed files
│   ├── github_post.py           # post the review as a PR comment
│   ├── pr_review.py             # entry point: runs the full pipeline
│   └── githubproject.py         # original single-agent CLI reviewer (kept for local file/folder reviews)
│
├── demo-test/                   # intentionally-flawed sample files used to demo the reviewer
│   ├── test1.py
│   └── test2.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup

**1. Install Ollama and pull the model**

```bash
# https://ollama.com
ollama pull qwen2.5-coder:3b
ollama serve
```

**2. Clone and install dependencies**

```bash
git clone https://github.com/RUPAL-bergbyte/heisenORIT.git
cd heisenORIT
python -m venv .venv
source .venv/bin/activate        # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements.txt
```

**3. Set up a GitHub token**

Create a `.env` file in the project root:

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

The token needs **`repo`** scope (classic PAT) or **Issues + Pull requests: Read & write** (fine-grained PAT) so it can post the review comment.

## Usage

**Review a PR and print the results:**

```bash
python ai-pr-reviewer/pr_review.py --repo owner/repo --pr 2
```

**Review a PR and post the merged review as a comment:**

```bash
python ai-pr-reviewer/pr_review.py --repo owner/repo --pr 2 --post
```

Or run it interactively — it'll prompt for the repo and PR number:

```bash
python ai-pr-reviewer/pr_review.py
```

**Review a single local file or folder** (original single-agent CLI, useful for quick local checks outside of a PR):

```bash
python ai-pr-reviewer/githubproject.py path/to/file.py
```

## Sample Output

Reviewing a file with hardcoded secrets and a SQL injection vulnerability:

```
--- demo-test/test1.py: SECURITY ---
- [HIGH] Hardcoded secret `API_KEY` in the code. Store secrets securely,
  e.g. using environment variables or a secure vault.
- [HIGH] Insecure use of `os.system()`. Use subprocess with proper
  argument handling instead of raw string concatenation.
- [MEDIUM] Missing input validation in `login()`. SQL query is built via
  f-string concatenation — vulnerable to injection.

=== FINAL MERGED REVIEW ===
Overall Verdict: REQUEST CHANGES
Address the hardcoded credentials and SQL injection risk before merge.
```

## Known Limitations

- **Diff size vs. model size.** `qwen2.5-coder:3b` is small and fast enough to run locally, but on very large diffs (e.g. an entire new file) it sometimes summarizes the code instead of producing structured findings. Smaller, focused diffs get the best results. A size-based skip threshold in `file_filter.py` can be tuned down if this becomes an issue.
- **Single review pass per agent.** Agents don't currently "debate" each other multi-turn — the Final Review agent does a single merge pass over their independent outputs.
- **No dashboard yet.** All output currently lives in the terminal, a local `review-output/` folder, and the GitHub PR comment.

## Roadmap

- [ ] Next.js dashboard for browsing review history and diffing agent opinions
- [ ] Multi-turn debate between agents before the final merge (not just one-shot)
- [ ] GitHub Action / webhook trigger so reviews run automatically on PR open
- [ ] Configurable severity thresholds for auto-approve vs. request-changes

## License

MIT (or update to match your project's actual license).