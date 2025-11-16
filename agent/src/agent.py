import logging
from dotenv import load_dotenv
import asyncio
import json
import os

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    inference,
    function_tool,
)

from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from logging_config import setup_logging

from services.kb_service import KnowledgeBaseService
from services.help_service import HelpRequestService

import redis.asyncio as aioredis


setup_logging()
load_dotenv(".env.local")
logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)

REDIS_URL = os.getenv("REDIS_URL")
redis = aioredis.from_url(REDIS_URL, decode_responses=True)
SUPERVISOR_CHANNEL = "supervisor_answers"


# Business Services 
# Hardcoding business id for dev 
BUSINESS_ID = 1
kb_service = KnowledgeBaseService()
help_service = HelpRequestService()


# Prewarm
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


# Agent Definition
class ReceptionistAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a professional receptionist assistant for a business.
Your responsibilities:
1. Answer caller questions using the knowledge base
2. If information isn't available, create a help request and assure the caller to wait while you get their answer
3. Be warm, professional, and concise
4. Never make up information - only use what's provided by the lookup_information function
5: Avoid answering questions that are not related to a business
Keep responses natural and conversational without complex formatting or emojis"""
        )

    @function_tool
    async def lookup_information(self, question: str):

        #get KB in memory and rank results return if matches found
        kb_result = kb_service.search(BUSINESS_ID, question)
        logger.info(f"kb_result: {kb_result}")

        if kb_result.hit and kb_result.matches:
            match = kb_result.matches[0]
            return f"Based on our records: {match.answer}"
        

        # we can make  it async to optimize agent reply speed
        try:
            help_request = help_service.create_request(question, BUSINESS_ID, 1)
            logger.info(f"Created help request: {help_request.id}")

            return (
                "I don't have that information right now. "
                "Let me check with my supervisor and get back to you shortly."
            )
        except Exception as e:
            logger.error(f"Failed to create help request: {e}")
            return "I couldn't create a help request. Please try again later."


# Redis Listener Background Task
async def listen_for_supervisor_updates(agent_session: AgentSession):
    pubsub = redis.pubsub()
    await pubsub.subscribe(SUPERVISOR_CHANNEL)

    logger.info("\n--------------------------\n"
                "Subscribed to Redis channel\n"
                "--------------------------")

    async for message in pubsub.listen():

        if message["type"] != "message":
            continue

        raw = message["data"]

        # Decode bytes → string
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="ignore").strip()

        # Skip noise from Redis
        if raw in ["1", "2", "subscribe", "unsubscribe", "message", ""]:
            logger.info(f"Ignoring non-JSON payload: {raw!r}")
            continue

        # Try loading JSON safely
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.error("\n------------------------------\n"
                         f"⚠️ Invalid JSON received:\n{raw}\n"
                         "------------------------------")
            continue

        logger.info("\n================ SUPERVISOR UPDATE ================\n"
                    f"{json.dumps(data, indent=2)}\n"
                    "===================================================")

        # Ensure it's actually a dict
        if not isinstance(data, dict):
            logger.error(f"Received non-dict JSON: {data}")
            continue

        # Business ID filter
    
        if int(data.get("business_id", -1)) != BUSINESS_ID:
            continue

        # Notify caller
        await agent_session.generate_reply(
        instructions=(
            "Tell the caller that you have the data they requested for regrading "
            f'{data.get("answer")}. '
            "Frame the reply as someone from the team letting the user knwo about the data they requested"
        )
)

# entrypoint
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    agent = ReceptionistAgent()

    session = AgentSession(
        stt=inference.STT(model="cartesia/ink-whisper", language="en"),
        llm=inference.LLM(model="openai/gpt-4.1-mini"),
        tts=inference.TTS(model="cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=False,
    )

    asyncio.create_task(listen_for_supervisor_updates(session))

    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )

    await session.generate_reply(
        instructions="Greet the caller warmly and ask how you can help them today."
    )


# Main
if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm)
    )
