
from echomind.extractor import extract_memory


# Explicit commitment
result = extract_memory(
    "I promised to finish the RAG evaluation by Friday."
)
assert result is not None
assert result.memory_type == "commitment"
assert result.content == "finish the RAG evaluation by Friday"
assert result.evidence == (
    "I promised to finish the RAG evaluation by Friday."
)

# Decision
result = extract_memory("I decided to use SQLite for storage.")
assert result is not None
assert result.memory_type == "decision"
assert result.content == "use SQLite for storage"

# Preference
result = extract_memory("I prefer concise answers.")
assert result is not None
assert result.memory_type == "preference"

# Goal
result = extract_memory("My goal is to ship EchoMind.")
assert result is not None
assert result.memory_type == "goal"

# Unsupported or empty input should not be saved.
assert extract_memory("The weather is nice today.") is None
assert extract_memory("") is None

print("Memory extractor tests passed.")
