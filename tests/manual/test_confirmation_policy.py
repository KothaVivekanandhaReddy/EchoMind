
from echomind.extractor import assess_memory_text


# Explicit statements can be saved.
result = assess_memory_text(
    "I promised to finish the RAG evaluation by Friday."
)
assert result["action"] == "save"
assert result["memory"].memory_type == "commitment"

# Ambiguous intentions require confirmation.
result = assess_memory_text("I should finish the project.")
assert result["action"] == "confirm"
assert result["reason"] == "ambiguous_intention"

result = assess_memory_text("I plan to submit the report.")
assert result["action"] == "confirm"

# Denial and uncertainty must not be saved as positive commitments.
result = assess_memory_text("I didn't promise to finish the project.")
assert result["action"] == "ignore"

result = assess_memory_text("I might finish the project.")
assert result["action"] == "ignore"

# Ordinary text is ignored.
result = assess_memory_text("The weather is nice today.")
assert result["action"] == "ignore"

# Empty input is ignored.
result = assess_memory_text("   ")
assert result["action"] == "ignore"
assert result["reason"] == "empty_input"

print("Confirmation policy tests passed.")
