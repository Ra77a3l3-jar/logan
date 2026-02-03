from abc import ABC, abstractmethod
from model import (
    UlogdEntry,
    HttpEntry,
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


class ApacheParser(BasicParser[HttpEntry]):
    PATTERN = re.compile(
        r'\[(?P<time>.*?)\] '
        r'"(?P<method>\w+) (?P<path>.*?) HTTP/.*?" '
        r'(?P<status>\d{3}) .*? (?P<latency>\d+)ms'
    )

    def match(self, line: str) -> bool:
        return bool(self.PATTERN.search(line))

    def parse(self, line: str) -> HttpEntry:
        match = self.PATTERN.search(line)

        if not match:
            raise ValueError("Error: not an apache log line")

        return HttpEntry(
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

class UlogdParser(BasicParser[UlogdEntry]):
    PATTERN = re.compile(
        r"""
        ^(?P<month>\S{3})\s+
        (?P<day>\d{1,2})\s+
        (?P<time>\d{2}:\d{2}:\d{2})\s+
        (?P<hostname>\S+)\s+
        \[(?P<state>\w+)\]\s+
        ORIG:\s+
        SRC=(?P<src_ip_ori>\S+)\s+
        DST=(?P<dest_ip_ori>\S+)\s+
        PROTO=(?P<protocol_ori>\S+)\s+
        SPT=(?P<src_port_ori>\d+)\s+
        DPT=(?P<dest_port_ori>\d+)\s+
        PKTS=(?P<pkts_ori>\d+)\s+
        BYTES=(?P<bytes_ori>\d+)\s*,\s*
        REPLY:\s+
        SRC=(?P<src_ip_dest>\S+)\s+
        DST=(?P<dest_ip_dest>\S+)\s+
        PROTO=(?P<protocol_dest>\S+)\s+
        SPT=(?P<src_port_dest>\d+)\s+
        DPT=(?P<dest_port_dest>\d+)\s+
        PKTS=(?P<pkts_dest>\d+)\s+
        BYTES=(?P<bytes_dest>\d+)$
        """,
        re.VERBOSE
    )

    def match(self, line: str) -> bool:
        return bool(self.PATTERN.match(line))

    def parse(self, line: str) -> UlogdEntry:
        match = self.PATTERN.match(line)

        if not match:
            raise ValueError("Not a ulogd log file")

        gd = match.groupdict()

        timestamp = datetime.strptime(f"{gd['month']} {gd['day']} {gd['time']}", "%b %d %H:%M:%S")

        return UlogdEntry(
            timestamp=timestamp,
            hostname=gd["hostname"],
            state=gd["state"],
            src_ip_ori=gd["src_ip_ori"],
            dest_ip_ori=gd["dest_ip_ori"],
            protocol_ori=gd["protocol_ori"],
            src_port_ori=int(gd["src_port_ori"]),
            dest_port_ori=int(gd["dest_port_ori"]),
            pkts_ori=int(gd["pkts_ori"]),
            bytes_ori=int(gd["bytes_ori"]),
            src_ip_dest=gd["src_ip_dest"],
            dest_ip_dest=gd["dest_ip_dest"],
            protocol_dest=gd["protocol_dest"],
            src_port_dest=int(gd["src_port_dest"]),
            dest_port_dest=int(gd["dest_port_dest"]),
            pkts_dest=int(gd["pkts_dest"]),
            bytes_dest=int(gd["bytes_dest"]),
        )

class JsonParser(BasicParser[HttpEntry]):
    def match(self, line: str) -> bool:
        return line.strip().startswith("{")

    def parse(self, line: str) -> HttpEntry:
        data = json.loads(line)

        return HttpEntry( # Will work only for a specific JSON formatting
            timestamp=datetime.fromisoformat(data["time"]),
            status=int(data["status"]),
            latency=int(data["latency"])
        )

PARSERS = [
    ApacheParser(),
    JsonParser(),
    DnsmasqParser(),
    UlogdParser(),
]

def parse_line(line: str) -> HttpEntry | DNSEntry | UlogdEntry:
    for parser in PARSERS:
        if parser.match(line):
            return parser.parse(line)

    raise ValueError("Error: unknown format")
