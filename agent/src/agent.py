import logging
from dotenv import load_dotenv
from livekit.agents import function_tool

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    inference,
)

from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

import boto3
import os
import uuid
from typing import List, Dict

load_dotenv(".env.local")

logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)

# -----------------------------
# DynamoDB + SQL placeholders
# -----------------------------
dynamo = boto3.resource(
    "dynamodb",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)
KB_TABLE = dynamo.Table(os.getenv("DYNAMO_KB_TABLE"))
BUSINESS_ID = "212"


def kb_lookup(business_id: str, question: str) -> Dict:
    """
    Enhanced KB lookup with better matching.
    Returns multiple relevant entries if found.
    """
    # try:
    #     resp = KB_TABLE.query(
    #         KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
    #         ExpressionAttributeValues={
    #             ":pk": f"BUSINESS#{business_id}",
    #             ":sk": "ENTRY#"
    #         }
    #     )
        
    #     items = resp.get("Items", [])
    #     if not items:
    #         return {"hit": False, "matches": []}
        
    #     # Enhanced matching: check for keyword overlap
    #     question_lower = question.lower()
    #     question_words = set(question_lower.split())
        
    #     matches = []
    #     for item in items:
    #         item_question = item.get("question", "").lower()
    #         item_words = set(item_question.split())
            
    #         # Check for exact substring match (original logic)
    #         if item_question in question_lower or question_lower in item_question:
    #             matches.append({
    #                 "question": item.get("question"),
    #                 "answer": item.get("answer"),
    #                 "score": 1.0  # Exact match
    #             })
    #         # Check for word overlap (fallback)
    #         else:
    #             overlap = len(question_words & item_words)
    #             if overlap >= 2:  # At least 2 common words
    #                 matches.append({
    #                     "question": item.get("question"),
    #                     "answer": item.get("answer"),
    #                     "score": overlap / max(len(question_words), len(item_words))
    #                 })
        
    #     # Sort by score and return top matches
    #     matches.sort(key=lambda x: x["score"], reverse=True)
        
    #     if matches:
    #         return {"hit": True, "matches": matches[:3]}  # Top 3 matches
        
    return {"hit": False, "matches": []}
        
    # except Exception as e:
    #     logger.error(f"KB lookup error: {e}")
    #     return {"hit": False, "matches": [], "error": str(e)}


def create_help_request_sql(business_id: str, question: str) -> str:
    """Create help request and return request ID."""
    # help_id = str(uuid.uuid4())
    # logger.info(f"Help request created: {help_id} for question: {question}")
    # # TODO: Insert into your SQL database
    return "21"


# -----------------------------
# Prewarm
# -----------------------------
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


# -----------------------------
# Custom Agent with KB Logic
# -----------------------------
class ReceptionistAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a professional receptionist assistant for a business.
            
Your responsibilities:
1. Answer caller questions using the knowledge base
2. If information isn't available, create a help request and assure the caller someone will follow up
3. Be warm, professional, and concise
4. Never make up information - only use what's provided by the lookup_information function
5: Avoid answering questions that are not related to a business

Keep responses natural and conversational without complex formatting or emojis.""",
        )

    @function_tool
    async def lookup_information(self, question: str):
        logger.info(f"🔍 Looking up: {question}")
        
        kb_result = kb_lookup(BUSINESS_ID, question)
        
        logger.info("kb_result");
        
        if kb_result["hit"] and kb_result["matches"]:
            matches = kb_result["matches"]
            
            if len(matches) == 1:
                # Single match - return directly
                answer = matches[0]["answer"]
                logger.info(f"✅ KB hit (single): {answer[:100]}...")
                return f"Based on our records: {answer}"
            else:
                # Multiple matches - combine them
                combined = "\n\n".join([
                    f"Regarding '{m['question']}': {m['answer']}" 
                    for m in matches
                ])
                logger.info(f"✅ KB hit (multiple): {len(matches)} matches")
                return f"Here's what I found:\n\n{combined}"
        else:
            # No match - create help request
            help_id = create_help_request_sql(BUSINESS_ID, question)
            logger.info(f"❌ No KB match, created help request: {help_id}")
            
            return f"""I don't have that specific information in my current knowledge base. 
I've created a help request (ID: {help_id}) and one of our team members will get back to you shortly. 
Is there anything else I can help you with in the meantime?"""


# -----------------------------
# Entry point
# -----------------------------
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    
    agent = ReceptionistAgent()
    
    session = AgentSession(
        stt=inference.STT(model="cartesia/ink-whisper", language="en"),
        llm=inference.LLM(model="openai/gpt-4.1-mini"),
        tts=inference.TTS(
            model="cartesia/sonic-3", 
            voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=False,
    )

    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(
        instructions="Greet the caller warmly and ask how you can help them today."
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))