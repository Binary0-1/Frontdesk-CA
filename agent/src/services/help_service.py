import logging
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass
from .db import get_db

logger = logging.getLogger("help_service")


@dataclass
class HelpRequest:
    id: int
    business_id: int
    customer_id: int
    question: str
    status: str = "pending"
    supervisor_answer: Optional[str] = None
    created_at: Optional[str] = None
    answered_at: Optional[str] = None


class HelpRequestService:

    def __init__(self):
        logger.info("Help Service initialized")

    # creates a help req entry in the table 
    def create_request(self, question: str, business_id: int, customer_id: int) -> HelpRequest:
        conn = None
        try:
            conn = get_db()
            cur = conn.cursor()

            created_at = datetime.now(timezone.utc)

            cur.execute(
                """
                INSERT INTO help_requests (business_id, customer_id, question, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, business_id, customer_id, question, status, supervisor_answer, created_at, answered_at
                """,
                (business_id, customer_id, question, "pending", created_at)
            )

            row = cur.fetchone()
            conn.commit()

            help_req = HelpRequest(
                id=row["id"],
                business_id=row["business_id"],
                customer_id=row["customer_id"],
                question=row["question"],
                status=row["status"],
                supervisor_answer=row["supervisor_answer"],
                created_at=row["created_at"].isoformat() if row["created_at"] else None,
                answered_at=row["answered_at"].isoformat() if row["answered_at"] else None,
            )

            logger.info(f"Help request created: {help_req.id}")
            return help_req

        except Exception as e:
            logger.error(f"Error creating help request: {e}", exc_info=True)
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
