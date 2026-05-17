"""cmeta-epistemic-closure

Tool self-awareness framework inspired by Epistemic Closure (arXiv:2603.09756).
Every tool declares its C_meta: scope, preconditions, failure modes.
Select/check before execution — refuse blind execution in invalid domains.
"""

from .tool_result import ToolResult
from .registry import (_TOOL_REGISTRY, _SYNONYM_MAP, get_supported_tools, get_tool_meta)
from .selector import select_tool, check_tool_fit

__version__ = "0.2.0"
__all__ = [
    "ToolResult",
    "_TOOL_REGISTRY", "_SYNONYM_MAP",
    "get_supported_tools", "get_tool_meta",
    "select_tool", "check_tool_fit",
]
