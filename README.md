# Logan

Command-line log analyzer for Apache, JSON HTTP, Dnsmasq and Ulogd log files.
Runs on Python with Pixi for dependency management.

Reading raw log files to understand traffic patterns or debug issues is slow and error-prone.
Logan parses the file, aggregates the data and prints clean color-coded tables so patterns are immediately visible.

---

## How it works

Pass any log file to the CLI. Logan reads it line by line, automatically detects the format and routes each entry to the right parser.
Invalid or unrecognized lines are silently skipped.
At the end it prints aggregated tables via Rich.

### Apache / JSON HTTP logs

Status codes are color-coded by class (2xx green, 3xx blue, 4xx yellow, 5xx red).
Each row shows timestamp, status code and request latency in seconds.
Useful for spotting error spikes or slow requests at a glance.

### Dnsmasq DNS logs

Queries are grouped by day, then by source IP.
For each IP, the top 10 queried domains are listed with query count and percentage of that IP's total traffic.
Useful for identifying which devices are making the most DNS requests and what they are resolving.

### Ulogd connection logs

Only DESTROY events are considered, meaning completed connections.
Connections are grouped by day and source IP, showing the top 10 destination IPs with connection count, packets and bytes sent.
Useful for understanding outbound traffic patterns from each host on the network.

---

## Prerequisites

- **Pixi** — package manager: https://pixi.prefix.dev/latest/

---

## Installation

```bash
git clone https://github.com/Ra77a3l3-jar/logan.git
cd logan
pixi install
```

---

## Usage

```bash
pixi run python logan/cli.py <path-to-log>
```

Example:

```bash
pixi run python logan/cli.py sample_logs/access.log
```

Logan detects the format automatically. If no valid entries are found it exits with code 1.

---

## License

MIT License - Copyright (c) 2026 Raffaele Meo
