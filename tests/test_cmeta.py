"""Self-diagnostic: verify C_meta registry is self-consistent."""

from cmeta import (
    _TOOL_REGISTRY, _SYNONYM_MAP,
    select_tool, check_tool_fit, ToolResult,
)


def test_registry_consistency():
    """Every tool must have all 4 C_meta fields."""
    required = {"needs", "fails_when", "gives", "tags"}
    for name, meta in _TOOL_REGISTRY.items():
        missing = required - set(meta.keys())
        assert not missing, f"{name}: missing fields {missing}"
    print(f"✅ Registry: {len(_TOOL_REGISTRY)} tools, all have complete C_meta")


def test_select():
    tests = [
        ("solve PDE", "pde_classify"),
        ("differentiate", "diff"),
        ("integrate x^2", "integrate"),
        ("solve equation", "solve"),
        ("matrix determinant", "matrix_ops"),
    ]
    for task, expected in tests:
        results = select_tool(task)
        assert len(results) > 0, f"{task}: no results"
        assert any(r["tool"] == expected for r in results[:3]), \
            f"{task}: expected {expected}, got {[r['tool'] for r in results[:3]]}"
    print(f"✅ select: {len(tests)} natural language queries OK")


def test_check_valid():
    """Valid inputs should pass check."""
    cases = [
        ("pde_classify", {"expr_str": "Derivative(f(x,y),x) + Derivative(f(x,y),y) + f"}, True),
        ("solve", {"expr_str": "x**2 - 4", "variable": "x"}, True),
        ("diff", {"expr_str": "x**3", "variable": "x"}, True),
    ]
    for tool, inputs, expected in cases:
        r = check_tool_fit(tool, inputs)
        assert r.success == expected, \
            f"{tool}({inputs}): expected {expected}, got {r.success}: {r.error}"
    print("✅ check_valid: all passed")


def test_check_fail():
    """Invalid inputs should be rejected."""
    cases = [
        ("pde_classify", {"expr_str": "x + y"}, False, "Derivative"),  # no Derivative
        ("nonexistent_tool", {"x": 1}, False, "Unknown tool"),
        ("matrix_ops", {"matrix_str": "[[1,2],[3,4]]"}, False, "operation"),  # missing op
    ]
    for tool, inputs, expected_ok, hint in cases:
        r = check_tool_fit(tool, inputs)
        assert r.success == expected_ok, \
            f"{tool}({inputs}): expected ok={expected_ok}, got {r.error}"
        assert hint.lower() in r.error.lower(), \
            f"{tool}: expected hint '{hint}' in '{r.error}'"
    print(f"✅ check_fail: {len(cases)} rejection tests OK")


def test_tool_result_format():
    """ToolResult should produce valid markdown and dict."""
    tr = ToolResult("test", True, result=42)
    md = tr.to_markdown()
    assert "✅" in md and "test" in md
    d = tr.to_dict()
    assert d["tool"] == "test" and d["success"] is True
    print("✅ ToolResult: markdown and dict format OK")


if __name__ == "__main__":
    test_registry_consistency()
    test_select()
    test_check_valid()
    test_check_fail()
    test_tool_result_format()
    print("\n🎯 All C_meta tests passed")
