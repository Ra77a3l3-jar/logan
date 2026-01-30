import re

# A 3 digit number with with a double quote and a space before the number
STATUS_RE = re.compile(r'" \d{3} ')

def extract_status(line: str) -> int:
    match = STATUS_RE.search(line)
    if not match:
        raise ValueError("Status code not present")

    # Returns the match
    # Removes any double quotes, whitespaces and \n \t 
    return int(match.group().strip().replace('"', ''))
