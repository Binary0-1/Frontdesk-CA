import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict
from dataclasses import dataclass
from .db import get_db

logger = logging.getLogger("help_service")


@dataclass
class HelpRequest:
    request_id: str
    business_id: str
    question: str
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None
    status: str = "pending"
    answer: Optional[str] = None
    customer_contact: Optional[Dict] = None


class HelpRequestService:

    def __init__(self):
        logger.info("Help Service initialized")

    def create_request(self, question: str, business_id: str, customer_contact: Dict) -> HelpRequest:
        conn = None
        try:
            conn = get_db()
            cur = conn.cursor()

            # Check if business_id exists
            cur.execute("SELECT id FROM business WHERE id = %s", (business_id,))
            if not cur.fetchone():
                raise ValueError(f"Business with ID {business_id} does not exist.")

            request_id = str(uuid.uuid4())
            created_at = datetime.now(timezone.utc)

            # Insert into help_request table
            cur.execute(
                """
                INSERT INTO help_request (id, business_id, question, customer_contact, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, business_id, question, customer_contact, status, created_at
                """,
                (request_id, business_id, question, customer_contact, "pending", created_at)
            )
            new_request = cur.fetchone()
            conn.commit()

            help_req = HelpRequest(
                request_id=str(new_request['id']),
                business_id=str(new_request['business_id']),
                question=new_request['question'],
                customer_contact=new_request['customer_contact'],
                status=new_request['status'],
                created_at=new_request['created_at'].isoformat() if new_request['created_at'] else None,
            )
            logger.info(f"Help request created: {request_id}")
            return help_req

        except Exception as e:
            logger.error(f"Error creating help request: {e}", exc_info=True)
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    # Other methods like get_request, update_status would also need to be rewritten
    # to use psycopg2 and SQL queries. For now, focusing on create_request.
