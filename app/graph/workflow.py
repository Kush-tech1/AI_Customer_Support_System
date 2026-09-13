from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.agents.triage import TriageAgent
from app.agents.order_payment import OrderPaymentAgent
from app.agents.response import ResponseAgent


class SupportState(TypedDict, total=False):
    message: str
    triage: dict
    order: dict | None
    payment: dict | None
    faqs: list
    response: dict
    runtime: dict


triage_agent = TriageAgent()
order_payment_agent = OrderPaymentAgent()
response_agent = ResponseAgent()


def triage_node(state: SupportState):

    result = triage_agent.classify(
        state["message"]
    )

    return {
        "triage": result.model_dump()
    }


def order_payment_node(state: SupportState):

    triage = state["triage"]

    result = order_payment_agent.run(
        order_id=triage.get("order_id"),
        requires_order_lookup=triage["requires_order_lookup"],
        requires_payment_lookup=triage["requires_payment_lookup"],
    )

    return {
        "order": result["order"],
        "payment": result["payment"],
        "faqs": result["faqs"],
    }


def response_node(state: SupportState):
    result = response_agent.generate(
        message=state["message"],
        triage=state["triage"],
        order=state.get("order"),
        payment=state.get("payment"),
        faqs=state.get("faqs", []),
    )

    return {
        "response": result.model_dump(),
        "runtime": {
            "model": response_agent.last_model,
            "latency_ms": response_agent.last_latency_ms,
            "retries": response_agent.last_retries,
            "fallback": response_agent.last_fallback,
        },
    }

def build_graph():

    graph = StateGraph(SupportState)

    graph.add_node("triage", triage_node)
    graph.add_node("order_payment", order_payment_node)
    graph.add_node("response", response_node)

    graph.add_edge(START, "triage")
    graph.add_edge("triage", "order_payment")
    graph.add_edge("order_payment", "response")
    graph.add_edge("response", END)

    return graph.compile()


support_graph = build_graph()