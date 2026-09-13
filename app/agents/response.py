from app.models.router import ModelRouter
from app.schemas.support import SupportResponse


class ResponseAgent:

    def __init__(self):
        self.router = ModelRouter()

        self.last_model = None
        self.last_latency_ms = None
        self.last_retries = None
        self.last_fallback = None

    def generate(
        self,
        message: str,
        triage: dict,
        order: dict | None,
        payment: dict | None,
        faqs: list,
    ) -> SupportResponse:

        prompt = f"""
You are a customer support response agent.

Answer the customer's question using ONLY the
information provided below.

Customer message:
{message}

Triage:
{triage}

Order:
{order}

Payment:
{payment}

FAQ / Policies:
{faqs}

Rules:
- Never invent information.
- Be concise and helpful.
- Use the FAQ/policy information when relevant.
- If an order was cancelled and payment was captured,
  explain the refund process.
- If the policy says refunds take 5 business days,
  include that timeframe.
- Only set needs_human=true if the available information
  is genuinely insufficient or the case requires manual review.
"""

        result = self.router.invoke(
            prompt=prompt,
            complexity=triage["complexity"],
            output_schema=SupportResponse,
            agent="response",
        )

        if not result["success"]:
            raise RuntimeError(
                f"Response generation failed: {result.get('error')}"
            )

        # Store runtime metadata for the graph/API
        self.last_model = result["model"]
        self.last_latency_ms = result["latency_ms"]
        self.last_retries = result["retries"]
        self.last_fallback = result["fallback"]

        return result["response"]