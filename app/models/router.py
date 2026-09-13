import json
import time
import uuid

from pydantic import BaseModel

from app.config import config
from app.models.client import GeminiClient
from app.observability.logger import log_event


class ModelRouter:

    def __init__(self):
        self.client = GeminiClient()

    def select_model(self, complexity: str) -> str:
        if complexity == "complex":
            return config.models.complex

        return config.models.default

    def parse_response(self, result: dict, output_schema):
        if output_schema:
            return output_schema.model_validate(
                json.loads(result["text"])
            )

        return result["text"]

    def invoke(
        self,
        prompt: str,
        complexity: str = "simple",
        output_schema: type[BaseModel] | None = None,
        agent: str = "unknown",
    ) -> dict:

        request_id = str(uuid.uuid4())

        primary_model = self.select_model(complexity)
        max_retries = config.runtime.max_retries

        # -------------------------
        # Primary model + retries
        # -------------------------

        for retry in range(max_retries + 1):

            start = time.perf_counter()

            try:
                result = self.client.generate(
                    model=primary_model,
                    prompt=prompt,
                    output_schema=output_schema,
                )

                parsed = self.parse_response(
                    result,
                    output_schema,
                )

                latency_ms = round(
                    (time.perf_counter() - start) * 1000
                )

                log_event({
                    "request_id": request_id,
                    "agent": agent,
                    "model": primary_model,
                    "latency_ms": latency_ms,
                    "success": True,
                    "retries": retry,
                    "fallback": False,
                })

                return {
                    "response": parsed,
                    "model": primary_model,
                    "latency_ms": latency_ms,
                    "retries": retry,
                    "fallback": False,
                    "success": True,
                }

            except Exception as error:

                log_event({
                    "request_id": request_id,
                    "agent": agent,
                    "model": primary_model,
                    "latency_ms": round(
                        (time.perf_counter() - start) * 1000
                    ),
                    "success": False,
                    "retries": retry + 1,
                    "fallback": False,
                    "error": str(error),
                })

        # -------------------------
        # Fallback model
        # -------------------------

        fallback_model = config.models.fallback

        start = time.perf_counter()

        try:
            result = self.client.generate(
                model=fallback_model,
                prompt=prompt,
                output_schema=output_schema,
            )

            parsed = self.parse_response(
                result,
                output_schema,
            )

            latency_ms = round(
                (time.perf_counter() - start) * 1000
            )

            log_event({
                "request_id": request_id,
                "agent": agent,
                "model": fallback_model,
                "latency_ms": latency_ms,
                "success": True,
                "retries": max_retries,
                "fallback": True,
            })

            return {
                "response": parsed,
                "model": fallback_model,
                "latency_ms": latency_ms,
                "retries": max_retries,
                "fallback": True,
                "success": True,
            }

        except Exception as error:

            log_event({
                "request_id": request_id,
                "agent": agent,
                "model": fallback_model,
                "latency_ms": round(
                    (time.perf_counter() - start) * 1000
                ),
                "success": False,
                "retries": max_retries,
                "fallback": True,
                "error": str(error),
            })

            return {
                "response": None,
                "model": fallback_model,
                "latency_ms": 0,
                "retries": max_retries,
                "fallback": True,
                "success": False,
                "error": str(error),
            }