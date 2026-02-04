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

@dataclass
class UlogdEntry:
    timestamp: datetime
    hostname: str
    state: str
    src_ip_ori: str
    dest_ip_ori: str
    protocol_ori: str
    src_port_ori: int | None
    dest_port_ori: int | None
    type_ori: int | None
    code_ori: int | None
    pkts_ori: int
    bytes_ori: int
    src_ip_dest: str
    dest_ip_dest: str
    protocol_dest: str
    src_port_dest: int | None
    dest_port_dest: int | None
    type_dest: int | None
    code_dest: int | None
    pkts_dest: int
    bytes_dest: int
