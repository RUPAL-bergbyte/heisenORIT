# HeisenORIT

AI-powered PR Reviewer using Ollama and Qwen2.5-Coder.

The tool takes a code file as input and generates a detailed terminal-friendly review covering:

* Security issues
* Performance problems
* Code quality
* Maintainability
* Suggestions and fixes

---

## Requirements

* Python 3.x
* Ollama

---

## Install Ollama

Install Ollama from:

https://ollama.com

Pull the required model:

```bash
ollama pull qwen2.5-coder:3b
```

---

## Install Dependencies

```bash
pip install ollama
```

---

## Project Structure

```bash
.
├── ai-pr-reviewer
│   └── githubproject.py
├── demo test
│   └── test1.py
└── README.md
```

---

## Run

```bash
python ai-pr-reviewer/githubproject.py
```

---

## Usage

After running the script:

```bash
Enter code file path:
```

Example:

```bash
Enter code file path: demo test/test1.py
```

The AI reviewer will analyze the file and generate a structured review directly in the terminal.

---

## Model Used

```bash
qwen2.5-coder:3b
```