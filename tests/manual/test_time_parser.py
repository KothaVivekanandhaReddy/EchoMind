
from datetime import datetime
from zoneinfo import ZoneInfo

from echomind.time_parser import parse_time_range


india_tz = ZoneInfo("Asia/Kolkata")

# Monday, October 12, 2026, at noon in India.
fixed_now = datetime(
    2026, 10, 12, 12, 0,
    tzinfo=india_tz,
)

start, end = parse_time_range(
    "What did I promise to finish last week?",
    now=fixed_now,
)

assert start == "2026-10-04T18:30:00+00:00"
assert end == "2026-10-11T18:30:00+00:00"

# Queries without a recognized time phrase have no date restriction.
start_none, end_none = parse_time_range(
    "What did I promise to finish?",
    now=fixed_now,
)

assert start_none is None
assert end_none is None

# Naive datetimes are rejected to avoid ambiguous timezone handling.
try:
    parse_time_range(
        "last week",
        now=datetime(2026, 10, 12, 12, 0),
    )
except ValueError:
    pass
else:
    raise AssertionError("A naive datetime should be rejected.")

print("Time parser tests passed.")
