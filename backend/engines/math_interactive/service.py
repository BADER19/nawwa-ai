"""
Interactive Math Visualization Service
Computes function data, derivatives, integrals, and critical points using SymPy and NumPy
Returns JSON data for frontend interactive plotting (Plotly)
"""
import numpy as np
import sympy as sp
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger("math_interactive")


def parse_expression(expr_str: str, variables: Optional[List[str]] = None) -> Tuple[sp.Expr, List[sp.Symbol]]:
    """
    Parse a mathematical expression string into a SymPy expression.

    Args:
        expr_str: Expression like "x**2 - 4*x + 3" or "sin(x)"
        variables: List of variable names (default: ['x'])

    Returns:
        (sympy_expr, list_of_symbols)
    """
    if variables is None:
        variables = ['x']

    # Create symbols
    symbols = {var: sp.Symbol(var, real=True) for var in variables}

    # Replace common notation
    expr_str = expr_str.replace('^', '**')

    # Parse expression
    try:
        expr = sp.sympify(expr_str, locals=symbols)
        return expr, [symbols[var] for var in variables]
    except Exception as e:
        logger.error(f"Failed to parse expression '{expr_str}': {e}")
        raise ValueError(f"Invalid expression: {expr_str}")


def evaluate_function(expr: sp.Expr, symbol: sp.Symbol, x_range: Tuple[float, float], num_points: int = 500) -> Dict[str, List[float]]:
    """
    Evaluate a function over a range and return x, y arrays.

    Args:
        expr: SymPy expression
        symbol: Variable symbol (e.g., x)
        x_range: (min, max) tuple
        num_points: Number of points to sample

    Returns:
        {"x": [...], "y": [...]}
    """
    x_vals = np.linspace(x_range[0], x_range[1], num_points)

    # Convert SymPy expression to numpy-compatible function
    func = sp.lambdify(symbol, expr, modules=['numpy'])

    try:
        y_vals = func(x_vals)

        # Handle complex results or infinities
        if np.iscomplexobj(y_vals):
            y_vals = np.real(y_vals)

        # Filter out infinities and NaNs
        mask = np.isfinite(y_vals)
        x_filtered = x_vals[mask].tolist()
        y_filtered = y_vals[mask].tolist()

        return {"x": x_filtered, "y": y_filtered}
    except Exception as e:
        logger.warning(f"Error evaluating function: {e}")
        return {"x": [], "y": []}


def find_critical_points(expr: sp.Expr, symbol: sp.Symbol, x_range: Tuple[float, float]) -> List[Dict[str, Any]]:
    """
    Find critical points (local minima/maxima) of a function.

    Returns:
        [{"x": 2.0, "y": -1.0, "label": "local minimum", "type": "min"}, ...]
    """
    critical_points = []

    try:
        # Compute first derivative
        derivative = sp.diff(expr, symbol)

        # Find critical points (where derivative = 0)
        critical_x = sp.solve(derivative, symbol)

        # Compute second derivative for classification
        second_derivative = sp.diff(derivative, symbol)

        for x_val in critical_x:
            try:
                # Evaluate if it's a real number in range
                x_float = float(x_val.evalf())

                if x_range[0] <= x_float <= x_range[1]:
                    # Evaluate y value
                    y_float = float(expr.subs(symbol, x_val).evalf())

                    # Classify using second derivative test
                    second_deriv_val = second_derivative.subs(symbol, x_val).evalf()

                    if second_deriv_val > 0:
                        point_type = "min"
                        label = "local minimum"
                    elif second_deriv_val < 0:
                        point_type = "max"
                        label = "local maximum"
                    else:
                        point_type = "inflection"
                        label = "inflection point"

                    critical_points.append({
                        "x": round(x_float, 4),
                        "y": round(y_float, 4),
                        "label": label,
                        "type": point_type
                    })
            except Exception as e:
                logger.debug(f"Skipping critical point {x_val}: {e}")
                continue
    except Exception as e:
        logger.warning(f"Error finding critical points: {e}")

    return critical_points


def find_roots(expr: sp.Expr, symbol: sp.Symbol, x_range: Tuple[float, float]) -> List[Dict[str, Any]]:
    """
    Find roots (x-intercepts) of a function.

    Returns:
        [{"x": 1.0, "y": 0.0, "label": "root"}, ...]
    """
    roots = []

    try:
        # Solve for roots
        solutions = sp.solve(expr, symbol)

        for sol in solutions:
            try:
                x_float = float(sol.evalf())

                if x_range[0] <= x_float <= x_range[1]:
                    roots.append({
                        "x": round(x_float, 4),
                        "y": 0.0,
                        "label": "root",
                        "type": "root"
                    })
            except Exception:
                continue
    except Exception as e:
        logger.warning(f"Error finding roots: {e}")

    return roots


def find_y_intercept(expr: sp.Expr, symbol: sp.Symbol) -> Optional[Dict[str, Any]]:
    """
    Find y-intercept (where x=0).

    Returns:
        {"x": 0.0, "y": 3.0, "label": "y-intercept"}
    """
    try:
        y_val = float(expr.subs(symbol, 0).evalf())
        return {
            "x": 0.0,
            "y": round(y_val, 4),
            "label": "y-intercept",
            "type": "intercept"
        }
    except Exception as e:
        logger.debug(f"No y-intercept found: {e}")
        return None


def compute_derivative(expr: sp.Expr, symbol: sp.Symbol, x_range: Tuple[float, float], num_points: int = 500) -> Dict[str, Any]:
    """
    Compute the derivative of an expression.

    Returns:
        {"expression": "2*x - 4", "points": {"x": [...], "y": [...]}}
    """
    try:
        derivative = sp.diff(expr, symbol)
        points = evaluate_function(derivative, symbol, x_range, num_points)

        return {
            "expression": str(derivative),
            "points": points
        }
    except Exception as e:
        logger.warning(f"Error computing derivative: {e}")
        return {"expression": "", "points": {"x": [], "y": []}}


def compute_integral(expr: sp.Expr, symbol: sp.Symbol, x_range: Tuple[float, float], num_points: int = 500) -> Dict[str, Any]:
    """
    Compute the indefinite integral of an expression.

    Returns:
        {"expression": "x**3/3 - 2*x**2 + 3*x", "points": {"x": [...], "y": [...]}}
    """
    try:
        integral = sp.integrate(expr, symbol)
        points = evaluate_function(integral, symbol, x_range, num_points)

        return {
            "expression": str(integral),
            "points": points
        }
    except Exception as e:
        logger.warning(f"Error computing integral: {e}")
        return {"expression": "", "points": {"x": [], "y": []}}


def extract_parameters(expr: sp.Expr, exclude_vars: List[str] = None) -> List[str]:
    """
    Extract parameter symbols from an expression (e.g., a, b, c in a*x**2 + b*x + c).

    Args:
        expr: SymPy expression
        exclude_vars: Variables to exclude (e.g., ['x'])

    Returns:
        List of parameter names
    """
    if exclude_vars is None:
        exclude_vars = ['x']

    all_symbols = expr.free_symbols
    parameters = [str(sym) for sym in all_symbols if str(sym) not in exclude_vars]

    return sorted(parameters)


def generate_math_data(
    expression: str,
    x_range: Optional[Tuple[float, float]] = None,
    y_range: Optional[Tuple[float, float]] = None,
    include_derivative: bool = False,
    include_integral: bool = False,
    include_annotations: bool = True,
    parameters: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Main function to generate all mathematical data for an expression.

    Args:
        expression: Math expression like "x**2 - 4*x + 3"
        x_range: (min, max) for x-axis, default: (-10, 10)
        y_range: (min, max) for y-axis (for display only)
        include_derivative: Whether to compute derivative
        include_integral: Whether to compute integral
        include_annotations: Whether to find critical points, roots, etc.
        parameters: Dict of parameter values for substitution (e.g., {"a": 2, "b": -4})

    Returns:
        {
            "function": {"points": {"x": [...], "y": [...]}, "expression": "..."},
            "derivative": {"points": {...}, "expression": "..."},
            "integral": {"points": {...}, "expression": "..."},
            "annotations": [...],
            "parameters": ["a", "b", "c"],
            "x_range": [-10, 10],
            "y_range": [-10, 10]
        }
    """
    if x_range is None:
        x_range = (-10, 10)

    if y_range is None:
        y_range = (-10, 10)

    # Parse expression
    expr, symbols = parse_expression(expression)
    symbol = symbols[0]  # Use first symbol as main variable

    # Substitute parameters if provided
    if parameters:
        for param, value in parameters.items():
            expr = expr.subs(sp.Symbol(param), value)

    # Extract remaining parameters (after substitution)
    param_names = extract_parameters(expr, exclude_vars=[str(symbol)])

    # Evaluate main function
    function_points = evaluate_function(expr, symbol, x_range)

    result = {
        "function": {
            "points": function_points,
            "expression": str(expr)
        },
        "x_range": list(x_range),
        "y_range": list(y_range),
        "parameters": param_names
    }

    # Compute derivative if requested
    if include_derivative:
        result["derivative"] = compute_derivative(expr, symbol, x_range)

    # Compute integral if requested
    if include_integral:
        result["integral"] = compute_integral(expr, symbol, x_range)

    # Find annotations if requested
    if include_annotations:
        annotations = []

        # Find critical points
        critical = find_critical_points(expr, symbol, x_range)
        annotations.extend(critical)

        # Find roots
        roots = find_roots(expr, symbol, x_range)
        annotations.extend(roots)

        # Find y-intercept
        y_int = find_y_intercept(expr, symbol)
        if y_int:
            annotations.append(y_int)

        result["annotations"] = annotations

    return result
