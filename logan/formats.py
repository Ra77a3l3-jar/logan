from abc import ABC, abstractmethod
from model import LogEntry
import re
from datetime import datetime


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
