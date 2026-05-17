"""C_META TOOL REGISTRY — v2.2 MVP

Inspired by Epistemic Closure (arXiv:2603.09756).
Every tool declares its C_meta metadata: scope, preconditions, failure modes.

A Constitutive Skill = {
    "needs": [list of required input fields],
    "fails_when": [list of conditions that cause failure],
    "gives": [list of output/effects],
    "tags": [list of natural language keywords],
    "warning": "optional human-readable caution message",
}
"""

from __future__ import annotations
import sys
import json
from typing import Any, Optional

from .tool_result import ToolResult


# ───── Registry ─────

_TOOL_REGISTRY = {
    # ── Calculus / Analysis ──
    "parse_expression": {
        "needs": ["expr_str"],
        "fails_when": ["invalid syntax", "unsupported operator", "empty string"],
        "gives": ["SymPy expression object"],
        "tags": ["parse", "expression", "string to sympy", "read"],
        "warning": "Only supports standard math operators +-*/^ and common functions",
    },
    "diff": {
        "needs": ["expr_str", "variable"],
        "fails_when": ["non-differentiable expression", "ambiguous variable"],
        "gives": ["differentiated expression (SymPy)", "LaTeX string of derivative"],
        "tags": ["diff", "derivative", "differentiate", "gradient"],
    },
    "integrate": {
        "needs": ["expr_str", "variable"],
        "fails_when": ["non-integrable in closed form", "divergent integral"],
        "gives": ["integrated expression (SymPy)", "LaTeX string of integral"],
        "tags": ["integrate", "integral", "antiderivative", "definite integral"],
    },
    "limits": {
        "needs": ["expr_str", "variable", "approach"],
        "fails_when": ["oscillating limit", "essential singularity", "branch cut ambiguity"],
        "gives": ["limit value (SymPy)", "LaTeX string of limit"],
        "tags": ["limit", "limits", "approach", "tend to"],
    },
    "series_expansion": {
        "needs": ["expr_str", "variable", "point", "order"],
        "fails_when": ["non-analytic at expansion point", "essential singularity"],
        "gives": ["series expansion (SymPy)", "truncated series terms", "LaTeX"],
        "tags": ["series", "expand", "taylor", "laurent", "expansion"],
    },
    "symbolic_summation": {
        "needs": ["expr_str", "index_var", "lower", "upper"],
        "fails_when": ["divergent sum", "non-closed-form sum"],
        "gives": ["sum expression (SymPy)", "LaTeX string"],
        "tags": ["sum", "summation", "sigma", "series sum"],
    },

    # ── Solving ──
    "solve": {
        "needs": ["expr_str", "variable"],
        "fails_when": ["no closed-form solution", "transcendental without special functions",
                       "overconstrained system"],
        "gives": ["list of solution expressions (SymPy)", "substituted results"],
        "tags": ["solve", "equation", "root", "solution", "find root"],
        "warning": "For non-polynomial equations, may return numeric approximations",
    },
    "solve_ode": {
        "needs": ["eq_str", "function_symbol", "variable"],
        "fails_when": ["not an ODE", "no closed-form solution available",
                       "highly nonlinear/non-standard ODE"],
        "gives": ["solution expression(s) (SymPy)", "classification string"],
        "tags": ["ode", "ordinary differential equation", "solve ode"],
        "warning": "dsolve may return implicit or unsolved forms",
    },
    "pde_classify": {
        "needs": ["expr_str"],
        "fails_when": ["no Derivative() found in expression",
                       "expression is not a valid PDE"],
        "gives": ["classification string (elliptic/parabolic/hyperbolic)",
                  "order, linearity, coefficients, checkability report"],
        "tags": ["pde", "classification", "partial differential equation", "type"],
        "warning": "Classification only valid for second-order linear PDEs",
    },
    "recurrence_solve": {
        "needs": ["eq_str", "function_symbol", "index_var"],
        "fails_when": ["non-linear recurrence", "no closed form"],
        "gives": ["closed form (SymPy)"],
        "tags": ["recurrence", "recurrence relation", "difference equation"],
    },

    # ── Algebra / Number Theory ──
    "factorize": {
        "needs": ["expr_str"],
        "fails_when": ["prime/irreducible over integers", "very large expression (>1M nodes)"],
        "gives": ["factorized expression (SymPy)", "LaTeX string"],
        "tags": ["factor", "factorize", "factorisation", "prime factor"],
        "warning": "Large expressions may be slow; use numeric mode for huge inputs",
    },
    "gcd_lcm": {
        "needs": ["a_expr", "b_expr"],
        "fails_when": ["non-polynomial expressions"],
        "gives": ["gcd/lcm expression (SymPy)"],
        "tags": ["gcd", "lcm", "greatest common divisor", "least common multiple"],
    },

    # ── Linear Algebra ──
    "matrix_ops": {
        "needs": ["matrix_str", "operation"],
        "fails_when": ["singular matrix for inverse", "non-square matrix for det",
                       "dimension mismatch", "format errors"],
        "gives": ["result value/matrix (SymPy)", "LaTeX string"],
        "tags": ["matrix", "determinant", "inverse", "transpose", "linear algebra"],
        "warning": "Inverse requires non-singular square matrix",
    },

    # ── Physics ──
    "quantum_commutator": {
        "needs": ["A_str", "B_str", "commutation_rules"],
        "fails_when": ["non-linear operators", "inconsistent commutation rules"],
        "gives": ["commutator expression [A,B] (SymPy)", "simplified form"],
        "tags": ["quantum", "commutator", "operator", "commutation"],
    },
    "physical_units": {
        "needs": ["value", "from_unit", "to_unit"],
        "fails_when": ["incompatible dimensions", "unknown unit"],
        "gives": ["converted value", "dimension string"],
        "tags": ["unit", "convert", "physical unit", "dimension"],
    },

    # ── Statistics / Geometry ──
    "distributions": {
        "needs": ["dist_name"],
        "fails_when": ["unknown distribution name"],
        "gives": ["PDF/CDF formulas (SymPy)", "moment formulas", "parameter descriptions"],
        "tags": ["distribution", "probability", "statistics", "pdf", "cdf"],
    },
    "geometry_measure": {
        "needs": ["shape", "measure_type"],
        "fails_when": ["unknown shape", "undefined measure"],
        "gives": ["formula expression (SymPy)", "substituted numeric value"],
        "tags": ["geometry", "area", "volume", "perimeter", "measure"],
    },
}

_SYNONYM_MAP = {
    "derivative": ["diff", "derivative", "differentiate"],
    "integral": ["integrate", "integral", "antiderivative"],
    "limit": ["limit", "limits", "approach"],
    "series": ["series", "expand", "taylor", "laurent"],
    "differential equation": ["ode", "pde", "differential"],
    "pde": ["pde", "partial differential equation"],
    "solve": ["solve", "root", "solution", "equation"],
    "factor": ["factor", "factorize", "factorisation"],
    "matrix": ["matrix", "linear algebra", "determinant", "inverse"],
    "sum": ["sum", "summation", "sigma"],
    "recurrence": ["recurrence", "recurrence relation", "difference equation"],
    "quantum": ["quantum", "commutator", "operator"],
    "unit": ["unit", "convert", "physical"],
    "distribution": ["distribution", "probability", "statistics"],
    "geometry": ["geometry", "area", "volume"],
    "gcd": ["gcd", "lcm", "greatest common divisor"],
}


def get_supported_tools() -> dict:
    """Return a copy of the full registry."""
    return dict(_TOOL_REGISTRY)


def get_tool_meta(tool_name: str) -> Optional[dict]:
    """Look up a tool's C_meta by exact name."""
    return _TOOL_REGISTRY.get(tool_name)
