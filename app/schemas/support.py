from typing import Literal

from pydantic import BaseModel


Intent = Literal[
    "order_status",
    "order_cancelled",
    "payment_issue",
    "refund_policy",
    "general_faq",
]


class TriageResult(BaseModel):
    intent: Intent
    complexity: Literal["simple", "complex"]
    order_id: int | None = None
    requires_order_lookup: bool
    requires_payment_lookup: bool


class SupportResponse(BaseModel):
    answer: str
    confidence: float
    needs_human: bool