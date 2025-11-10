import MathRenderer from './renderers/MathRenderer';
import MathInteractiveRenderer from '../engines/math-interactive/MathInteractiveRenderer';
import ConceptualRenderer from './renderers/ConceptualRenderer';
import MermaidRenderer from './renderers/MermaidRenderer';
import ShapeRenderer from './renderers/ShapeRenderer';
import D3Renderer from './renderers/D3Renderer';
import PlotlyRenderer from './renderers/PlotlyRenderer';

/**
 * VisualizationRouter - Central orchestration layer for all visualization types
 *
 * This component routes to the appropriate renderer based on visualType:
 * - 'mathematical' → MathRenderer (Matplotlib backend)
 * - 'conceptual' → ConceptualRenderer (React Flow)
 * - 'timeline' → TimelineRenderer (TBD - future)
 * - 'statistical' → ChartRenderer (TBD - future)
 * - 'network' → GraphRenderer (TBD - future)
 * - 'spatial' → SpatialRenderer (TBD - future)
 */

type VisualSpec = {
  visualType?: 'conceptual' | 'mathematical' | 'mathematical_interactive' | 'timeline' | 'statistical' | 'network' | 'spatial' | 'mermaid' | 'plotly';
  elements?: Array<{
    type: string;
    [key: string]: any;
  }>;
  expression?: string; // For interactive math (single function)
  expressions?: string[]; // For interactive math (multiple functions)
  mermaidCode?: string; // For mermaid diagrams
  nodes?: Array<{id: string; label: string; [key: string]: any}>; // For D3 network graphs
  links?: Array<{source: string; target: string; [key: string]: any}>; // For D3 network graphs
  plotlySpec?: {
    data: any[];
    layout?: any;
    config?: any;
  }; // For Plotly universal charts
};

export default function VisualizationRouter({ spec }: { spec: VisualSpec }) {
  const { visualType, elements, expression, expressions, mermaidCode, nodes, links, plotlySpec } = spec;

  console.log('[VisualizationRouter] Routing visualType:', visualType, 'with', elements?.length || 0, 'elements');
  console.log('[VisualizationRouter] Full spec keys:', Object.keys(spec));
  console.log('[VisualizationRouter] nodes:', nodes);
  console.log('[VisualizationRouter] links:', links);
  console.log('[VisualizationRouter] Has nodes:', !!nodes, 'Has links:', !!links);
  console.log('[VisualizationRouter] plotlySpec:', plotlySpec);

  switch (visualType) {
    case 'plotly':
      if (plotlySpec) {
        return <PlotlyRenderer plotlySpec={plotlySpec} />;
      }
      return (
        <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
          <p style={{ fontSize: '16px', marginBottom: '8px' }}>Plotly Renderer Error</p>
          <p style={{ fontSize: '14px' }}>No plotlySpec provided.</p>
        </div>
      );

    case 'mermaid':
      return <MermaidRenderer mermaidCode={mermaidCode || ''} />;

    case 'mathematical_interactive':
      return <MathInteractiveRenderer initialExpression={expression} initialExpressions={expressions} />;

    case 'mathematical':
      // If expression provided, use interactive math renderer
      if (expression || expressions) {
        return <MathInteractiveRenderer initialExpression={expression} initialExpressions={expressions} />;
      }
      // Otherwise use traditional element-based math renderer
      return <MathRenderer elements={elements || []} />;

    case 'conceptual':
      // Smart routing based on data structure:
      // - D3: nodes/links at top level (smart auto-layout for networks)
      // - ShapeRenderer: basic shapes (SVG rendering)
      // - ConceptualRenderer: fallback (ReactFlow)

      // Check for nodes/links at TOP LEVEL of spec
      if (nodes && nodes.length > 0) {
        console.log('[VisualizationRouter] Using D3Renderer with', nodes.length, 'nodes');
        // Pass the spec as elements array with nodes/links embedded
        return <D3Renderer elements={[{ type: 'graph', nodes, links }]} layoutType="force" />;
      }

      const hasShapes = elements?.some(e => ['circle', 'triangle', 'ellipse', 'polygon', 'path'].includes(e.type));

      if (hasShapes) {
        // Ensure elements have required x,y coordinates with defaults
        const shapeElements = (elements || []).map(e => ({
          ...e,
          x: e.x ?? 100,
          y: e.y ?? 100
        }));
        return <ShapeRenderer elements={shapeElements as any} />;
      }
      // Ensure all elements have required x,y coordinates
      const conceptualElements = (elements || []).map(e => ({
        ...e,
        x: e.x ?? 100,
        y: e.y ?? 100
      }));
      return <ConceptualRenderer elements={conceptualElements as any} />;

    case 'timeline':
      // TODO: Implement TimelineRenderer
      return (
        <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
            Timeline Renderer Coming Soon
          </p>
          <p style={{ fontSize: '14px' }}>
            Timeline visualizations are not yet implemented.
          </p>
        </div>
      );

    case 'statistical':
      // TODO: Implement ChartRenderer
      return (
        <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
            Chart Renderer Coming Soon
          </p>
          <p style={{ fontSize: '14px' }}>
            Statistical visualizations are not yet implemented.
          </p>
        </div>
      );

    case 'network':
      // TODO: Implement GraphRenderer
      return (
        <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
            Graph Renderer Coming Soon
          </p>
          <p style={{ fontSize: '14px' }}>
            Network graph visualizations are not yet implemented.
          </p>
        </div>
      );

    case 'spatial':
      // TODO: Implement SpatialRenderer
      return (
        <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
            Spatial Renderer Coming Soon
          </p>
          <p style={{ fontSize: '14px' }}>
            3D and spatial visualizations are not yet implemented.
          </p>
        </div>
      );

    default:
      // Default to conceptual renderer for unknown types
      console.warn('[VisualizationRouter] Unknown visualType:', visualType, '- defaulting to ConceptualRenderer');
      // Ensure all elements have required x,y coordinates
      const defaultElements = (elements || []).map(e => ({
        ...e,
        x: e.x ?? 100,
        y: e.y ?? 100
      }));
      return <ConceptualRenderer elements={defaultElements as any} />;
  }
}
