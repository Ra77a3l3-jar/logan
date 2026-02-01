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
        # Count queries per (source IP, destination domain)
        ip_to_domain_count = defaultdict(lambda: defaultdict(int))
        
        # Count queries per minute from each IP
        ip_queries_per_minute = defaultdict(lambda: defaultdict(int))
        
        # Count total queries per IP
        ip_total_queries = defaultdict(int)
        
        # Count queries per domain
        domain_query_count = defaultdict(int)
        
        for entry in dnsEntries:
            # Track IP -> domain queries
            ip_to_domain_count[entry.src_ip][entry.name] += 1
            
            # Track queries per minute per IP
            minute_key = entry.timestamp.replace(second=0, microsecond=0)
            ip_queries_per_minute[entry.src_ip][minute_key] += 1
            
            # Total queries per IP
            ip_total_queries[entry.src_ip] += 1
            
            # Total queries per domain
            domain_query_count[entry.name] += 1

        console.print("\n")
        table1 = Table(title="DNS Queries")

        table1.add_column("Ip", style="cyan")
        table1.add_column("Destination", style="blue")
        table1.add_column("Frequency (min)", style="yellow", justify="right")
        table1.add_column("Total Queries", style="yellow", justify="right")
    
        ip_active_minutes = {
            ip: len(minutes)
            for ip, minutes in ip_queries_per_minute.items()
        }

        for ip, domain in ip_to_domain_count.items():
            active_min = ip_active_minutes.get(ip, 1)

            for i, (domain, count) in enumerate(
                sorted(domain.items(), key=lambda x: x[1], reverse=True)
            ):
                freq_per_min = count / active_min

                table1.add_row(
                    ip if i == 0 else "",
                    domain,
                    f"{freq_per_min:.2f}",
                    str(count),
                )

        console.print(table1)
        
    if not logEntries and not dnsEntries:
        print("No valid log entries found")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
