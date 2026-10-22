
from echomind.models import create_memory


memory = create_memory(
    memory_type="commitment",
    content="Finish the RAG evaluation project",
    source="input_001",
)

print(memory)
memory.validate()

print("\nMemory model test passed.")
