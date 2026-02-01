from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class LogEntry:
    timestamp: datetime
    status: int
    latency: int

@dataclass
class DNSEntry:
    timestamp: datetime
    qtype: str
    name: str
    src_ip: str
    pid: int
