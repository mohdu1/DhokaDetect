"""Load the synthetic intelligence graph used by the demo API."""

import json
from pathlib import Path
from typing import Any


class CorrelationEngine:
    """Provide the demo graph through the correlation-engine interface."""

    def __init__(self, evidence_path: Path | None = None) -> None:
        self.evidence_path = evidence_path or Path(__file__).with_name(
            "synthetic_evidence.json"
        )

    def generate_graph(self) -> dict[str, Any]:
        """Load and return the graph dataset from disk."""
        with self.evidence_path.open("r", encoding="utf-8") as evidence_file:
            graph = json.load(evidence_file)

        if not isinstance(graph, dict):
            raise ValueError("Synthetic evidence must contain a JSON object.")
        if not isinstance(graph.get("nodes"), list):
            raise ValueError("Synthetic evidence must contain a nodes array.")
        if not isinstance(graph.get("edges"), list):
            raise ValueError("Synthetic evidence must contain an edges array.")

        return graph