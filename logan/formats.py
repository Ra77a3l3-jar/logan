from abc import ABC, abstractmethod
from model import (
    LogEntry,
    DNSEntry,
)
import re
from datetime import datetime
import json
from typing import Generic, TypeVar

T = TypeVar("T")


class BasicParser(ABC, Generic[T]):
    @abstractmethod
    def match(self, line: str) -> bool:
        pass

    @abstractmethod
    def parse(self, line: str) -> T:
        pass


class ApacheParser(BasicParser[LogEntry]):
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

class DnsmasqParser(BasicParser[DNSEntry]):
    PATTERN= re.compile(
        r"""
        ^(?P<time>
            [A-Z][a-z]{2}\s+
            \d{1,2}\s+
            \d{2}:\d{2}:\d{2}
        )\s+
        dnsmasq
        \[(?P<pid>\d+)\]:
        \s+query\[
            (?:
                (?P<qtype>[A-Z]+)
                |
                type=(?P<qtype_num>\d+)
            )
        \]\s+
        (?P<name>[A-Za-z0-9._\-]+)
        \s+from\s+
        (?P<src_ip>\d{1,3}(?:\.\d{1,3}){3})
        $
        """,
        re.VERBOSE
    )

    def match(self, line: str) -> bool:
        return bool(self.PATTERN.match(line))

    def parse(self, line: str) -> DNSEntry:
        match = self.PATTERN.match(line)
        if not match:
            raise ValueError("Not a dnsmasq log line")

        # Normalize DNS type
        if match["qtype"]:
            qtype = match["qtype"]
        else:
            raw_type = int(match["qtype_num"])
            qtype = f"TYPE{raw_type}"

        ts = datetime.strptime(match["time"], "%b %d %H:%M:%S")
        ts = ts.replace(year=datetime.now().year)

        return DNSEntry(
            timestamp=ts,
            qtype=qtype,
            domain=match["name"],
            src_ip=match["src_ip"],
            pid=int(match["pid"]),
        )
   

class JsonParser(BasicParser[LogEntry]):
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
    DnsmasqParser(),
]

def parse_line(line: str) -> LogEntry | DNSEntry:
    for parser in PARSERS:
        if parser.match(line):
            return parser.parse(line)

    raise ValueError("Error: unknown format")
