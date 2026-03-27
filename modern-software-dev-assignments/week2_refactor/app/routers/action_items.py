from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from .. import db
from ..schemas import ActionItemOut, ExtractRequest, ExtractResponse, MarkDoneRequest
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest, use_llm: bool = False) -> ExtractResponse:
    # save note if requested
    note_id: Optional[int] = None
    if req.save_note:
        note_id = db.insert_note(req.text)

    # choose extractor (query param keeps backward compatibility)
    items = extract_action_items_llm(req.text) if use_llm else extract_action_items(req.text)

    ids = db.insert_action_items(items, note_id=note_id)
    rows = db.list_action_items(note_id=note_id) if ids else []

    # Build response aligned with inserted ids (preserve order)
    id_to_row = {int(r["id"]): r for r in rows}
    out_items: List[ActionItemOut] = []
    for _id, txt in zip(ids, items):
        r = id_to_row.get(int(_id))
        created_at = r["created_at"] if r else ""
        done = bool(r["done"]) if r else False
        out_items.append(
            ActionItemOut(
                id=int(_id),
                note_id=note_id,
                text=txt,
                done=done,
                created_at=created_at,
            )
        )

    return ExtractResponse(note_id=note_id, items=out_items)


@router.get("/", response_model=list[ActionItemOut])
def list_all(note_id: Optional[int] = None) -> list[ActionItemOut]:
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemOut(
            id=int(r["id"]),
            note_id=(int(r["note_id"]) if r["note_id"] is not None else None),
            text=str(r["text"]),
            done=bool(r["done"]),
            created_at=str(r["created_at"]),
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done", response_model=ActionItemOut)
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> ActionItemOut:
    # Ensure exists
    rows = db.list_action_items()
    if not any(int(r["id"]) == action_item_id for r in rows):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="action item not found")

    db.mark_action_item_done(action_item_id, payload.done)

    # Return updated row
    row = next(r for r in db.list_action_items() if int(r["id"]) == action_item_id)
    return ActionItemOut(
        id=int(row["id"]),
        note_id=(int(row["note_id"]) if row["note_id"] is not None else None),
        text=str(row["text"]),
        done=bool(row["done"]),
        created_at=str(row["created_at"]),
    )
