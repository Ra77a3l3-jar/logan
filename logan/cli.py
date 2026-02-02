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
from collections import defaultdict
from datetime import datetime

app = typer.Typer()
console = Console()

@app.command()
def main(file: str):
    
    informational = 0
    successful = 0
    redirection = 0
    clientError = 0
    serverError = 0

    logEntries: list[LogEntry] = []
    dnsEntries: list[DNSEntry] = []

    with open(file) as f:
        for line in f:
            try:
                entry = parse_line(line)
                if isinstance(entry, LogEntry):
                    logEntries.append(entry)
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
                    dnsEntries.append(entry)
            except ValueError:
                pass

    # Display HTTP log analysis
    if logEntries:
        table = Table(title="HTTP Log Analyzer")

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
        print()

    # Display DNS log analysis
    if dnsEntries:
        # day -> ip -> domain -> count
        # Number of queries that ip made to domain on day
        day_ip_domain_queries = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        # day -> ip -> total count
        # Total number of queries made by ip on a given day
        day_ip_total = defaultdict(lambda: defaultdict(int))

        for entry in dnsEntries:
            day_key = entry.timestamp.date()
            day_ip_domain_queries[day_key][entry.src_ip][entry.domain] += 1
            day_ip_total[day_key][entry.src_ip] += 1

        TOP_DOMAINS_PER_IP = 10

        # Iterate through each day
        for day in sorted(day_ip_domain_queries.keys()):
            console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
            console.print(f"[bold cyan]{day.strftime('%B %d, %Y')}[/bold cyan]")
            console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")

            # Get IPs for this day sorted by total queries
            ips_for_day = sorted(
                day_ip_total[day].keys(),
                key=lambda x: day_ip_total[day][x],
                reverse=True
            )

            # Create a table for each IP on this day
            for ip in ips_for_day:
                table = Table(title=f"IP: {ip}", header_style="bold magenta")

                table.add_column("Domain", style="yellow")
                table.add_column("Queries", style="green", justify="right")
                table.add_column("% of IP's Connections", style="cyan", justify="right")

                total_queries_for_ip = day_ip_total[day][ip]

                # Get top domains for this IP on this day
                domains = sorted(
                    day_ip_domain_queries[day][ip].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:TOP_DOMAINS_PER_IP]

                # Calculate percentage in day
                for domain, count in domains:
                    percentage_total_queries = (count / total_queries_for_ip) * 100
                    table.add_row(domain, str(count), f"{percentage_total_queries:.1f}%")

                console.print(table)
                console.print(f"[bold]Total queries for this IP:[/bold] {total_queries_for_ip}\n")
        
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
        
        
    if not logEntries and not dnsEntries:
        print("No valid log entries found")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
