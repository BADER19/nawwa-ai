# Visualization Renderers

This directory contains modular, specialized rendering engines for different visualization types.

## Architecture Overview

```
User Input → LLM Classification → VisualizationRouter → Specific Renderer
```

Each renderer is **isolated** and handles only one visualization family.

---

## Current Renderers

### 1. **MathRenderer.tsx** - Mathematical Visualizations
**Engine:** Matplotlib (Python backend) + NumPy
**Status:** ✅ Implemented

**Handles:**
- Function plots (`sin(x)`, `x²`, polynomials)
- Critical points (minima, maxima)
- Axes and coordinate systems
- Mathematical annotations

**How it works:**
1. Receives elements with `type: 'function'`, `expression`, `domain`
2. Calls `/visualize/math` backend API
3. Backend evaluates expression with NumPy (500 points)
4. Backend renders plot with Matplotlib
5. Returns base64 PNG image
6. Displays the image

**Example Input:**
```json
{
  "visualType": "mathematical",
  "elements": [
    {
      "type": "axes",
      "xRange": [-10, 10],
      "yRange": [-10, 10]
    },
    {
      "type": "function",
      "expression": "x**2 - 4*x + 3",
      "domain": [-5, 5],
      "color": "#2563eb",
      "label": "y = x²"
    },
    {
      "type": "point",
      "x": 2,
      "y": -1,
      "label": "minimum"
    }
  ]
}
```

**Use Cases:**
- "Plot sin(x) and cos(x)"
- "Show local minima of y=x²-4x+3"
- "Graph a parabola"

---

### 2. **ConceptualRenderer.tsx** - Conceptual/Structural Visualizations
**Engine:** React Flow (formerly Canvas.tsx with Fabric.js)
**Status:** ✅ Implemented

**Handles:**
- Flowcharts
- Diagrams
- Mind maps
- Concept relationships
- Arrows and connectors
- Text labels

**How it works:**
1. Converts elements to React Flow nodes and edges
2. Applies smart layout via `applySmartLayout()`
3. Renders interactive diagram

**Example Input:**
```json
{
  "visualType": "conceptual",
  "elements": [
    {
      "type": "rect",
      "x": 100,
      "y": 100,
      "width": 120,
      "height": 60,
      "label": "Input",
      "color": "#dbeafe"
    },
    {
      "type": "connector",
      "from_point": {"x": 220, "y": 130},
      "to_point": {"x": 300, "y": 130},
      "label": "flows to"
    }
  ]
}
```

**Use Cases:**
- "Explain photosynthesis"
- "Compare democracy vs autocracy"
- "Show the water cycle"

---

## Planned Renderers (Not Yet Implemented)

### 3. **TimelineRenderer.tsx** - Timeline Visualizations
**Engine:** TBD (vis-timeline or custom SVG)
**Status:** ❌ Planned

**Will Handle:**
- Historical timelines
- Project roadmaps
- Life cycles
- Sequential events

**Proposed Input:**
```json
{
  "visualType": "timeline",
  "events": [
    {"date": "1939-09-01", "label": "WWII Starts"},
    {"date": "1945-05-08", "label": "VE Day"}
  ]
}
```

---

### 4. **ChartRenderer.tsx** - Statistical/Data Visualizations
**Engine:** TBD (Chart.js, Recharts, or D3.js)
**Status:** ❌ Planned

**Will Handle:**
- Bar charts
- Line charts
- Pie charts
- Scatter plots
- Data series

**Proposed Input:**
```json
{
  "visualType": "statistical",
  "chartType": "bar",
  "datasets": [
    {"label": "Q1", "data": [100, 200, 150]},
    {"label": "Q2", "data": [120, 190, 180]}
  ],
  "labels": ["Product A", "Product B", "Product C"]
}
```

---

### 5. **GraphRenderer.tsx** - Network/Graph Visualizations
**Engine:** TBD (React Flow or D3.js force-directed)
**Status:** ❌ Planned

**Will Handle:**
- Network graphs
- Dependency graphs
- Org charts
- Mind maps (advanced)

---

### 6. **SpatialRenderer.tsx** - 3D/Spatial Visualizations
**Engine:** TBD (Three.js)
**Status:** ❌ Planned

**Will Handle:**
- 3D models
- Spatial relationships
- Geometric visualizations

---

## Adding a New Renderer

### Step 1: Create the Renderer Component
```tsx
// renderers/TimelineRenderer.tsx
export default function TimelineRenderer({ events }: { events: any[] }) {
  // Your rendering logic here
  return <div>Timeline visualization</div>;
}
```

### Step 2: Register in VisualizationRouter
```tsx
// VisualizationRouter.tsx
import TimelineRenderer from './renderers/TimelineRenderer';

// In switch statement:
case 'timeline':
  return <TimelineRenderer events={spec.elements} />;
```

### Step 3: Update LLM Prompt
```python
# backend/services/llm_service.py
# Add timeline classification rules
```

### Step 4: Test in Isolation
```bash
# Test only TimelineRenderer without affecting other renderers
npm test TimelineRenderer
```

---

## Design Principles

1. **Isolation** - Each renderer is self-contained
2. **Single Responsibility** - One renderer = one visualization type
3. **Independent Development** - Build/test/ship separately
4. **Technology Flexibility** - Each renderer can use different libraries
5. **Progressive Enhancement** - Add features without breaking others

---

## Benefits of This Architecture

✅ **Parallel Development** - Different engineers work on different renderers
✅ **Easy Debugging** - Math broken? Only check MathRenderer
✅ **Gradual Rollout** - Ship Math today, Timeline next week
✅ **Technology Diversity** - Use best tool for each job
✅ **Testability** - Unit test each renderer independently
✅ **Scalability** - Add 10 more renderers without complexity explosion

---

## Current Directory Structure

```
frontend/components/
├── renderers/
│   ├── README.md               ← You are here
│   ├── MathRenderer.tsx        ← Math plots (Matplotlib)
│   ├── ConceptualRenderer.tsx  ← Diagrams (React Flow)
│   ├── TimelineRenderer.tsx    ← TODO
│   ├── ChartRenderer.tsx       ← TODO
│   ├── GraphRenderer.tsx       ← TODO
│   └── SpatialRenderer.tsx     ← TODO
│
├── VisualizationRouter.tsx     ← Central router
├── ChatInput.tsx
└── ...
```

---

## Next Steps

1. **Implement TimelineRenderer** - Most commonly requested
2. **Implement ChartRenderer** - Universal data visualization
3. **Implement GraphRenderer** - Complex relationships
4. **Add SymPy integration** - Symbolic math for MathRenderer
5. **Add animation support** - Per-renderer animations
