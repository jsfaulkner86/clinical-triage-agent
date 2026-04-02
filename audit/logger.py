"""Append-only audit logger for clinical triage decisions."""
import os
import json
import logging
import asyncpg
from typing import Optional
from .models import TriageAuditEvent, TriageAuditEventType

logger = logging.getLogger(__name__)


class TriageAuditLogger:
    """
    Append-only HIPAA-compliant audit logger.
    Never raises — a failed audit write must not interrupt clinical triage flow.
    """

    def __init__(self, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.getenv("DATABASE_URL", "")
        self._pool: Optional[asyncpg.Pool] = None

    async def init(self) -> None:
        self._pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=5)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()

    async def log(self, event: TriageAuditEvent) -> None:
        if not self._pool:
            logger.warning("TriageAuditLogger not initialized — event dropped: %s", event.event_type)
            return
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO triage_audit_log (
                        id, created_at, event_type, patient_id, message_id,
                        thread_id, acuity_level, message_type, assigned_pathway,
                        assigned_role, documentation_gaps, requires_human_review,
                        confidence, error_detail, metadata
                    ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15)
                    """,
                    event.id, event.created_at, event.event_type.value,
                    event.patient_id, event.message_id, event.thread_id,
                    event.acuity_level, event.message_type, event.assigned_pathway,
                    event.assigned_role, event.documentation_gaps,
                    event.requires_human_review, event.confidence,
                    event.error_detail,
                    json.dumps(event.metadata) if event.metadata else None,
                )
        except Exception as e:
            logger.error("Triage audit write failed [%s]: %s", event.message_id, e)

    async def log_routing_completed(
        self,
        patient_id: str,
        message_id: str,
        acuity_level: str,
        assigned_pathway: str,
        assigned_role: str,
        requires_human_review: bool,
        documentation_gaps: list[str],
        thread_id: Optional[str] = None,
    ) -> None:
        await self.log(TriageAuditEvent(
            event_type=TriageAuditEventType.ROUTING_COMPLETED,
            patient_id=patient_id,
            message_id=message_id,
            thread_id=thread_id,
            acuity_level=acuity_level,
            assigned_pathway=assigned_pathway,
            assigned_role=assigned_role,
            documentation_gaps=documentation_gaps,
            requires_human_review=requires_human_review,
        ))

    async def log_human_review_flagged(
        self,
        patient_id: str,
        message_id: str,
        reason: str,
        acuity_level: Optional[str] = None,
    ) -> None:
        await self.log(TriageAuditEvent(
            event_type=TriageAuditEventType.HUMAN_REVIEW_FLAGGED,
            patient_id=patient_id,
            message_id=message_id,
            acuity_level=acuity_level,
            requires_human_review=True,
            metadata={"flag_reason": reason},
        ))


audit_logger = TriageAuditLogger()
