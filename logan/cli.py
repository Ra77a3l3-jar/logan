from model import (
    HttpEntry,
    DNSEntry,
    UlogdEntry,
)
from formats import parse_line
from rich.console import Console
import typer
from display import (
    displayDnsEntries,
    displayHttpEntries,
    displayUlogdEntries,
)

app = typer.Typer()
console = Console()

@app.command()
def main(file: str):

    logEntries: list[HttpEntry] = []
    dnsEntries: list[DNSEntry] = []
    ulogdEntries: list[UlogdEntry] = []

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
                elif isinstance(entry, UlogdEntry):
                    ulogdEntries.append(entry)
            except ValueError:
                pass

    # Display HTTP log analysis
    if logEntries:
        displayHttpEntries(logEntries)

    # Display DNS log analysis
    if dnsEntries:
        displayDnsEntries(dnsEntries)

    # Display Ulogd log analysis
    if ulogdEntries:
        displayUlogdEntries(ulogdEntries)

    if not logEntries and not dnsEntries and not ulogdEntries:
        print("No valid log entries found")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
