import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    noisy_libs = [
        "livekit",
        "livekit.agents",
        "livekit.plugins",
        "httpx",
        "httpcore",
        "openai",
        "urllib3",
        "asyncio"
    ]

    for lib in noisy_libs:
        logging.getLogger(lib).setLevel(logging.WARNING)
