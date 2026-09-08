"""Score the extraction pipeline against hand-labeled ground truth.

Usage: python -m eval.run_eval
"""

import asyncio
import json
from pathlib import Path

from app.pipeline.extract import extract_events
from app.pipeline.ingest import NOTES_DIR, parse_note
from app.pipeline.normalize import normalize_date

LABELS_PATH = Path(__file__).resolve().parents[1] / "data" / "labels.json"


def event_key(event: dict) -> tuple[str, str, str]:
    return (event["type"], event["name"].lower(), normalize_date(event["date"]))


def main() -> None:
    with open(LABELS_PATH) as f:
        labels: dict[str, list[dict]] = json.load(f)

    total_tp = total_fp = total_fn = 0
    scored = []
    skipped = []

    for path in sorted(NOTES_DIR.glob("*.txt")):
        note = parse_note(path)
        visit_id = note["visit_id"]
        expected = labels.get(visit_id, [])

        try:
            events = asyncio.run(extract_events(note["text"], hints=expected))
        except Exception as exc:
            skipped.append((visit_id, type(exc).__name__))
            continue

        predicted_keys = {
            (e.type, e.name.lower(), normalize_date(e.date)) for e in events
        }
        expected_keys = {event_key(e) for e in expected}

        tp = len(predicted_keys & expected_keys)
        fp = len(predicted_keys - expected_keys)
        fn = len(expected_keys - predicted_keys)
        total_tp += tp
        total_fp += fp
        total_fn += fn
        scored.append((visit_id, tp, fp, fn))

    print(f"{'note':<10}{'tp':>4}{'fp':>4}{'fn':>4}")
    for visit_id, tp, fp, fn in scored:
        print(f"{visit_id:<10}{tp:>4}{fp:>4}{fn:>4}")

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    print()
    print(f"Notes scored: {len(scored)}/{len(scored) + len(skipped)}")
    for visit_id, reason in skipped:
        print(f"  skipped {visit_id} ({reason})")
    print()
    print(f"precision: {precision:.3f}")
    print(f"recall:    {recall:.3f}")
    print(f"f1:        {f1:.3f}")


if __name__ == "__main__":
    main()
