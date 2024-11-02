import re

def _convert_time_to_minutes(self, time_str: str) -> int | None:
    def extract_time(unit: str) -> int:
        match = re.search(rf"(\d+){unit}", time_str.strip())
        return int(match.group(1)) if match else 0
    days_in_minutes = extract_time('d') * 24 * 60
    hours_in_minutes = extract_time('h') * 60
    total_minutes = days_in_minutes + hours_in_minutes + extract_time('m')
    return total_minutes if total_minutes > 0 else None

def id_valid(issue_id: str) -> bool:
    return re.match(r"^[A-Za-z]+-\d+$", issue_id)