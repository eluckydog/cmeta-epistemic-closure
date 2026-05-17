"""Tool selector and pre-check functions.

select_tool: natural language -> ranked tool recommendations
check_tool_fit: pre-check input feasibility before calling a tool

Inspired by Epistemic Closure (arXiv:2603.09756):
- Constitutive Skill metadata = C_meta (needs, fails_when, gives, tags)
- Deductive Pruning = check_tool_fit refusing invalid inputs
"""

from __future__ import annotations
import json
from typing import Any, Optional

from .tool_result import ToolResult
from .registry import _TOOL_REGISTRY, _SYNONYM_MAP, get_tool_meta


def select_tool(task: str, constraints: Optional[dict] = None) -> list[dict]:
    """Given a natural language task, return ranked tool recommendations.

    Args:
        task: Natural language description of what the user wants to do.
        constraints: Optional filter dict with keys:
            - tags: [list] — only return tools with ALL these tags
            - avoid: [list] — exclude tools with ANY of these tags

    Returns:
        Sorted list of {tool, score, reasons, meta} dicts.
    """
    if constraints is None:
        constraints = {}

    tags_required = constraints.get("tags", [])
    tags_avoid = constraints.get("avoid", [])

    query_lower = task.lower()
    query_tags = set()

    # Map natural language -> tags via synonym map
    for phrase, synonyms in _SYNONYM_MAP.items():
        if phrase in query_lower:
            query_tags.update(synonyms)

    # Also add direct word matches
    for word in query_lower.split():
        if len(word) > 2:  # skip short words
            for phrase, synonyms in _SYNONYM_MAP.items():
                if word in phrase.split():
                    query_tags.update(synonyms)

    # If the task contains a known tool name or operation, add it
    for tool_name in _TOOL_REGISTRY:
        if tool_name in query_lower or tool_name.replace("_", " ") in query_lower:
            query_tags.update(_TOOL_REGISTRY[tool_name]["tags"])

    # Score each tool
    scored = []
    for tool_name, meta in _TOOL_REGISTRY.items():
        tool_tags = set(meta.get("tags", []))

        # Filter by required tags
        if tags_required and not all(t in tool_tags for t in tags_required):
            continue
        # Filter by avoided tags
        if tags_avoid and any(t in tool_tags for t in tags_avoid):
            continue

        score = 0
        reasons = []

        # Direct tag match
        matched_tags = tool_tags & query_tags
        if matched_tags:
            score += len(matched_tags)
            reasons.append(f"tags: {', '.join(sorted(matched_tags))}")

        # Keyword overlap
        tool_words = set(tool_name.replace("_", " ").split())
        query_words = set(w for w in query_lower.split() if len(w) > 3)
        word_overlap = tool_words & query_words
        if word_overlap:
            score += len(word_overlap) * 2
            reasons.append(f"token: {', '.join(sorted(word_overlap))}")

        if score > 0:
            scored.append({
                "tool": tool_name,
                "score": score,
                "reasons": "; ".join(reasons) if reasons else "default",
                "meta": {
                    "needs": meta.get("needs", []),
                    "fails_when": meta.get("fails_when", []),
                    "gives": meta.get("gives", []),
                    "warning": meta.get("warning", ""),
                },
            })

    scored.sort(key=lambda x: -x["score"])
    return scored


def check_tool_fit(tool_name: str, inputs: str | dict) -> ToolResult:
    """Pre-check whether a call to *tool_name* with *inputs* is feasible.

    Checks:
    1. Tool exists in registry
    2. Required parameters are present
    3. Tool-specific heuristics (PDE needs Derivative, matrix det=0, etc.)

    Args:
        tool_name: Exact name of the tool to check.
        inputs: Input dict (JSON string or Python dict) for the tool call.

    Returns:
        ToolResult with ok=True/False and warnings/errors.
    """
    # Parse inputs
    if isinstance(inputs, str):
        try:
            inputs = json.loads(inputs.replace("'", '"'))
        except (json.JSONDecodeError, ValueError):
            return ToolResult(
                tool=tool_name, success=False,
                error="Invalid JSON input; expected dict or JSON string",
            )

    if not isinstance(inputs, dict):
        raise TypeError("inputs must be a dict or JSON string")

    meta = get_tool_meta(tool_name)
    if meta is None:
        return ToolResult(
            tool=tool_name, success=False,
            error=f"Unknown tool '{tool_name}'. Not registered in C_meta registry. "
                  f"Registered: {', '.join(sorted(_TOOL_REGISTRY.keys()))}",
        )

    missing = []
    for need in meta.get("needs", []):
        if need not in inputs or (isinstance(inputs.get(need), str) and not inputs[need]):
            missing.append(need)

    warnings = []

    # Tool-specific heuristics
    if tool_name in ("pde_classify",):
        expr = inputs.get("expr", "") or inputs.get("expr_str", "")
        if not expr:
            missing.append("expr_str")
        elif "Derivative(" not in expr:
            return ToolResult(
                tool=tool_name, success=False,
                error="Expression lacks Derivative(); not a PDE — check will be meaningless",
            )

    if tool_name in ("expression_equivalence", "sympy_equivalent_expression"):
        expr_str = inputs.get("expr_a", "") or inputs.get("expr1", "")
        if len(expr_str) > 5000:
            warnings.append("Large expression; may timeout. Consider numeric check mode")

    if tool_name == "matrix_ops":
        mat = inputs.get("matrix_str", "")
        op = inputs.get("operation", "")
        if op == "inverse" and "det=0" in mat.lower():
            # Simple check: if user mentions singular
            warnings.append("Matrix may be singular; inverse will fail")
        if not mat:
            missing.append("matrix_str")
        if not op:
            missing.append("operation")

    if missing:
        return ToolResult(
            tool=tool_name, success=False,
            error=f"Missing required parameters: {', '.join(missing)}",
        )

    if warnings:
        return ToolResult(
            tool=tool_name, success=True,
            result="Pre-check passed with warnings",
            latex_str="; ".join(warnings),
        )

    return ToolResult(
        tool=tool_name, success=True,
        result="Pre-check passed",
    )
