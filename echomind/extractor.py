
import re
from dataclasses import dataclass


REJECTION_PATTERNS = [
    # Explicit negation: do not turn a denial into a memory.
    re.compile(
        r"\bI\s+(?:didn't|did not|never|haven't|have not|"
        r"don't|do not|won't|will not|can't|cannot)\s+"
        r"(?:promise|promised|commit|committed|need|have|"
        r"decide|decided|prefer|want|plan|agree|agree to)\b",
        re.IGNORECASE,
    ),
    # Uncertain language should not become a firm commitment.
    re.compile(
        r"\b(?:I\s+)?(?:might|may|could|would)\s+"
        r"(?:possibly\s+)?(?:finish|complete|submit|deliver|"
        r"do|try|work|help|attend|call|send|build|ship)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:I\s+)?(?:hope|wish)\s+to\b|\bI'm\s+not\s+sure\b|"
        r"\bI am not sure\b|\bI don't know if\b|\bI do not know if\b",
        re.IGNORECASE,
    ),
]

@dataclass
class ExtractedMemory:
    memory_type: str
    content: str
    evidence: str
    confidence: float


# Each pattern must explicitly signal a memory type.
PATTERNS = [
    (
        "commitment",
        re.compile(
            r"\bI\s+(?:promised|committed)\s+to\s+(.+)",
            re.IGNORECASE,
        ),
        "I promised to",
    ),
    (
        "commitment",
        re.compile(
            r"\bI\s+will\s+(.+)",
            re.IGNORECASE,
        ),
        "I will",
    ),
    (
        "commitment",
        re.compile(
            r"\bI\s+(?:need|have)\s+to\s+(.+)",
            re.IGNORECASE,
        ),
        None,
    ),
    (
        "decision",
        re.compile(
            r"\bI\s+decided\s+to\s+(.+)",
            re.IGNORECASE,
        ),
        None,
    ),
    (
        "preference",
        re.compile(
            r"\bI\s+prefer\s+(.+)",
            re.IGNORECASE,
        ),
        None,
    ),
    (
        "goal",
        re.compile(
            r"\bmy\s+goal\s+is\s+to\s+(.+)",
            re.IGNORECASE,
        ),
        None,
    ),
]


def extract_memory(text: str) -> ExtractedMemory | None:
    """
    Extract one explicitly expressed memory from a short text.

    Returns None when no supported pattern matches.
    This is a rule-based prototype, not a general-purpose NLP model.
    """
    text = text.strip()

    if not text:
        return None
        # Reject negated or uncertain statements before applying extraction rules.
    if any(pattern.search(text) for pattern in REJECTION_PATTERNS):
        return None

    # Use the first sentence as the evidence unit for this prototype.
    sentence_match = re.search(r"[^.!?\n]+(?:[.!?]|$)", text)
    if not sentence_match:
        return None

    evidence = sentence_match.group().strip()

    for memory_type, pattern, _prefix in PATTERNS:
        match = pattern.search(evidence)

        if not match:
            continue

        content = match.group(1).strip().rstrip(".!?")
        content = re.sub(r"\s+", " ", content)

        if not content:
            return None

        return ExtractedMemory(
            memory_type=memory_type,
            content=content,
            evidence=evidence,
            confidence=0.95,
        )

    return None


def assess_memory_text(text: str) -> dict:
    """
    Decide whether text can be saved, needs confirmation, or should be ignored.
    """
    cleaned = text.strip()

    if not cleaned:
        return {
            "action": "ignore",
            "reason": "empty_input",
            "memory": None,
        }

    # Never turn an explicit denial or uncertain statement into a positive
    # memory, and don't ask for confirmation to save it as a positive fact.
    if any(pattern.search(cleaned) for pattern in REJECTION_PATTERNS):
        return {
            "action": "ignore",
            "reason": "negated_or_uncertain",
            "memory": None,
        }

    extracted = extract_memory(cleaned)

    if extracted is not None:
        return {
            "action": "save",
            "reason": "explicit_supported_statement",
            "memory": extracted,
        }

    # These phrases can indicate an intention, but do not establish a
    # definite commitment under our current extraction policy.
    ambiguous_patterns = [
        r"\bI\s+should\b",
        r"\bI\s+plan\s+to\b",
        r"\bI\s+intend\s+to\b",
        r"\bI\s+need\s+to\s+remember\s+to\b",
        r"\bI\s+think\s+I\s+(?:will|should|need\s+to)\b",
    ]

    if any(
        re.search(pattern, cleaned, re.IGNORECASE)
        for pattern in ambiguous_patterns
    ):
        return {
            "action": "confirm",
            "reason": "ambiguous_intention",
            "memory": None,
        }

    return {
        "action": "ignore",
        "reason": "no_supported_memory",
        "memory": None,
    }
