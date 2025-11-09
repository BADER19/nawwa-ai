import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional

def generate_math_plot(elements: List[Dict[str, Any]]) -> str:
    """
    Generate a mathematical plot from element specifications and return as base64 PNG.

    Elements can be:
    - axes: {type:'axes', xRange:[-5,5], yRange:[-1,10], xLabel:'x', yLabel:'y'}
    - function: {type:'function', expression:'x**2', domain:[-5,5], color:'#2563eb', label:'y=x²'}
    - point: {type:'point', x:2, y:4, label:'local minimum', color:'#ef4444'}
    - annotation: {type:'annotation', x:2, y:4, text:'minimum at (2,4)', anchor:'top'}
    """
    # Find axes configuration
    axes_el = next((e for e in elements if e.get('type') == 'axes'), None)
    x_range = axes_el.get('xRange', [-10, 10]) if axes_el else [-10, 10]
    y_range = axes_el.get('yRange', [-10, 10]) if axes_el else [-10, 10]
    x_label = axes_el.get('xLabel', 'x') if axes_el else 'x'
    y_label = axes_el.get('yLabel', 'y') if axes_el else 'y'

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Set up axes
    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.axhline(y=0, color='#888888', linewidth=1)
    ax.axvline(x=0, color='#888888', linewidth=1)

    # Process each element
    for el in elements:
        el_type = el.get('type', '')

        if el_type == 'function' and el.get('expression'):
            # Plot function
            expression = el['expression']
            domain = el.get('domain', x_range)
            color = el.get('color', '#2563eb')
            label = el.get('label', expression)

            # Generate x values
            x_vals = np.linspace(domain[0], domain[1], 500)

            try:
                # Evaluate expression safely
                # Replace common math notation with numpy equivalents
                expr = expression.replace('^', '**')

                # Create safe namespace with numpy functions
                namespace = {
                    'x': x_vals,
                    'np': np,
                    'sin': np.sin,
                    'cos': np.cos,
                    'tan': np.tan,
                    'exp': np.exp,
                    'log': np.log,
                    'sqrt': np.sqrt,
                    'abs': np.abs,
                    'pi': np.pi,
                    'e': np.e,
                }

                # Evaluate expression
                y_vals = eval(expr, {"__builtins__": {}}, namespace)

                # Plot the function
                ax.plot(x_vals, y_vals, color=color, linewidth=2, label=label)

            except Exception as e:
                print(f"Error plotting function {expression}: {e}")
                continue

        elif el_type == 'point' and el.get('x') is not None and el.get('y') is not None:
            # Plot point
            x_pt = el['x']
            y_pt = el['y']
            color = el.get('color', '#ef4444')
            label = el.get('label', '')

            ax.plot(x_pt, y_pt, 'o', color=color, markersize=10, label=label if label else None, zorder=5)

            # Add label next to point
            if label:
                ax.annotate(
                    label,
                    xy=(x_pt, y_pt),
                    xytext=(10, 10),
                    textcoords='offset points',
                    fontsize=10,
                    color=color,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, alpha=0.8)
                )

        elif el_type == 'annotation' and el.get('x') is not None and el.get('y') is not None:
            # Add annotation
            x_ann = el['x']
            y_ann = el['y']
            text = el.get('text', '')
            color = el.get('color', '#374151')
            anchor = el.get('anchor', 'center')

            # Map anchor to matplotlib position
            ha_map = {'left': 'right', 'right': 'left', 'center': 'center'}
            va_map = {'top': 'bottom', 'bottom': 'top', 'middle': 'center'}
            ha = ha_map.get(anchor, 'center')
            va = va_map.get(anchor, 'center')

            ax.annotate(
                text,
                xy=(x_ann, y_ann),
                xytext=(15, 15),
                textcoords='offset points',
                fontsize=10,
                color=color,
                ha=ha,
                va=va,
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, alpha=0.9)
            )

    # Add legend if there are labeled items
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(loc='upper right', framealpha=0.9, fontsize=10)

    # Tight layout
    plt.tight_layout()

    # Convert to base64 PNG
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{img_base64}"
