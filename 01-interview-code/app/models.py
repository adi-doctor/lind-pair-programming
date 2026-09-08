from dataclasses import dataclass

EVENT_TYPES = ("diagnosis", "medication", "procedure")


@dataclass
class Event:
    type: str
    name: str
    date: str
