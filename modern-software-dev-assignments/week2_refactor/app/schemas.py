from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field

class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Free-form notes to extract action items from")
    save_note: bool = Field(False, description="Whether to persist the raw note to the database")

class ActionItemOut(BaseModel):
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool = False
    created_at: str

class ExtractResponse(BaseModel):
    note_id: Optional[int] = None
    items: List[ActionItemOut]

class CreateNoteRequest(BaseModel):
    content: str = Field(..., min_length=1)

class NoteOut(BaseModel):
    id: int
    content: str
    created_at: str

class MarkDoneRequest(BaseModel):
    done: bool = True
