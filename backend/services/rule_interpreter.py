from __future__ import annotations
import math
import re
from typing import Dict, Any, List, Optional


def _poly_points(fn, x0: float, x1: float, n: int = 80, scale: float = 40.0, cx: int = 400, cy: int = 260) -> List[Dict[str, int]]:
    pts: List[Dict[str, int]] = []
    step = (x1 - x0) / max(n - 1, 1)
    for i in range(n):
        x = x0 + i * step
        try:
            y = fn(x)
        except Exception:
            y = 0.0
        # Cartesian to canvas (x right, y down)
        px = int(cx + x * scale)
        py = int(cy - y * scale)
        pts.append({"x": px, "y": py})
    return pts


def _safe_parse_function(expr: str):
    # Support basic functions: x, constants, + - * / ^, pow, sin cos tan, exp, log
    expr = expr.strip().lower().replace("^", "**")
    allowed = {
        'x': 0.0,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'exp': math.exp,
        'log': math.log,
        'sqrt': math.sqrt,
        'abs': abs,
        'pi': math.pi,
        'e': math.e,
    }
    # Very limited eval context
    code = compile(expr, "<expr>", "eval")
    def fn(x: float) -> float:
        local = dict(allowed)
        local['x'] = x
        return float(eval(code, {"__builtins__": {}}, local))
    return fn


def try_parabola_tangent(command: str) -> Optional[Dict[str, Any]]:
    text = command.lower()
    if 'parabola' not in text:
        return None
    # default y=x^2
    a_match = re.search(r"tangent\s+at\s*x\s*=\s*([\-0-9\.]+)", text)
    a = float(a_match.group(1)) if a_match else None

    elements: List[Dict[str, Any]] = []
    # axes
    elements.append({"type": "line", "x": 100, "y": 260, "width": 600, "height": 0, "color": "#9ca3af"})  # x-axis
    elements.append({"type": "line", "x": 400, "y": 460, "width": 0, "height": -360, "color": "#9ca3af"})  # y-axis

    # parabola y=x^2
    pts = _poly_points(lambda x: x * x, -6, 6, n=120)
    elements.append({"type": "polyline", "points": pts, "color": "#2563eb"})

    if a is not None:
        # tangent line y = 2a(x-a) + a^2
        m = 2 * a
        b = -2 * a * a + a * a  # we will compute points directly
        x0, x1 = a - 3, a + 3
        tan_pts = _poly_points(lambda x: m * (x - a) + a * a, x0, x1, n=10)
        elements.append({"type": "polyline", "points": tan_pts, "color": "#ef4444"})
    return {"elements": elements}


def try_plot_function(command: str) -> Optional[Dict[str, Any]]:
    m = re.search(r"y\s*=\s*([^,;]+)", command, flags=re.I)
    # ONLY handle explicit mathematical equations, NOT chart type requests
    # Skip if user is asking for specific chart types (scatter, bar, histogram, etc.)
    chart_type_keywords = ["scatter", "bar chart", "histogram", "pie chart", "line chart", "box plot", "heatmap", "sankey"]
    cmd_lower = command.lower()
    if any(chart_type in cmd_lower for chart_type in chart_type_keywords):
        return None  # Let LLM handle chart type requests with Plotly
    if not m:
        return None  # Only handle explicit equations like "y = x²"
    expr = m.group(1).strip() if m else "x"
    try:
        fn = _safe_parse_function(expr)
    except Exception:
        return None
    elements: List[Dict[str, Any]] = []
    elements.append({"type": "line", "x": 100, "y": 260, "width": 600, "height": 0, "color": "#9ca3af"})
    elements.append({"type": "line", "x": 400, "y": 460, "width": 0, "height": -360, "color": "#9ca3af"})
    pts = _poly_points(fn, -6, 6, n=120)
    elements.append({"type": "polyline", "points": pts, "color": "#10b981"})
    return {"elements": elements}


def try_flowchart(command: str) -> Optional[Dict[str, Any]]:
    text = command.lower()
    if not any(k in text for k in ["flowchart", "funnel"]):
        return None
    steps = ["Awareness", "Consideration", "Signup", "Activation"] if "funnel" in text else ["Start", "Process", "End"]
    x, y = 120, 100
    gap = 90
    elements: List[Dict[str, Any]] = []
    for i, s in enumerate(steps):
        yy = y + i * gap
        elements.append({"type": "rect", "x": x, "y": yy, "width": 220, "height": 60, "color": "#e5e7eb"})
        elements.append({"type": "text", "x": x + 16, "y": yy + 18, "label": s, "color": "#111827"})
        if i < len(steps) - 1:
            elements.append({"type": "arrow", "x": x + 110, "y": yy + 60, "width": 0, "height": 30, "color": "#6b7280"})
    return {"elements": elements}


def interpret_by_rules(command: str) -> Optional[Dict[str, Any]]:
    for handler in (try_parabola_tangent, try_plot_function, try_flowchart, _try_icon_person, _try_icon_temple):
        spec = handler(command)
        if spec:
            return spec
    return None


def _try_icon_person(command: str) -> Optional[Dict[str, Any]]:
    text = command.lower()
    if not any(k in text for k in ["person", "human", "man", "woman", "stick figure", "messi"]):
        return None
    x, y = 380, 140
    elements: List[Dict[str, Any]] = []
    # Head
    elements.append({"type": "circle", "x": x, "y": y, "radius": 24, "color": "#fde68a"})
    # Body
    elements.append({"type": "line", "x": x, "y": y + 24, "width": 0, "height": 80, "color": "#111827"})
    # Arms
    elements.append({"type": "line", "x": x, "y": y + 54, "width": -40, "height": 20, "color": "#111827"})
    elements.append({"type": "line", "x": x, "y": y + 54, "width": 40, "height": 20, "color": "#111827"})
    # Legs
    elements.append({"type": "line", "x": x, "y": y + 104, "width": -30, "height": 50, "color": "#111827"})
    elements.append({"type": "line", "x": x, "y": y + 104, "width": 30, "height": 50, "color": "#111827"})
    # Ball if soccer context
    if any(k in text for k in ["soccer", "football", "messi"]):
        elements.append({"type": "circle", "x": x + 60, "y": y + 140, "radius": 12, "color": "#16a34a"})
    return {"elements": elements}


 


def _try_icon_temple(command: str) -> Optional[Dict[str, Any]]:
    text = command.lower()
    if not any(k in text for k in ["petra", "temple", "treasury", "facade"]):
        return None
    x, y = 120, 120
    w, h = 520, 240
    elements: List[Dict[str, Any]] = []
    # base and roof
    elements.append({"type": "rect", "x": x, "y": y + h - 20, "width": w, "height": 20, "color": "#d1d5db"})
    elements.append({"type": "triangle", "x": x + w/2 - 120, "y": y - 20, "width": 240, "height": 120, "color": "#fca5a5"})
    # columns (6)
    col_w = 24
    gap = (w - 6*col_w) / 7
    cx = x + gap
    for i in range(6):
        elements.append({"type": "rect", "x": int(cx + i*(col_w+gap)), "y": y + 40, "width": col_w, "height": h - 60, "color": "#fecaca"})
    # entablature
    elements.append({"type": "rect", "x": x, "y": y + 20, "width": w, "height": 20, "color": "#fca5a5"})
    return {"elements": elements}
