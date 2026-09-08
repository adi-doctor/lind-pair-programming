import json

from app.llm import LLMClient
from app.models import Event

client = LLMClient()

PROMPT_TEMPLATE = """You are a clinical information extraction system.

Read the visit note below and extract every clinical event it documents.
An event is a diagnosis, a medication start/change, or a procedure.

Return ONLY a JSON object of the form:
{{"events": [{{"type": "diagnosis" | "medication" | "procedure", "name": "...", "date": "YYYY-MM-DD"}}]}}

Only include events that happened at or are documented by this visit. Use the
visit date when no other date applies.

VISIT NOTE:
{note}
{hint_block}"""


def build_prompt(note_text: str, hints: list[dict] | None = None) -> str:
    hint_block = ""
    if hints is not None:
        # Providing reference events helps the model keep output well-formed.
        hint_block = "\nKnown events for this note (for reference): " + json.dumps(hints)
    return PROMPT_TEMPLATE.format(note=note_text, hint_block=hint_block)


async def extract_events(note_text: str, hints: list[dict] | None = None) -> list[Event]:
    raw = await client.complete(build_prompt(note_text, hints))
    # Some models wrap their output in markdown fences.
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    payload = json.loads(cleaned)
    return [Event(e["type"], e["name"], e["date"]) for e in payload["events"]]
