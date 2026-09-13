import time

from google import genai

from app.config import config, settings


class GeminiClient:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def generate(
        self,
        model: str,
        prompt: str,
        output_schema=None,
    ) -> dict:

        # Demo-only failure simulation
        if (
            config.demo.force_model_failure
            and model == config.models.complex
        ):
            raise TimeoutError(
                "Simulated strong-model failure"
            )

        start_time = time.perf_counter()

        generation_config = None

        if output_schema:
            generation_config = {
                "response_mime_type": "application/json",
                "response_schema": output_schema,
            }

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=generation_config,
        )

        latency_ms = round(
            (time.perf_counter() - start_time) * 1000
        )

        return {
            "text": response.text,
            "model": model,
            "latency_ms": latency_ms,
        }