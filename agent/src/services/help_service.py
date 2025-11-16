import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass
import boto3
import hashlib
import os

logger = logging.getLogger("help_service")


def make_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


@dataclass
class HelpRequest:
    request_id: str
    user_id: str
    business_id: str
    question: str
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None
    status: str = "pending"
    answer: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()


class HelpRequestService:

    def __init__(self, table_name: str, region: str):
        logger.info("Help Service initialized")

        self.dynamo = boto3.resource(
            "dynamodb",
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        self.table = self.dynamo.Table(table_name)

    def register_temp_phone(self, business_id: str, phone_number: str) -> str:
        user_id = make_hash(f"{business_id}:{phone_number}")

        self.table.put_item(
            Item={
                "PK": f"BUSINESS#{business_id}",
                "SK": f"USER#{user_id}",
                "user_id": user_id,
                "phone_number": phone_number,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        logger.info(f"Temporary phone -> user_id: {phone_number} -> {user_id}")
        return user_id

    def create_request(self, question: str, business_id: str, phone_number: str) -> HelpRequest:
        request_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        user_id = make_hash(f"{business_id}:{phone_number}")

        help_req = HelpRequest(
            request_id=request_id,
            user_id=user_id,
            business_id=business_id,
            question=question,
            created_at=created_at,
        )

        item = {
            "PK": f"BUSINESS#{business_id}",
            "SK": f"REQUEST#{request_id}",
            "request_id": request_id,
            "business_id": business_id,
            "user_id": user_id,
            "question": question,
            "status": "pending",
            "created_at": created_at,
        }

        self.table.put_item(Item=item)
        logger.info(f"Help request created: {request_id}")

        return help_req

    def get_request(self, business_id: int, request_id: str) -> Optional[HelpRequest]:
        resp = self.table.get_item(
            Key={
                "PK": f"BUSINESS#{business_id}",
                "SK": f"REQUEST#{request_id}"
            }
        )

        item = resp.get("Item")
        if not item:
            return None

        return HelpRequest(
            request_id=item["request_id"],
            user_id=item["user_id"],
            business_id=item["business_id"],
            question=item["question"],
            created_at=item["created_at"],
            resolved_at=item.get("resolved_at"),
            status=item["status"],
            answer=item.get("answer"),
        )

    def update_status(self, business_id: int, request_id: str, new_status: str, answer: Optional[str] = None) -> bool:
        update_expr = "SET #s = :new_status"
        expr_vals = {":new_status": new_status}
        expr_names = {"#s": "status"}

        if new_status == "resolved":
            resolved_ts = datetime.now(timezone.utc).isoformat()
            update_expr += ", resolved_at = :resolved_at"
            expr_vals[":resolved_at"] = resolved_ts

        if answer is not None:
            update_expr += ", answer = :answer"
            expr_vals[":answer"] = answer

        resp = self.table.update_item(
            Key={
                "PK": f"BUSINESS#{business_id}",
                "SK": f"REQUEST#{request_id}"
            },
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_vals,
            ReturnValues="UPDATED_NEW"
        )

        return "Attributes" in resp
