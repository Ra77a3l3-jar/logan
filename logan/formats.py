from abc import ABC, abstractmethod
from model import LogEntry
import re
from datetime import datetime
import json


class BasicParser(ABC):
    @abstractmethod
    def match(self, line: str) -> bool:
        pass

    @abstractmethod
    def parse(self, line: str) -> LogEntry:
        pass


class ApacheParser(BasicParser):
    PATTERN = re.compile(
        r'\[(?P<time>.*?)\] '
        r'"(?P<method>\w+) (?P<path>.*?) HTTP/.*?" '
        r'(?P<status>\d{3}) .*? (?P<latency>\d+)ms'
    )

    def match(self, line: str) -> bool:
        return bool(self.PATTERN.search(line))

    def parse(self, line: str) -> LogEntry:
        match = self.PATTERN.search(line)

        if not match:
            raise ValueError("Error: not an apache log line")

        return LogEntry(
            timestamp=datetime.strptime(match["time"], "%d/%b/%Y:%H:%M:%S %z"),
            status=int(match["status"]),
            latency=int(match["latency"]),
        )

class JsonParser(BasicParser):
    def match(self, line: str) -> bool:
        return line.strip().startswith("{")

    def parse(self, line: str) -> LogEntry:
        data = json.loads(line)

        return LogEntry( # Will work only for a specific JSON formatting
            timestamp=datetime.fromisoformat(data["time"]),
            status=int(data["status"]),
            latency=int(data["latency"])
        )

PARSERS = [
    ApacheParser(),
    JsonParser(),
]

def parse_line(line: str) -> LogEntry:
    for parser in PARSERS:
        if parser.match(line):
            return parser.parse(line)

    raise ValueError("Error: unknown format")
