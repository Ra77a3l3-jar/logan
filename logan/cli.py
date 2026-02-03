from model import (
    HttpEntry,
    DNSEntry,
)
from formats import parse_line
from rich.console import Console
import typer
from display import (
    displayDnsEntries,
    displayHttpEntries,
)

app = typer.Typer()
console = Console()

@app.command()
def main(file: str):

    logEntries: list[HttpEntry] = []
    dnsEntries: list[DNSEntry] = []

    with open(file) as f:
        for line in f:
            try:
                entry = parse_line(line)
                if isinstance(entry, HttpEntry):
                    logEntries.append(entry)
                    if 100 <= entry.status < 600:
                        pass
                    else:
                        raise ValueError(f"Invalid HTTP status code: {entry.status}")
                elif isinstance(entry, DNSEntry):
                    dnsEntries.append(entry)
            except ValueError:
                pass

    # Display HTTP log analysis
    if logEntries:
        displayHttpEntries(logEntries)

    # Display DNS log analysis
    if dnsEntries:
        displayDnsEntries(dnsEntries)

    if not logEntries and not dnsEntries:
        print("No valid log entries found")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
