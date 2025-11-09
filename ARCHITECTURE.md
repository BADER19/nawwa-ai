# Nawwa Architecture - Modular Visualization System

## Overview

Nawwa uses a **modular, multi-renderer architecture** where different visualization types are handled by specialized, isolated rendering engines.

## Core Principle

> **"There's no 'one renderer to rule them all'"**
> Each visualization family requires fundamentally different technology and rendering approaches.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│           USER INPUT                        │
│   "Plot sin(x)" or "Explain photosynthesis" │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│         LLM (GPT-5)                         │
│    Intent Classification                    │
│                                             │
│  Detects: visualType =                      │
│  'mathematical' | 'conceptual' |            │
│  'timeline' | 'statistical' | ...           │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│    LLM Generates Visual Spec (JSON)         │
│                                             │
│    {                                        │
│      visualType: "mathematical",            │
│      elements: [                            │
│        {type: "axes", xRange, yRange},      │
│        {type: "function",                   │
│         expression: "sin(x)"}               │
│      ]                                      │
│    }                                        │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│      VisualizationRouter.tsx                │
│   (Central Orchestration Layer)             │
│                                             │
│   Routes based on visualType:               │
│   - mathematical → MathRenderer             │
│   - conceptual   → ConceptualRenderer       │
│   - timeline     → TimelineRenderer (TODO)  │
│   - statistical  → ChartRenderer (TODO)     │
│   - network      → GraphRenderer (TODO)     │
│   - spatial      → SpatialRenderer (TODO)   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌─────────────────┐  ┌─────────────────┐
│  MathRenderer   │  │ Conceptual      │
│                 │  │ Renderer        │
│ • Matplotlib    │  │                 │
│ • NumPy         │  │ • React Flow    │
│ • Server-side   │  │ • Client-side   │
│                 │  │ • Interactive   │
│ Renders:        │  │                 │
│ - Function      │  │ Renders:        │
│   curves        │  │ - Flowcharts    │
│ - Critical      │  │ - Diagrams      │
│   points        │  │ - Mind maps     │
│ - Axes          │  │ - Connectors    │
└─────────────────┘  └─────────────────┘
```

---

## Current Implementation Status

### ✅ Implemented Renderers

#### 1. MathRenderer (Mathematical Visualizations)
- **Location:** `frontend/components/renderers/MathRenderer.tsx`
- **Backend:** `backend/services/math_plot_service.py`
- **Engine:** Matplotlib + NumPy (Python server-side)
- **Output:** Base64 PNG image
- **Handles:**
  - Function plots (`sin(x)`, `x²`, polynomials)
  - Critical points (minima, maxima)
  - Axes, gridlines, coordinate systems
  - Mathematical annotations

**Technical Flow:**
```
Frontend → POST /visualize/math → Backend NumPy evaluates expression
→ Matplotlib renders plot → Base64 PNG → Frontend displays image
```

#### 2. ConceptualRenderer (Conceptual/Structural Visualizations)
- **Location:** `frontend/components/renderers/ConceptualRenderer.tsx`
- **Engine:** React Flow (client-side)
- **Output:** Interactive SVG diagram
- **Handles:**
  - Flowcharts
  - Diagrams
  - Concept maps
  - Arrows and connectors
  - Text labels

**Technical Flow:**
```
Frontend → Converts elements to React Flow nodes/edges
→ Applies smart layout → Renders interactive diagram
```

---

### ❌ Planned Renderers (Not Yet Implemented)

#### 3. TimelineRenderer (Next Priority)
- **Proposed Engine:** vis-timeline or custom SVG
- **Use Cases:** Historical timelines, project roadmaps, life cycles
- **Why Next:** Common use case, relatively simple, good test of modularity

#### 4. ChartRenderer (Statistical Data)
- **Proposed Engine:** Chart.js, Recharts, or D3.js
- **Use Cases:** Bar charts, line charts, pie charts, scatter plots
- **Why Important:** Universal need for data visualization

#### 5. GraphRenderer (Network Graphs)
- **Proposed Engine:** React Flow or D3.js force-directed
- **Use Cases:** Network graphs, dependency trees, org charts
- **Why Last:** Most complex layout algorithms

#### 6. SpatialRenderer (3D Visualizations)
- **Proposed Engine:** Three.js
- **Use Cases:** 3D models, spatial relationships
- **Why Future:** Less common, requires WebGL expertise

---

## Directory Structure

```
frontend/
├── components/
│   ├── renderers/
│   │   ├── README.md                  ← Renderer documentation
│   │   ├── MathRenderer.tsx          ← ✅ Math plots
│   │   ├── ConceptualRenderer.tsx    ← ✅ Diagrams
│   │   ├── TimelineRenderer.tsx      ← ❌ TODO
│   │   ├── ChartRenderer.tsx         ← ❌ TODO
│   │   ├── GraphRenderer.tsx         ← ❌ TODO
│   │   └── SpatialRenderer.tsx       ← ❌ TODO
│   │
│   ├── VisualizationRouter.tsx       ← Central router
│   └── ChatInput.tsx
│
├── pages/
│   └── app.tsx                        ← Main app (uses VisualizationRouter)
│
└── lib/
    ├── api.ts
    └── layoutEngine.ts

backend/
├── services/
│   ├── llm_service.py                 ← Intent classification
│   ├── math_plot_service.py           ← Math rendering (Matplotlib)
│   ├── visualize.py                   ← Main orchestrator
│   └── ...
│
└── ...
```

---

## Key Design Principles

### 1. **Modularity**
Each renderer is a self-contained module:
- Independent development
- Separate testing
- Isolated failures
- Technology flexibility

### 2. **Separation of Concerns**
```
VisualizationRouter     → Orchestration (routing only)
MathRenderer           → Math visualization (only)
ConceptualRenderer     → Diagrams (only)
```

No renderer knows about other renderers.

### 3. **Progressive Enhancement**
Ship renderers incrementally:
```
v1.0: Math + Conceptual ✅
v1.1: + Timeline
v1.2: + Charts
v1.3: + Networks
```

Each version is independently shippable.

### 4. **Technology Diversity**
Different renderers use different tech stacks:

| Renderer | Technology | Reason |
|----------|-----------|---------|
| Math | Matplotlib (Python) | Accurate numerical computation |
| Conceptual | React Flow | Interactive diagrams |
| Timeline | vis-timeline | Temporal layout |
| Charts | Chart.js | Data binding |
| Network | D3.js | Force-directed graphs |
| Spatial | Three.js | 3D rendering |

---

## Benefits of This Architecture

### Development Benefits
✅ **Parallel Development** - Different engineers work on different renderers simultaneously
✅ **Easy Debugging** - Math broken? Only check MathRenderer
✅ **Gradual Rollout** - Ship Math today, Timeline next week
✅ **Technology Flexibility** - Swap Matplotlib for Plotly without touching Timeline
✅ **Team Scaling** - Assign different engineers to different renderers

### Maintenance Benefits
✅ **Isolated Changes** - Update Math without risking Conceptual
✅ **Clear Ownership** - Each renderer has a clear maintainer
✅ **Easier Testing** - Unit test each renderer independently
✅ **Simpler Code** - Each renderer is smaller and simpler

### User Benefits
✅ **Better Quality** - Each renderer optimized for its visualization type
✅ **Faster Iteration** - New features ship faster
✅ **Reliability** - One renderer's bug doesn't break others

---

## Adding a New Renderer

### Step 1: Create the Renderer Component
```tsx
// frontend/components/renderers/TimelineRenderer.tsx
export default function TimelineRenderer({ events }: { events: any[] }) {
  // Rendering logic
  return <div>Timeline visualization</div>;
}
```

### Step 2: Register in VisualizationRouter
```tsx
// frontend/components/VisualizationRouter.tsx
import TimelineRenderer from './renderers/TimelineRenderer';

// Add case to switch statement:
case 'timeline':
  return <TimelineRenderer events={spec.elements} />;
```

### Step 3: Update LLM Classification
```python
# backend/services/llm_service.py
# Add timeline classification rules to PROMPT_TEMPLATE
```

### Step 4: Test Independently
```bash
npm test TimelineRenderer
```

### Step 5: Ship to Production
Deploy without touching existing renderers.

---

## Example: How Mathematical Visualization Works

### 1. User Input
```
"Plot sin(x) and cos(x)"
```

### 2. LLM Classification
```json
{
  "visualType": "mathematical",
  "elements": [
    {
      "type": "axes",
      "xRange": [-6.28, 6.28],
      "yRange": [-1.5, 1.5]
    },
    {
      "type": "function",
      "expression": "sin(x)",
      "color": "#2563eb",
      "label": "sin(x)"
    },
    {
      "type": "function",
      "expression": "cos(x)",
      "color": "#ef4444",
      "label": "cos(x)"
    }
  ]
}
```

### 3. Router Decision
```tsx
// VisualizationRouter sees visualType === 'mathematical'
switch (visualType) {
  case 'mathematical':
    return <MathRenderer elements={elements} />;
}
```

### 4. MathRenderer Calls Backend
```tsx
const response = await apiPost('/visualize/math', { elements });
// Response: { imageUrl: "data:image/png;base64,iVBORw0KG..." }
```

### 5. Backend Processing
```python
# math_plot_service.py
x_vals = np.linspace(-6.28, 6.28, 500)
y_sin = np.sin(x_vals)
y_cos = np.cos(x_vals)

ax.plot(x_vals, y_sin, color='#2563eb', label='sin(x)')
ax.plot(x_vals, y_cos, color='#ef4444', label='cos(x)')

# Convert to base64 PNG
return base64_image
```

### 6. Display Result
Frontend displays the PNG image with both curves plotted.

---

## Performance Considerations

### MathRenderer (Server-Side)
- **Pro:** Accurate math computation, consistent rendering
- **Con:** Network latency for plot generation
- **Optimization:** Cache generated plots, use Redis

### ConceptualRenderer (Client-Side)
- **Pro:** Instant interactivity, no network calls
- **Con:** Browser performance limits
- **Optimization:** Virtualization for large diagrams

---

## Future Enhancements

1. **Animation Support** - Per-renderer animations
2. **Export Options** - SVG, PNG, PDF per renderer
3. **Collaboration** - Real-time editing per renderer type
4. **Templates** - Pre-built templates per visualization type
5. **SymPy Integration** - Symbolic math for MathRenderer
6. **Voice Input** - Natural language to visualization

---

## Summary

The modular architecture allows Nawwa to scale to support 6+ visualization types while maintaining:
- Clean code separation
- Independent development cycles
- Technology flexibility
- High reliability
- Easy maintenance

Each renderer is an expert at one thing, making the entire system more robust and maintainable than a monolithic approach.
