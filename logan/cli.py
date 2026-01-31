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

    logEntries = []

    with open(file) as f:
        for line in f:
            entry = parse_line(line)
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

    if not logEntries:
        console.print("[red]No valid log entries found[/red]")
        raise typer.Exit(code=1)

    table = Table(title="Log Analyzer")

    table.add_column("Minute", style="cyan")
    table.add_column("Requests", style="green", justify="right")
    table.add_column("Avr latency (ms)", style="green", justify="right")
    table.add_column("Error rate", style="red", justify="right")

    each_min = count_per_minute(logEntries)
    lat_min = avr_latency_per_minute(logEntries)
    err_min = error_per_minute(logEntries)

    for minute in sorted(each_min):
        table.add_row(
            str(minute),
            str(each_min.get(minute, 0)),
            str(lat_min.get(minute, 0)),
            str(err_min.get(minute, 0)),
        )

    console.print(table)

    print("-"*20)
    print(f"Informational code: {informational}")
    print(f"Successful codes: {successful}")
    print(f"Redirection codes: {redirection}")
    print(f"Client error codes: {clientError}")
    print(f"Server error codes: {serverError}")


if __name__ == "__main__":
    app()
