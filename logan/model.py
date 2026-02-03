from dataclasses import dataclass
from datetime import datetime

@dataclass
class HttpEntry:
    timestamp: datetime
    status: int
    latency: int

@dataclass
class DNSEntry:
    timestamp: datetime
    qtype: str
    domain: str
    src_ip: str
    pid: int
