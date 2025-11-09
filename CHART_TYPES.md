# InstantViz - Comprehensive Visualization Reference

This document lists **ALL 40+ supported visualization types** in InstantViz, organized by category.

**Renderers**: Plotly.js (charts), Mermaid (diagrams), SVG (conceptual), D3, Math

---

## 1. BASIC STATISTICAL CHARTS (Plotly)

### Histogram (type: 'histogram')
**Purpose**: Show distribution of continuous data, frequency of values in bins
**Keywords**: distribution, frequency, bins, histogram, bell curve
**Example Commands**:
- "histogram of exam scores"
- "show distribution of ages"
- "frequency distribution of response times"

**Plotly Spec**:
```json
{
  "data": [{
    "type": "histogram",
    "x": [65, 72, 78, 82, 85, 88, 90, 92, 95, 98],
    "nbinsx": 5,
    "marker": {"color": "#3b82f6"}
  }],
  "layout": {"title": "Score Distribution"}
}
```

### Box Plot (type: 'box')
**Purpose**: Show distribution summary with quartiles, median, outliers
**Keywords**: box plot, quartile, median, outliers, distribution summary
**Example Commands**:
- "box plot of salaries by department"
- "show quarterly sales distribution"

**Plotly Spec**:
```json
{
  "data": [{
    "type": "box",
    "y": [20, 25, 30, 35, 40, 45, 50, 100],
    "name": "Sales",
    "marker": {"color": "#10b981"}
  }],
  "layout": {"title": "Sales Distribution"}
}
```

### Violin Plot (type: 'violin')
**Purpose**: Show distribution shape + summary statistics
**Keywords**: violin plot, distribution shape, density
**Example Commands**:
- "violin plot of response times"
- "show distribution shape of prices"

**Plotly Spec**:
```json
{
  "data": [{
    "type": "violin",
    "y": [20, 22, 25, 28, 30, 32, 35, 38, 40],
    "box": {"visible": true},
    "meanline": {"visible": true}
  }]
}
```

## 2. COMPARISON CHARTS

### Bar Chart - Vertical (type: 'bar')
**Purpose**: Compare values across categories
**Keywords**: compare, vs, versus, bar chart, ranking
**Example Commands**:
- "compare revenue by quarter"
- "top 10 products by sales"

### Bar Chart - Horizontal (type: 'bar' with orientation: 'h')
**Purpose**: Compare categories with long names
**Keywords**: horizontal bar, compare
**Plotly Spec**:
```json
{
  "data": [{
    "type": "bar",
    "y": ["Product A", "Product B", "Product C"],
    "x": [100, 150, 200],
    "orientation": "h"
  }]
}
```

### Stacked Bar Chart (type: 'bar' with barmode: 'stack')
**Purpose**: Show composition and total
**Keywords**: stacked bar, breakdown, composition over time
**Plotly Spec**:
```json
{
  "data": [
    {"type": "bar", "name": "Desktop", "x": ["Q1","Q2"], "y": [50, 60]},
    {"type": "bar", "name": "Mobile", "x": ["Q1","Q2"], "y": [30, 40]}
  ],
  "layout": {"barmode": "stack"}
}
```

### Grouped Bar Chart (type: 'bar' with barmode: 'group')
**Purpose**: Side-by-side comparison
**Keywords**: grouped bar, compare, side by side
**Plotly Spec**:
```json
{
  "data": [
    {"type": "bar", "name": "2023", "x": ["Q1","Q2"], "y": [50, 60]},
    {"type": "bar", "name": "2024", "x": ["Q1","Q2"], "y": [55, 65]}
  ],
  "layout": {"barmode": "group"}
}
```

### Waterfall Chart (type: 'waterfall')
**Purpose**: Show cumulative effect of sequential values
**Keywords**: waterfall, cumulative, sequential changes
**Example Commands**:
- "waterfall chart of profit breakdown"
- "show cumulative cash flow"

**Plotly Spec**:
```json
{
  "data": [{
    "type": "waterfall",
    "x": ["Revenue", "Costs", "Taxes", "Net"],
    "y": [100, -30, -20, 50],
    "measure": ["relative", "relative", "relative", "total"]
  }]
}
```

## 3. COMPOSITION CHARTS

### Pie Chart (type: 'pie')
**Purpose**: Show parts of a whole
**Keywords**: pie chart, market share, percentage, proportion

### Donut Chart (type: 'pie' with hole)
**Purpose**: Pie chart with center hole, better for multiple series
**Keywords**: donut chart, donut, ring chart
**Plotly Spec**:
```json
{
  "data": [{
    "type": "pie",
    "labels": ["A", "B", "C"],
    "values": [40, 35, 25],
    "hole": 0.4
  }]
}
```

### Treemap (type: 'treemap')
**Purpose**: Show hierarchical data with nested rectangles
**Keywords**: treemap, hierarchy, nested, hierarchical breakdown
**Example Commands**:
- "treemap of sales by region and product"
- "show hierarchical budget breakdown"

**Plotly Spec**:
```json
{
  "data": [{
    "type": "treemap",
    "labels": ["Total", "North", "South", "N-Product A", "N-Product B"],
    "parents": ["", "Total", "Total", "North", "North"],
    "values": [100, 60, 40, 35, 25]
  }]
}
```

### Sunburst Chart (type: 'sunburst')
**Purpose**: Show hierarchy in concentric rings
**Keywords**: sunburst, circular hierarchy, radial tree
**Plotly Spec**:
```json
{
  "data": [{
    "type": "sunburst",
    "labels": ["Total", "Sales", "Marketing", "Product A", "Product B"],
    "parents": ["", "Total", "Total", "Sales", "Sales"],
    "values": [100, 60, 40, 35, 25]
  }]
}
```

### Funnel Chart (type: 'funnel')
**Purpose**: Show progressive reduction through stages
**Keywords**: funnel, conversion, stages, pipeline
**Example Commands**:
- "sales funnel conversion rates"
- "user journey funnel"

**Plotly Spec**:
```json
{
  "data": [{
    "type": "funnel",
    "y": ["Visitors", "Sign up", "Trial", "Purchase"],
    "x": [1000, 500, 200, 100]
  }]
}
```

## 4. DISTRIBUTION & RELATIONSHIP CHARTS

### Scatter Plot (type: 'scatter' with mode: 'markers')
**Purpose**: Show relationship between two variables
**Keywords**: scatter, correlation, relationship

### Bubble Chart (type: 'scatter' with marker.size)
**Purpose**: Scatter plot with third dimension (size)
**Keywords**: bubble chart, three variables
**Plotly Spec**:
```json
{
  "data": [{
    "type": "scatter",
    "mode": "markers",
    "x": [1, 2, 3, 4],
    "y": [10, 20, 30, 40],
    "marker": {
      "size": [20, 30, 40, 50],
      "color": [10, 20, 30, 40],
      "colorscale": "Viridis",
      "showscale": true
    }
  }]
}
```

### Heat Map (type: 'heatmap')
**Purpose**: Show magnitude in 2D matrix using color
**Keywords**: heatmap, correlation matrix, intensity
**Example Commands**:
- "heatmap of correlation matrix"
- "show activity by hour and day"

**Plotly Spec**:
```json
{
  "data": [{
    "type": "heatmap",
    "z": [[1, 20, 30], [20, 1, 60], [30, 60, 1]],
    "x": ["A", "B", "C"],
    "y": ["A", "B", "C"],
    "colorscale": "Viridis"
  }]
}
```

### Hexbin Plot (type: 'histogram2d' or 'density_heatmap')
**Purpose**: 2D histogram for large datasets
**Keywords**: hexbin, density, 2d histogram
**Plotly Spec**:
```json
{
  "data": [{
    "type": "histogram2d",
    "x": [1, 2, 3, 4, 5],
    "y": [1, 2, 3, 4, 5]
  }]
}
```

## 5. TREND & TIME SERIES CHARTS

### Line Chart (type: 'scatter' with mode: 'lines')
**Purpose**: Show trends over time
**Keywords**: trend, over time, timeline, time series

### Area Chart (type: 'scatter' with fill)
**Purpose**: Line chart with filled area
**Keywords**: area chart, filled, cumulative
**Plotly Spec**:
```json
{
  "data": [{
    "type": "scatter",
    "x": [1, 2, 3, 4],
    "y": [10, 20, 15, 25],
    "fill": "tozeroy",
    "mode": "lines"
  }]
}
```

### Stacked Area Chart (multiple traces with fill)
**Purpose**: Show composition over time
**Keywords**: stacked area, composition over time
**Plotly Spec**:
```json
{
  "data": [
    {"type": "scatter", "x": [1,2,3], "y": [3,2,4], "fill": "tozeroy", "name": "A"},
    {"type": "scatter", "x": [1,2,3], "y": [5,4,6], "fill": "tonexty", "name": "B"}
  ]
}
```

## 6. SPECIALIZED CHARTS

### Radar/Spider Chart (type: 'scatterpolar')
**Purpose**: Show multivariate data on radial axes
**Keywords**: radar chart, spider chart, star plot, multivariate
**Example Commands**:
- "radar chart of player stats"
- "spider chart of product features"

**Plotly Spec**:
```json
{
  "data": [{
    "type": "scatterpolar",
    "r": [80, 70, 90, 85, 75],
    "theta": ["Speed", "Power", "Accuracy", "Defense", "Stamina"],
    "fill": "toself"
  }]
}
```

### Sankey Diagram (type: 'sankey')
**Purpose**: Show flows between nodes
**Keywords**: sankey, flow, relationship, connections

### Network Graph (type: 'scatter' with annotations for edges)
**Purpose**: Show nodes and connections
**Keywords**: network, graph, nodes, connections, relationships

### Parallel Coordinates (type: 'parcoords')
**Purpose**: Show many variables across items
**Keywords**: parallel coordinates, multivariate, many dimensions
**Plotly Spec**:
```json
{
  "data": [{
    "type": "parcoords",
    "dimensions": [
      {"label": "Age", "values": [25, 30, 35]},
      {"label": "Income", "values": [50, 60, 70]},
      {"label": "Score", "values": [80, 85, 90]}
    ]
  }]
}
```

### Bullet Graph (combination of bar + markers)
**Purpose**: Show progress toward goal with thresholds
**Keywords**: bullet graph, KPI, target, threshold
**Example**: Use bar chart with shapes overlay for target line

### Dot Plot (type: 'scatter' with mode: 'markers')
**Purpose**: Similar to bar but using dots
**Keywords**: dot plot, Cleveland dot plot

### Choropleth Map (type: 'choropleth')
**Purpose**: Geographic map with color-coded regions
**Keywords**: choropleth, map, geographic, by country/region
**Plotly Spec**:
```json
{
  "data": [{
    "type": "choropleth",
    "locations": ["USA", "CAN", "MEX"],
    "z": [100, 80, 60],
    "locationmode": "ISO-3",
    "colorscale": "Viridis"
  }]
}
```

## CHART SELECTION GUIDE

**For Distributions**: histogram, box, violin
**For Comparisons**: bar (vertical/horizontal/stacked/grouped)
**For Compositions**: pie, donut, treemap, sunburst, funnel
**For Trends**: line, area, stacked area
**For Relationships**: scatter, bubble, heatmap, network
**For Flows**: sankey, waterfall
**For Multivariate**: radar, parallel coordinates, bubble
**For Geography**: choropleth, scatter geo
**For Hierarchies**: treemap, sunburst, sankey

---

## 6. MERMAID DIAGRAMS - Process Flows, Hierarchies, Journeys

### Flowchart (type: flowchart TD/LR)
**Purpose**: Show process flows, decision trees, workflows
**Keywords**: flowchart, process, workflow, decision, steps
**Example Commands**:
- "create a flowchart for user authentication"
- "show workflow for order processing"
- "decision tree for loan approval"

**Mermaid Code**:
```
flowchart TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Process]
    B -->|No| D[End]
    C --> D
```

### Org Chart / Hierarchy (type: graph TD)
**Purpose**: Show organizational structure, reporting lines
**Keywords**: org chart, organization, hierarchy, reporting structure
**Example Commands**:
- "company org chart"
- "team hierarchy"
- "department structure"

**Mermaid Code**:
```
graph TD
    CEO[CEO] --> CTO[CTO]
    CEO --> CFO[CFO]
    CTO --> Dev[Dev Team]
    CTO --> QA[QA Team]
```

### Mind Map (type: mindmap)
**Purpose**: Brainstorming, idea organization, concept mapping
**Keywords**: mind map, mindmap, brainstorm, ideas, concept map
**Example Commands**:
- "mind map of AI concepts"
- "brainstorm features for app"
- "concept map of marketing strategy"

**Mermaid Code**:
```
mindmap
  root((AI))
    Machine Learning
      Supervised
      Unsupervised
    Deep Learning
      CNN
      RNN
```

### Sequence Diagram (type: sequenceDiagram)
**Purpose**: Show interactions between entities over time
**Keywords**: sequence, interaction, API flow, message flow
**Example Commands**:
- "sequence diagram for login"
- "API interaction flow"
- "message sequence for chat"

**Mermaid Code**:
```
sequenceDiagram
    Client->>Server: Request
    Server->>DB: Query
    DB-->>Server: Data
    Server-->>Client: Response
```

### Journey Map (type: journey)
**Purpose**: Customer experience, user journey mapping
**Keywords**: journey map, customer journey, user experience, touchpoints
**Example Commands**:
- "customer journey for e-commerce"
- "user experience map for signup"
- "journey map for onboarding"

**Mermaid Code**:
```
journey
    title Customer Shopping Journey
    section Discovery
      Browse: 5: Customer
      Search: 4: Customer
    section Purchase
      Add to cart: 5: Customer
      Checkout: 3: Customer
```

### Entity Relationship Diagram (type: erDiagram)
**Purpose**: Database schema, data models
**Keywords**: ER diagram, database schema, data model, entity relationship
**Example Commands**:
- "ER diagram for user database"
- "database schema for e-commerce"
- "data model for CRM"

**Mermaid Code**:
```
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ ITEM : contains
```

### Gantt Chart (type: gantt)
**Purpose**: Project timelines, task scheduling
**Keywords**: gantt, timeline, project schedule, task timeline
**Example Commands**:
- "gantt chart for project"
- "project timeline"
- "development schedule"

**Mermaid Code**:
```
gantt
    title Project Schedule
    section Phase 1
    Task 1: 2024-01-01, 10d
    Task 2: 2024-01-11, 15d
```

---

## 7. ADVANCED PLOTLY VISUALIZATIONS

### Gauge Chart / KPI (type: 'indicator')
**Purpose**: KPI dashboards, performance metrics, progress
**Keywords**: gauge, KPI, speedometer, progress indicator
**Example**: Dashboard showing completion percentage, sales target

### Correlogram (type: 'heatmap' variant)
**Purpose**: Correlation matrix visualization
**Keywords**: correlogram, correlation matrix
**Example**: Show correlations between multiple variables (-1 to +1)

### Ridgeline Plot (type: 'violin' stacked)
**Purpose**: Comparing distributions across many categories
**Keywords**: ridgeline, joy plot, overlapping distributions
**Example**: Temperature distributions by month

### Density Curve / KDE (type: 'histogram' with density)
**Purpose**: Smooth probability distribution
**Keywords**: density curve, kernel density, KDE
**Example**: Distribution of test scores with smooth curve

### QQ Plot (type: 'scatter' with reference line)
**Purpose**: Test if data follows theoretical distribution
**Keywords**: QQ plot, quantile plot, normality test
**Example**: Check if data is normally distributed

---

## 8. CONCEPTUAL DIAGRAMS (SVG/Basic Shapes)

### Venn Diagram
**Purpose**: Show overlapping sets, intersections
**Keywords**: venn diagram, overlap, intersection, sets
**Implementation**: Use overlapping circles with labels

### System Architecture
**Purpose**: Software/hardware architecture diagrams
**Keywords**: architecture, system design, components, infrastructure
**Implementation**: Rectangles for components, arrows for connections

### Infographics
**Purpose**: Combine charts, text, icons for storytelling
**Keywords**: infographic, visual story, data story
**Implementation**: Mix of charts + text + icons

---

## DIAGRAM SELECTION GUIDE

**For Data Analysis**: Use Plotly charts (bar, line, scatter, heatmap, box, etc.)
**For Processes**: Use Mermaid flowcharts, sequence diagrams
**For Hierarchies**: Use Mermaid org charts, tree diagrams, mind maps
**For Timelines**: Use Gantt charts, journey maps
**For Relationships**: Use Sankey, network graphs, ER diagrams
**For Conceptual Ideas**: Use Venn diagrams, architecture diagrams, mind maps

---

## DOCUMENTATION REFERENCES
- **Plotly.js**: https://plotly.com/javascript/
- **Mermaid**: https://mermaid.js.org/
- **Chart Selection Guide**: https://www.data-to-viz.com/
