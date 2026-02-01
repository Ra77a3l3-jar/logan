from parser import (
    extract_status,
    extract_time,
    extract_latency
)
from stats import (
    count_per_minute,
    avr_latency_per_minute,
    error_per_minute
)
from model import (
    LogEntry,
    DNSEntry,
)
from formats import parse_line
from rich.console import Console
from rich.table import Table
import typer

app = typer.Typer()
console = Console()

@app.command()
def main(file: str):
    
    informational = 0
    successful = 0
    redirection = 0
    clientError = 0
    serverError = 0

    logEntries: list[LogEntry | DNSEntry] = []

    with open(file) as f:
        for line in f:
            entry = parse_line(line)
            if isinstance(entry, LogEntry):
                try:
                    logEntries.append(entry)
                except ValueError:
                    pass
                if 100 <= entry.status < 200:
                    informational += 1
                elif 200 <= entry.status < 300:
                    successful += 1
                elif 300 <= entry.status < 400:
                    redirection += 1
                elif 400 <= entry.status < 500:
                    clientError += 1
                elif 500 <= entry.status < 600:
                    serverError += 1
                else:
                    raise ValueError(f"Invalid HTTP status code: {entry.status}")
            elif isinstance(entry, DNSEntry):
                # TODO
                # Number of connections to a destination from ip(Devide by subNet) and how frequently
                pass


if __name__ == "__main__":
    app()
