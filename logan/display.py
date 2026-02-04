from rich.console import Console
from rich.table import Table
from collections import defaultdict
from model import (
    DNSEntry,
    HttpEntry,
    UlogdEntry,
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

def displayUlogdEntries(ulogdEntries: list[UlogdEntry]) -> None:
    console = Console()

    # Group entries by day
    day_entries = defaultdict(list)
    for entry in ulogdEntries:
        day_key = entry.timestamp.date()
        day_entries[day_key].append(entry)

    # Display entries grouped by day
    for day in sorted(day_entries.keys()):
        console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
        console.print(f"[bold cyan]{day.strftime('%B %d')}[/bold cyan]")
        console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")

        entries_for_day = day_entries[day]

        # Create table for this day
        table = Table(title=f"Ulogd Connection Tracking - {day.strftime('%B %d')}", header_style="bold magenta")

        table.add_column("Time", style="cyan", width=8)
        table.add_column("State", style="bold", width=8)
        table.add_column("Protocol", style="yellow", width=8)
        table.add_column("Source", style="green", width=21)
        table.add_column("Destination", style="blue", width=21)
        table.add_column("Packets", style="magenta", justify="right", width=7)
        table.add_column("Bytes", style="magenta", justify="right", width=7)

        for entry in entries_for_day:
            # Format time
            time_str = entry.timestamp.strftime("%H:%M:%S")

            # Color state
            if entry.state == "NEW":
                state_color = "green"
            elif entry.state == "DESTROY":
                state_color = "red"
            else:
                state_color = "yellow"

            state_str = f"[{state_color}]{entry.state}[/{state_color}]"

            # Format ORIG source and destination
            if entry.src_port_ori is not None:
                orig_src = f"{entry.src_ip_ori}:{entry.src_port_ori}"
            elif entry.type_ori is not None:
                orig_src = f"{entry.src_ip_ori}"
            else:
                orig_src = f"{entry.src_ip_ori}"

            if entry.dest_port_ori is not None:
                orig_dst = f"{entry.dest_ip_ori}:{entry.dest_port_ori}"
            elif entry.code_ori is not None:
                orig_dst = f"{entry.dest_ip_ori}"
            else:
                orig_dst = f"{entry.dest_ip_ori}"

            # Format protocol with additional info for ICMP
            proto_str = entry.protocol_ori
            if entry.type_ori is not None and entry.code_ori is not None:
                proto_str = f"{proto_str} T:{entry.type_ori} C:{entry.code_ori}"

            # Format packets and bytes (combine ORIG and REPLY)
            total_pkts = entry.pkts_ori + entry.pkts_dest
            total_bytes = entry.bytes_ori + entry.bytes_dest

            table.add_row(
                time_str,
                state_str,
                proto_str,
                orig_src,
                orig_dst,
                str(total_pkts),
                str(total_bytes)
            )

        console.print(table)

        # Summary statistics for the day
        total_new = sum(1 for e in entries_for_day if e.state == "NEW")
        total_destroy = sum(1 for e in entries_for_day if e.state == "DESTROY")

        # Protocol breakdown
        proto_count = defaultdict(int)
        for entry in entries_for_day:
            proto_count[entry.protocol_ori] += 1

        console.print(f"\n[bold]Summary for {day.strftime('%B %d')}:[/bold]")
        console.print(f"  Total Connections: {len(entries_for_day)}")
        console.print(f"  New Connections: [green]{total_new}[/green]")
        console.print(f"  Destroyed Connections: [red]{total_destroy}[/red]")
        console.print(f"  Protocol Breakdown:")
        for proto, count in sorted(proto_count.items(), key=lambda x: x[1], reverse=True):
            console.print(f"    {proto}: {count}")
        console.print()

    console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")
