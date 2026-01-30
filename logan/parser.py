import re
from datetime import datetime

# A 3 digit number with with a double quote and a space before the number
STATUS_RE = re.compile(r'" \d{3} ')

def extract_status(line: str) -> int:
    match = STATUS_RE.search(line)
    if not match:
        raise ValueError("Status code not present")

    # Returns the match
    # Removes any double quotes, whitespaces and \n \t 
    return int(match.group().strip().replace('"', ''))

# returns a string of chars between [] as short as possible, ? not greedy
TIME_RE = re.compile(r"\[(.*?)\]")

def extract_time(line: str) -> datetime:
    match = TIME_RE.search(line)
    if not match:
        raise ValueError("Timestamp not present")

    # Strign with just content in [], if 0 content with []
    raw = match.group(1)
    return datetime.strptime(raw, "%d/%b/%Y:%H:%M:%S %z") # Convert string to datetime formatt    
