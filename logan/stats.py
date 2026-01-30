from collections import defaultdict
from datetime import datetime

# Round the timestamp to start of the minute
def minute_bucket(ts: datetime) -> datetime:
    return ts.replace(second=0, microsecond=0)

# Retun a map of timestamps and the number of entries for the timestamp
def count_per_minute(timestamp: list[datetime]) -> dict[datetime, int]:
    count = defaultdict(int)

    for ts in timestamp:
        count[minute_bucket(ts)] += 1

    return count
