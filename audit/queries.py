"""Read-side analytics and reporting for triage audit data."""
import os
import asyncpg
from datetime import datetime, timedelta
from typing import Optional


class TriageAuditQueryService:

    def __init__(self, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.getenv("DATABASE_URL", "")
        self._pool: Optional[asyncpg.Pool] = None

    async def init(self) -> None:
        self._pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=3)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()

    async def get_message_trail(self, message_id: str) -> list[dict]:
        """Full event trail for a single patient message."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM triage_audit_log WHERE message_id=$1 ORDER BY created_at ASC",
                message_id,
            )
            return [dict(r) for r in rows]

    async def get_acuity_distribution(
        self, since: Optional[datetime] = None
    ) -> list[dict]:
        """Breakdown of triage decisions by acuity level — use for clinical operations reporting."""
        since = since or (datetime.utcnow() - timedelta(days=30))
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT acuity_level, COUNT(*) AS count,
                       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
                FROM triage_audit_log
                WHERE event_type = 'routing_completed' AND created_at >= $1
                GROUP BY acuity_level ORDER BY count DESC
                """,
                since,
            )
            return [dict(r) for r in rows]

    async def get_human_review_rate(
        self, since: Optional[datetime] = None
    ) -> dict:
        """Ratio of auto-triaged vs. flagged-for-human-review. KPI for model confidence calibration."""
        since = since or (datetime.utcnow() - timedelta(days=30))
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) FILTER (WHERE event_type='routing_completed')     AS total_routed,
                    COUNT(*) FILTER (WHERE event_type='human_review_flagged')  AS flagged_for_review,
                    COUNT(*) FILTER (WHERE event_type='routing_failed')        AS failed
                FROM triage_audit_log WHERE created_at >= $1
                """,
                since,
            )
            return dict(row)

    async def get_documentation_gap_summary(
        self, since: Optional[datetime] = None
    ) -> list[dict]:
        """Most frequently missing documentation fields — use to identify systemic intake gaps."""
        since = since or (datetime.utcnow() - timedelta(days=30))
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT gap, COUNT(*) AS frequency
                FROM triage_audit_log,
                     UNNEST(documentation_gaps) AS gap
                WHERE created_at >= $1
                GROUP BY gap ORDER BY frequency DESC
                """,
                since,
            )
            return [dict(r) for r in rows]

    async def export_audit_range(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> list[dict]:
        """Full export for HIPAA audit requests, JCAHO reviews."""
        since = since or (datetime.utcnow() - timedelta(days=90))
        until = until or datetime.utcnow()
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM triage_audit_log WHERE created_at BETWEEN $1 AND $2 ORDER BY created_at ASC",
                since, until,
            )
            return [dict(r) for r in rows]
