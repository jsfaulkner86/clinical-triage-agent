"""Tests for the clinical triage audit layer."""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from audit.models import TriageAuditEvent, TriageAuditEventType
from audit.logger import TriageAuditLogger


def test_audit_event_model():
    event = TriageAuditEvent(
        event_type=TriageAuditEventType.ROUTING_COMPLETED,
        patient_id="P-001",
        message_id="MSG-001",
        acuity_level="URGENT",
        assigned_pathway="Acute Care",
        assigned_role="RN Pool",
        requires_human_review=False,
    )
    assert event.id is not None
    assert isinstance(event.created_at, datetime)
    assert event.acuity_level == "URGENT"


@pytest.mark.asyncio
async def test_logger_never_raises_without_pool():
    logger = TriageAuditLogger(dsn="postgresql://test")
    logger._pool = None
    await logger.log(TriageAuditEvent(
        event_type=TriageAuditEventType.ROUTING_FAILED,
        message_id="MSG-FAIL",
        error_detail="Test failure",
    ))


@pytest.mark.asyncio
async def test_logger_writes_routing_completed():
    logger = TriageAuditLogger(dsn="postgresql://test")
    mock_conn = AsyncMock()
    mock_pool = AsyncMock()
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
    logger._pool = mock_pool

    await logger.log_routing_completed(
        patient_id="P-001",
        message_id="MSG-001",
        acuity_level="URGENT",
        assigned_pathway="Acute Care",
        assigned_role="RN Pool",
        requires_human_review=False,
        documentation_gaps=[],
    )
    mock_conn.execute.assert_called_once()
