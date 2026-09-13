import logging
import json


logger = logging.getLogger("support_ai")

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


def log_event(event: dict):
    logger.info(
        json.dumps(event)
    )