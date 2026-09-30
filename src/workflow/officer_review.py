"""
Human-in-the-Loop Agricultural Extension Officer Review Workflow.

Manages the advisory lifecycle state machine:
  [AI DRAFT] ---> [UNDER_REVIEW] ---> [APPROVED] ---> [BROADCASTED]
                      |
                      v
                  [REJECTED / REVISED]

Provides extension officers full audit logging, overrides, and digital sign-off.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

class AdvisoryReviewQueue:
    def __init__(self):
        self.queue: Dict[str, Dict[str, Any]] = {}
        self.audit_log: List[Dict[str, Any]] = []

    def submit_draft(
        self,
        advisory_id: str,
        panchayat_id: str,
        block_id: str,
        advisory_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        entry = {
            "advisory_id": advisory_id,
            "panchayat_id": panchayat_id,
            "block_id": block_id,
            "status": "DRAFT", # DRAFT | UNDER_REVIEW | APPROVED | BROADCASTED
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "reviewed_by": None,
            "officer_notes": "",
            "advisory_payload": advisory_payload,
            "overrides": {}
        }
        self.queue[advisory_id] = entry
        self._log_event(advisory_id, "SUBMITTED_AS_DRAFT", "System AI Engine")
        return entry

    def update_officer_review(
        self,
        advisory_id: str,
        officer_name: str,
        status: str,
        notes: str = "",
        overrides: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        if advisory_id not in self.queue:
            return None

        entry = self.queue[advisory_id]
        entry["status"] = status
        entry["reviewed_by"] = officer_name
        entry["officer_notes"] = notes
        entry["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        if overrides:
            entry["overrides"] = overrides
            # Merge overrides into payload
            for k, v in overrides.items():
                if k in entry["advisory_payload"]:
                    entry["advisory_payload"][k] = v

        self._log_event(advisory_id, f"STATUS_CHANGED_TO_{status}", officer_name, notes)
        return entry

    def list_queue(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        items = list(self.queue.values())
        if status:
            items = [item for item in items if item["status"] == status]
        return sorted(items, key=lambda x: x["created_at"], reverse=True)

    def get_advisory(self, advisory_id: str) -> Optional[Dict[str, Any]]:
        return self.queue.get(advisory_id)

    def _log_event(self, advisory_id: str, event_type: str, actor: str, details: str = ""):
        self.audit_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "advisory_id": advisory_id,
            "event_type": event_type,
            "actor": actor,
            "details": details
        })

review_queue = AdvisoryReviewQueue()
