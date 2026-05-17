"""精简版 ToolResult 仅供 C_meta 使用"""
import json
from typing import Any, Optional


class ToolResult:
    """Minimal ToolResult for C_meta pre-check output"""
    
    def __init__(self, tool: str, success: bool, result: Any = None,
                 latex_str: str = "", error: str = ""):
        self.tool = tool
        self.success = success
        self.result = result
        self.latex_str = latex_str
        self.error = error

    def to_dict(self) -> dict:
        return {
            "tool": self.tool,
            "success": self.success,
            "result": self._serialize(self.result),
            "latex_str": self.latex_str,
            "error": self.error,
        }

    def _serialize(self, obj):
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        return str(obj)

    def to_markdown(self) -> str:
        icon = "✅" if self.success else "❌"
        md = f"{icon} **{self.tool}**: {'OK' if self.success else self.error or 'Unknown error'}"
        if self.result is not None:
            md += f"\n   Result: {self._serialize(self.result)}"
        return md
