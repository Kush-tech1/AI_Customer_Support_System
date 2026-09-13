from app.models.router import ModelRouter
from app.schemas.support import TriageResult


class TriageAgent:

    def __init__(self):
        self.router = ModelRouter()

    def classify(self, message: str) -> TriageResult:

        prompt = f"""
You are a customer support triage agent.

Classify the customer's request.

Possible intents:
- order_status
- order_cancelled
- payment_issue
- refund_policy
- general_faq

Rules:

1. Use "simple" for straightforward questions.
2. Use "complex" when the request involves:
   - payment problems
   - cancellation + payment
   - disputes
   - multiple related issues
3. Extract the order ID if explicitly present.
4. Never invent an order ID.
5. Set requires_order_lookup to true when order information is needed.
6. Set requires_payment_lookup to true when payment information is needed.

Customer message:
{message}
"""

        result = self.router.invoke(
            prompt=prompt,
            complexity="simple",
            output_schema=TriageResult,
            agent="triage",
        )

        if not result["success"]:
            raise RuntimeError(
                f"Triage failed: {result.get('error')}"
            )

        return result["response"]