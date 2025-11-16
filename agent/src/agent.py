import logging
from dotenv import load_dotenv
import random 
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
from logging_config import setup_logging


import os
import uuid
from typing import List, Dict
from services.kb_service import KnowledgeBaseService
from services.help_service import HelpRequestService


setup_logging()
load_dotenv(".env.local")

logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)

BUSINESS_ID = 1

kb_service = KnowledgeBaseService()
help_service = HelpRequestService()


# Prewarm
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


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
        logger.info(f"Searching for -: {question}")
        logger.info("\n\n\n")


        kb_result = kb_service.search(BUSINESS_ID, question)

        logger.info(f"kb_result: {kb_result}")
        
        if kb_result.hit and kb_result.matches:
            matches = kb_result.matches
            
            if len(matches) == 1:
                answer = matches[0].answer
                logger.info(f"KB hit (single): {answer[:100]}...")
                return f"Based on our records: {answer}"
            else:
                combined = "\n\n".join([
                    f"Regarding '{m.question}': {m.answer}" 
                    for m in matches
                ])
                logger.info(f"KB hit (multiple): {len(matches)} matches")
                return f"Here's what I found:\n\n{combined}"
        else:
            try:
                help_request = help_service.create_request(question, BUSINESS_ID, 1)
                return f"""I don't have that specific information currently "Let me check with my supervisor and get back to you.". 
Is there anything else I can help you with in the meantime?"""
            except Exception as e:
                logger.error(f"Failed to create help request: {e}")
                return "I'm sorry, I couldn't create a help request at this time. Please try again later."


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