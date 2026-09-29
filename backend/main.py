"""FastAPI application for the SIH26151 intelligence graph demo."""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if __package__:
    from .correlation_engine import CorrelationEngine
else:
    from correlation_engine import CorrelationEngine


app = FastAPI(
    title="SIH26151 Threat Intelligence Graph API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

correlation_engine = CorrelationEngine()


@app.get("/api/v1/graph")
def get_graph() -> dict[str, Any]:
    """Return the synthetic React Flow nodes and edges."""
    return correlation_engine.generate_graph()
