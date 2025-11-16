from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import json
import redis

from pydantic import BaseModel

from app.db.db import get_session
from app.db.models.help_request import HelpRequest, HelpStatus
from app.db.models.kb_article import KBArticle

from app.services.gemini_service import extract_kb_metadata

from dotenv import load_dotenv

load_dotenv()


redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnswerPayload(BaseModel):
    answer: str



@app.get("/requests/pending", response_model=List[HelpRequest])
def get_pending_requests(session: Session = Depends(get_session)):
    stmt = select(HelpRequest).where(HelpRequest.status == HelpStatus.pending)
    return session.exec(stmt).all()


@app.get("/requests/resolved", response_model=List[HelpRequest])
def get_resolved_requests(session: Session = Depends(get_session)):
    stmt = select(HelpRequest).where(HelpRequest.status == HelpStatus.resolved)
    return session.exec(stmt).all()


@app.post("/requests/{req_id}/answer")
async def answer_help_request(
    req_id: int,
    payload: AnswerPayload,
    session: Session = Depends(get_session)
):
    help_req = session.get(HelpRequest, req_id)

    if not help_req:
        raise HTTPException(status_code=404, detail="Help request not found")

    if help_req.status == HelpStatus.resolved:
        raise HTTPException(status_code=400, detail="Request already resolved")

    # Update help request
    help_req.supervisor_answer = payload.answer
    help_req.status = HelpStatus.resolved
    help_req.answered_at = datetime.utcnow()

    # NEW: Extract metadata via llm
    meta = await extract_kb_metadata(help_req.question, payload.answer)
    kb_entry = KBArticle(
        business_id=help_req.business_id,
        title=help_req.question,
        content={
            "key": meta["key"],
            "canonical_question": meta["canonical_question"],
            "category": meta["category"],
            "tags": meta["tags"],
            "answer": payload.answer
        }
    )

    session.add(help_req)
    session.add(kb_entry)
    session.commit()
    session.refresh(help_req)

    msg = {
        "business_id": help_req.business_id,
        "request_id": help_req.id,
        "answer": payload.answer,
        "question" : help_req.question,
    }

    redis_client.publish("supervisor_answers", json.dumps(msg))

    return {
        "message": "Help request resolved, metadata extracted, KB updated",
        "request": help_req
    }


@app.get("/")
def root():
    return {"message": "Support backend running"}
