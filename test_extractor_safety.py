
from echomind.extractor import extract_memory


# Clear, explicit commitments should still be accepted.
result = extract_memory(
    "I promised to finish the RAG evaluation by Friday."
)
assert result is not None
assert result.memory_type == "commitment"

# Uncertainty must not be treated as a firm commitment.
assert extract_memory("I might finish the project.") is None
assert extract_memory("I could submit the report tomorrow.") is None
assert extract_memory("I hope to finish the project.") is None

# Explicit denials must not become positive memories.
assert extract_memory("I didn't promise to finish the project.") is None
assert extract_memory("I never promised to submit the report.") is None
assert extract_memory("I won't finish the project.") is None

# Supported non-commitment categories should still work.
result = extract_memory("I decided to use SQLite for storage.")
assert result is not None
assert result.memory_type == "decision"

result = extract_memory("I prefer concise answers.")
assert result is not None
assert result.memory_type == "preference"

print("Extractor safety tests passed.")
