from fastapi import FastAPI
from pydantic import BaseModel

from app.graph.workflow import support_graph


app = FastAPI(
    title="AI Customer Support Platform",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/support")
def support(request: ChatRequest):
    result = support_graph.invoke({
        "message": request.message
    })

    return {
        "answer": result["response"]["answer"],
        "intent": result["triage"]["intent"],
        "complexity": result["triage"]["complexity"],
        "order_id": result["triage"]["order_id"],
        "confidence": result["response"]["confidence"],
        "needs_human": result["response"]["needs_human"],
        "runtime": result["runtime"],
    }