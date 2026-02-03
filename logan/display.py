from rich.console import Console
from rich.table import Table
from collections import defaultdict
from model import (
    DNSEntry,
    HttpEntry,
)

def displayDnsEntries(dnsEntries: list[DNSEntry]) -> None:
    console = Console()
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

def displayHttpEntries(logEntries: list[HttpEntry]) -> None:
    console = Console()

    table = Table(title="HTTP Log Analyzer", style="magenta")

    table.add_column("Time", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Latency (s)", justify="right")

    for entry in logEntries:
        status = entry.status

        if 100 <= status < 200:
            status_color = "bright_cyan"
        elif 200 <= status < 300:
            status_color = "green"
        elif 300 <= status < 400:
            status_color = "blue"
        elif 400 <= status < 500:
            status_color = "yellow"
        elif 500 <= status < 600:
            status_color = "red"
        else:
            status_color = "magenta"

        table.add_row(
            f"{entry.timestamp}",
            f"[{status_color}]{status}[/{status_color}]",
            f"{entry.latency:.1f}"
        )

    console.print(table)
