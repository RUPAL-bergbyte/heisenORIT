import ollama

# Step 1: Ask user for file path
file_path = input("Enter code file path: ")

# Step 2: Read file content
with open(file_path, "r", encoding="utf-8") as file:
    code_to_review = file.read()

# Step 3: Hidden system prompt
SYSTEM_PROMPT = """
You are an elite software engineer and code reviewer.

Review the given code for:
- Bugs
- Security issues
- Performance issues
- Bad practices
- Maintainability

Give structured feedback with severity levels.
"""

# Step 4: Send code to Ollama
response = ollama.chat(
    model='qwen2.5-coder:3b',
    messages=[
        {
            'role': 'system',
            'content': SYSTEM_PROMPT
        },
        {
            'role': 'user',
            'content': code_to_review
        }
    ]
)

# Step 5: Print review
print("\n========== AI CODE REVIEW ==========\n")
print(response['message']['content'])