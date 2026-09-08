import logging
import re
from pathlib import Path

from app.db import get_conn
from app.pipeline.extract import extract_events
from app.pipeline.normalize import normalize_date

logger = logging.getLogger(__name__)

NOTES_DIR = Path(__file__).resolve().parents[2] / "data" / "notes"

VISIT_RE = re.compile(r"^Visit ID:\s*(VN-\d+)", re.MULTILINE)
PATIENT_RE = re.compile(r"^Patient:\s*(P-\d+)\s*\(([^)]+)\)", re.MULTILINE)
DATE_RE = re.compile(r"^Visit date:\s*(\S+)", re.MULTILINE)


def parse_note(path: Path) -> dict:
    text = path.read_text()
    return {
        "visit_id": VISIT_RE.search(text).group(1),
        "patient_id": PATIENT_RE.search(text).group(1),
        "patient_name": PATIENT_RE.search(text).group(2),
        "visit_date": DATE_RE.search(text).group(1),
        "filename": path.name,
        "text": text,
    }


async def ingest_all(notes_dir: Path = NOTES_DIR) -> dict:
    conn = get_conn()
    conn.execute("DELETE FROM events")
    conn.execute("DELETE FROM notes")
    conn.execute("DELETE FROM patients")
    conn.commit()
    conn.close()

    processed = 0
    skipped = 0
    events_created = 0

    for path in sorted(notes_dir.glob("*.txt")):
        note = parse_note(path)

        conn = get_conn()
        conn.execute(
            "INSERT OR IGNORE INTO patients (id, name) VALUES (?, ?)",
            (note["patient_id"], note["patient_name"]),
        )
        conn.commit()
        conn.execute(
            "INSERT INTO notes (id, patient_id, filename, visit_date) VALUES (?, ?, ?, ?)",
            (note["visit_id"], note["patient_id"], note["filename"], note["visit_date"]),
        )
        conn.commit()

        try:
            events = await extract_events(note["text"])
        except Exception:
            logger.debug("extraction failed for %s", note["visit_id"])
            skipped += 1
            conn.close()
            continue

        for event in events:
            conn.execute(
                "INSERT INTO events (note_id, patient_id, event_type, name, event_date)"
                " VALUES (?, ?, ?, ?, ?)",
                (
                    note["visit_id"],
                    note["patient_id"],
                    event.type,
                    event.name,
                    normalize_date(event.date),
                ),
            )
            conn.commit()
            events_created += 1

        processed += 1
        conn.close()

    return {
        "notes_processed": processed,
        "notes_skipped": skipped,
        "events_created": events_created,
    }
