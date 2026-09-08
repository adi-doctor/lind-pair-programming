import time

from fastapi import FastAPI, HTTPException

from app.db import get_conn
from app.pipeline.ingest import ingest_all

app = FastAPI(title="Chronicle")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest")
async def ingest() -> dict:
    started = time.monotonic()
    result = await ingest_all()
    result["duration_seconds"] = round(time.monotonic() - started, 1)
    return result


@app.get("/patients")
def list_patients() -> list[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT id, name FROM patients ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/patients/{patient_id}/timeline")
def patient_timeline(patient_id: str) -> dict:
    conn = get_conn()
    patient = conn.execute(
        "SELECT id, name FROM patients WHERE id = ?", (patient_id,)
    ).fetchone()
    if patient is None:
        conn.close()
        raise HTTPException(status_code=404, detail="patient not found")

    events = conn.execute(
        "SELECT id, note_id, event_type, name, event_date FROM events"
        " WHERE patient_id = ? ORDER BY event_date, id",
        (patient_id,),
    ).fetchall()

    timeline = []
    for event in events:
        note = conn.execute(
            "SELECT filename, visit_date FROM notes WHERE id = ?",
            (event["note_id"],),
        ).fetchone()
        timeline.append(
            {
                "date": event["event_date"],
                "type": event["event_type"],
                "name": event["name"],
                "source_note": note["filename"],
                "recorded_at_visit": note["visit_date"],
            }
        )

    conn.close()
    return {"patient": dict(patient), "events": timeline}
