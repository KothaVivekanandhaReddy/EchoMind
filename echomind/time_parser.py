
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


DEFAULT_TIMEZONE = "Asia/Kolkata"


def parse_time_range(
    query: str,
    now: datetime | None = None,
    timezone_name: str = DEFAULT_TIMEZONE,
) -> tuple[str | None, str | None]:
    """
    Return an inclusive start and exclusive end as ISO timestamps.

    Supported phrase: 'last week', meaning the previous calendar week
    from Monday 00:00 up to, but not including, this Monday 00:00.
    """
    local_tz = ZoneInfo(timezone_name)

    if now is None:
        now = datetime.now(local_tz)
    elif now.tzinfo is None:
        raise ValueError("'now' must be timezone-aware.")
    else:
        now = now.astimezone(local_tz)

    normalized_query = query.casefold()

    if "last week" not in normalized_query:
        return None, None

    this_monday = now.date() - timedelta(days=now.weekday())
    last_monday = this_monday - timedelta(days=7)

    start = datetime.combine(
        last_monday,
        time.min,
        tzinfo=local_tz,
    )
    end = datetime.combine(
        this_monday,
        time.min,
        tzinfo=local_tz,
    )

    return (
        start.astimezone(timezone.utc).isoformat(),
        end.astimezone(timezone.utc).isoformat(),
    )
