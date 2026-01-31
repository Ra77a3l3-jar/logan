from collections import defaultdict
from datetime import datetime
from model import LogEntry
from statistics import mean

# Retun a map of timestamps and the number of entries for the timestamp
def count_per_minute(entries: list[LogEntry]) -> dict[datetime, int]:
    count = defaultdict(int)

    for entry in entries:
        # Round the timestamp to start of the minute
        minute = entry.timestamp.replace(second=0, microsecond=0)
        count[minute] += 1

    return count

def avr_latency_per_minute(entries: list[LogEntry]) -> dict:
    count = {}

    for entry in entries:
        minute = entry.timestamp.replace(second=0, microsecond=0)

        if minute not in count:
            count[minute] = []

        count[minute].append(entry.latency)

    return {
        minute: round(mean(values), 2)
        for minute, values in count.items()
    }

def error_per_minute(entries: list[LogEntry]) -> dict:
    count = {}

    for entry in entries:
        minute = entry.timestamp.replace(second=0, microsecond=0)

        if minute not in count:
            count[minute] = {"total": 0, "errors": 0}

        count[minute]["total"] += 1

        if entry.status >= 500:
            count[minute]["errors"] += 1

    return {
        minute: round(data["errors"] / data["total"], 2)
        for minute, data in count.items()
    }
