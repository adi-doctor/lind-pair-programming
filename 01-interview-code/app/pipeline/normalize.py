from datetime import datetime

from app.models import Event

DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y"]

# Specialty routing codes for the referrals integration.
SPECIALTY_CODES = {
    "cardiology": "CARD",
    "endocrinology": "ENDO",
    "orthopedics": "ORTH",
    "pulmonology": "PULM",
}


def normalize_date(raw: str) -> str:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw


def dedupe_events(events: list[Event]) -> list[Event]:
    seen: set[tuple[str, str, str]] = set()
    result: list[Event] = []
    for event in events:
        key = (event.type, event.name.lower(), event.date)
        if key in seen:
            continue
        seen.add(key)
        result.append(event)
    return result
