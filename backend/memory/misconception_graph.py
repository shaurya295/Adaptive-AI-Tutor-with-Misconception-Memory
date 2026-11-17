"""
misconception_graph.py
----------------------
The concept prerequisite graph: which concepts a student needs before another.

The graph is curated content, so it lives in one file,
backend/content/concepts.json, whose names match the topics shown in the UI.
It is read once and kept in memory; no database is needed to use it.

    "Fractions": ["Comparing Unit Fractions", "Common Denominators"]
means Fractions REQUIRES each of the two concepts on the right.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

_GRAPH_FILE = Path(__file__).resolve().parents[1] / "content" / "concepts.json"


@lru_cache(maxsize=1)
def _graph() -> Dict[str, List[str]]:
    return json.loads(_GRAPH_FILE.read_text(encoding="utf-8"))


def get_prerequisites(concept: str) -> List[str]:
    """Direct prerequisites of a concept ([] if it has none or is unknown)."""
    return list(_graph().get(concept, []))


def get_deep_prerequisites(concept: str) -> List[str]:
    """Every prerequisite reachable from a concept, nearest first, without repeats."""
    seen: List[str] = []
    queue = get_prerequisites(concept)
    while queue:
        name = queue.pop(0)
        if name not in seen and name != concept:
            seen.append(name)
            queue.extend(get_prerequisites(name))
    return seen


def get_all_concepts() -> List[str]:
    names: List[str] = []
    for concept, prereqs in _graph().items():
        for name in [concept, *prereqs]:
            if name not in names:
                names.append(name)
    return names


def get_all_edges() -> List[Tuple[str, str]]:
    """(concept, prerequisite) pairs."""
    return [(concept, prereq) for concept, prereqs in _graph().items() for prereq in prereqs]


if __name__ == "__main__":
    for name in get_all_concepts():
        print(f"{name}: direct={get_prerequisites(name)} deep={get_deep_prerequisites(name)}")
