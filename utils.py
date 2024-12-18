from datetime import datetime
import humanize
def format_duration(seconds: int) -> str:
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

def format_view_count(count: int) -> str:
    if count >= 10000000:
        return f"{count // 10000000}Cr"
    elif count >= 1000000:
        return f"{count // 1000000}M"
    elif count >= 1000:
        return f"{count // 1000}K"
    return str(count)

def format_published_time(published_time: datetime) -> str:
    return humanize.naturaltime(published_time)