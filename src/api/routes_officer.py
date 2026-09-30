"""
Agricultural Extension Officer Workflow API Routes.

Endpoints for:
1. Extension officer review queue management
2. Reviewing, editing, certifying, and approving AI-generated advisories
3. Digital audit trail tracking
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import uuid

from src.workflow.officer_review import review_queue

router = APIRouter(prefix="/api/v1/officer", tags=["Officer Review Workflow"])

class SubmitDraftRequest(BaseModel):
    panchayat_id: str
    block_id: str
    advisory_payload: Dict[str, Any]

class UpdateReviewRequest(BaseModel):
    officer_name: str = "Dr. S. Patil (Block Agronomist)"
    status: str = "APPROVED" # DRAFT | UNDER_REVIEW | APPROVED | BROADCASTED | REJECTED
    notes: str = "Certified suitable for distribution."
    overrides: Optional[Dict[str, Any]] = None

@router.get("/queue")
def list_queue(status: Optional[str] = None):
    """Lists advisories pending or completed in the officer review queue."""
    items = review_queue.list_queue(status)
    return {"status": "success", "count": len(items), "queue": items}

@router.post("/draft")
def submit_new_draft(req: SubmitDraftRequest):
    """Submits a newly generated AI agromet advisory into the review queue."""
    adv_id = f"ADV-{str(uuid.uuid4())[:8].upper()}"
    entry = review_queue.submit_draft(
        advisory_id=adv_id,
        panchayat_id=req.panchayat_id,
        block_id=req.block_id,
        advisory_payload=req.advisory_payload
    )
    return {"status": "success", "entry": entry}

@router.post("/review/{advisory_id}")
def update_review(advisory_id: str, req: UpdateReviewRequest):
    """Updates an advisory's review status, notes, or agronomic overrides."""
    updated = review_queue.update_officer_review(
        advisory_id=advisory_id,
        officer_name=req.officer_name,
        status=req.status,
        notes=req.notes,
        overrides=req.overrides
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Advisory ID not found in queue")
    return {"status": "success", "entry": updated}

@router.get("/audit")
def get_audit_trail():
    """Returns the immutable audit log of officer reviews and edits."""
    return {"status": "success", "audit_log": review_queue.audit_log}
