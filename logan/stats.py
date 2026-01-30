from collections import defaultdict
from datetime import datetime
from model import LogEntry

# Retun a map of timestamps and the number of entries for the timestamp
def count_per_minute(entries: list[LogEntry]) -> dict[datetime, int]:
    count = defaultdict(int)

    for entry in entries:
        # Round the timestamp to start of the minute
        minute = entry.timestamp.replace(second=0, microsecond=0)
        count[minute] += 1

    return count
