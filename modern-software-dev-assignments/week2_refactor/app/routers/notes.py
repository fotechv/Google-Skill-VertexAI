from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from .. import db
from ..schemas import CreateNoteRequest, NoteOut


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(payload: CreateNoteRequest) -> NoteOut:
    note_id = db.insert_note(payload.content)
    note = db.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to create note")
    return NoteOut(id=int(note["id"]), content=str(note["content"]), created_at=str(note["created_at"]))


@router.get("/{note_id}", response_model=NoteOut)
def get_single_note(note_id: int) -> NoteOut:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="note not found")
    return NoteOut(id=int(row["id"]), content=str(row["content"]), created_at=str(row["created_at"]))


@router.get("/", response_model=list[NoteOut])
def list_all_notes() -> list[NoteOut]:
    rows = db.list_notes()
    return [NoteOut(id=int(r["id"]), content=str(r["content"]), created_at=str(r["created_at"])) for r in rows]
