import logging
import uuid
from datetime import datetime
from typing import Optional, Dict
from dataclasses import dataclass
import boto3
import os

logger = logging.getLogger("help_service")


@dataclass
class HelpRequest:
    request_id: str
    business_id: str
    question: str
    caller_phone: Optional[str] = None
    caller_name: Optional[str] = None
    created_at: str = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()


class HelpRequestService:
    
    def __init__(self, table_name: str, region: str):
        self.dynamo = boto3.resource(
            "dynamodb",
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        self.table = self.dynamo.Table(table_name)
    
    def create_request(
        self, 
        business_id: str, 
        question: str,
        caller_phone: Optional[str] = None,
        caller_name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> HelpRequest:
        try:
            request_id = str(uuid.uuid4())
            help_request = HelpRequest(
                request_id=request_id,
                business_id=business_id,
                question=question,
                caller_phone=caller_phone,
                caller_name=caller_name
            )
            
            item = {
                "PK": f"BUSINESS#{business_id}",
                "SK": f"HELP#{request_id}",
                "request_id": request_id,
                "business_id": business_id,
                "question": question,
                "status": help_request.status,
                "created_at": help_request.created_at,
            }
            
            if caller_phone:
                item["caller_phone"] = caller_phone
            
            if caller_name:
                item["caller_name"] = caller_name
            
            if metadata:
                item["metadata"] = metadata
            
            self.table.put_item(Item=item)
            
            logger.info(f"✅ Help request created: {request_id} for business: {business_id}")
            logger.info(f"   Question: {question}")
            
            self._notify_business(business_id, help_request)
            
            return help_request
            
        except Exception as e:
            logger.error(f"Failed to create help request: {e}", exc_info=True)
            return HelpRequest(
                request_id=str(uuid.uuid4()),
                business_id=business_id,
                question=question,
                status="failed"
            )
    
    def get_request(self, business_id: str, request_id: str) -> Optional[HelpRequest]:
        try:
            response = self.table.get_item(
                Key={
                    "PK": f"BUSINESS#{business_id}",
                    "SK": f"HELP#{request_id}"
                }
            )
            
            if "Item" in response:
                item = response["Item"]
                return HelpRequest(
                    request_id=item["request_id"],
                    business_id=item["business_id"],
                    question=item["question"],
                    caller_phone=item.get("caller_phone"),
                    caller_name=item.get("caller_name"),
                    created_at=item["created_at"],
                    status=item.get("status", "pending")
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve help request: {e}", exc_info=True)
            return None
    
    def update_status(self, business_id: str, request_id: str, new_status: str) -> bool:
        try:
            self.table.update_item(
                Key={
                    "PK": f"BUSINESS#{business_id}",
                    "SK": f"HELP#{request_id}"
                },
                UpdateExpression="SET #status = :status, updated_at = :updated_at",
                ExpressionAttributeNames={
                    "#status": "status"
                },
                ExpressionAttributeValues={
                    ":status": new_status,
                    ":updated_at": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Help request {request_id} status updated to: {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update help request status: {e}", exc_info=True)
            return False
    
    def _notify_business(self, business_id: str, help_request: HelpRequest):
        logger.info(f"Notify business {business_id} about request {help_request.request_id}")
        pass