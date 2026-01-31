from parser import (
    extract_status,
    extract_time,
    extract_latency
)
from stats import (
    count_per_minute,
    avr_latency_per_minute
)
from model import LogEntry

def main():
    
    informational = 0
    successful = 0
    redirection = 0
    clientError = 0
    serverError = 0

    logEntries = []
        
    with open("sample_logs/access.log") as f:
        for line in f:
            entry = LogEntry(
                timestamp=extract_time(line),
                status=extract_status(line),
                latency=extract_latency(line)
            )
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

        each_min = count_per_minute(logEntries)

        for minute, count in sorted(each_min.items()):
            print(f"{minute} -> {count}")

        lat_min = avr_latency_per_minute(logEntries)

        for minute, count in sorted(lat_min.items()):
            print(f"{minute} avr latency: {count}ms")

        print("-"*20)
        print(f"Informational code: {informational}")
        print(f"Successful codes: {successful}")
        print(f"Redirection codes: {redirection}")
        print(f"Client error codes: {clientError}")
        print(f"Server error codes: {serverError}")


if __name__ == "__main__":
    main()
