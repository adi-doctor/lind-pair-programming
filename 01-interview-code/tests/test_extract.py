import asyncio

from app.pipeline import extract


def test_extract_parses_events(monkeypatch):
    async def fake_complete(prompt):
        return (
            '{"events": [{"type": "diagnosis", "name": "asthma",'
            ' "date": "2024-02-01"}]}'
        )

    monkeypatch.setattr(extract.client, "complete", fake_complete)
    events = asyncio.run(extract.extract_events("Visit ID: VN-999\nsome note"))
    assert len(events) == 1
    assert events[0].type == "diagnosis"
    assert events[0].name == "asthma"


def test_build_prompt_includes_note_text():
    prompt = extract.build_prompt("Visit ID: VN-999\npatient was seen today")
    assert "patient was seen today" in prompt
