import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface D3Node {
  id: string;
  label: string;
  color?: string;
  size?: number;
  shape?: 'circle' | 'rect' | 'diamond';
}

interface D3Link {
  source: string;
  target: string;
  label?: string;
}

interface D3Element {
  type: string;
  nodes?: D3Node[];
  links?: D3Link[];
  // For backward compatibility with element-based specs
  id?: string;
  label?: string;
  x?: number;
  y?: number;
  color?: string;
  [key: string]: any;
}

interface D3RendererProps {
  elements: D3Element[];
  layoutType?: 'force' | 'tree' | 'radial' | 'manual';
}

export default function D3Renderer({ elements, layoutType = 'force' }: D3RendererProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  console.log('[D3Renderer] Received elements:', elements);

  useEffect(() => {
    console.log('[D3Renderer useEffect] Starting render');
    if (!svgRef.current) {
      console.log('[D3Renderer] No svgRef!');
      return;
    }

    const width = 800;
    const height = 600;

    // Clear previous render
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height]);

    // Add background
    svg.append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('fill', '#ffffff');

    // Check if we have a graph structure (nodes/links) or individual elements
    const hasGraphStructure = elements.some(e => e.nodes || e.type === 'node');
    console.log('[D3Renderer] hasGraphStructure:', hasGraphStructure);

    if (hasGraphStructure) {
      console.log('[D3Renderer] Rendering graph');
      renderGraph(svg, elements, layoutType, width, height);
    } else {
      console.log('[D3Renderer] Rendering elements');
      renderElements(svg, elements, width, height);
    }

  }, [elements, layoutType]);

  return (
    <div
      style={{
        width: '100%',
        minHeight: '600px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#ffffff',
        padding: '40px',
      }}
    >
      <svg ref={svgRef} style={{ border: '1px solid #e5e7eb', borderRadius: '8px' }} />
    </div>
  );
}

// Render force-directed graph with smart layout
function renderGraph(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  elements: D3Element[],
  layoutType: string,
  width: number,
  height: number
) {
  // Extract nodes and links
  let nodes: D3Node[] = [];
  let links: D3Link[] = [];

  elements.forEach(el => {
    if (el.nodes) nodes = [...nodes, ...el.nodes];
    if (el.links) links = [...links, ...el.links];
  });

  // If no explicit nodes, create from individual elements
  if (nodes.length === 0) {
    nodes = elements
      .filter(e => e.type === 'node' || e.id)
      .map(e => ({
        id: e.id || `node_${Math.random()}`,
        label: e.label || e.text || 'Node',
        color: e.color || '#3b82f6',
        size: e.radius || e.size || 35,  // Increased default size for better text fit
        shape: e.shape || 'circle',
      }));
  }

  if (layoutType === 'force') {
    renderForceDirectedGraph(svg, nodes, links, width, height);
  } else {
    // Manual layout - render at specified positions
    renderManualLayout(svg, elements, width, height);
  }
}

// Force-directed layout with automatic positioning
function renderForceDirectedGraph(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  nodes: D3Node[],
  links: D3Link[],
  width: number,
  height: number
) {
  // Create simulation
  const simulation = d3.forceSimulation(nodes as any)
    .force('link', d3.forceLink(links).id((d: any) => d.id).distance(180))
    .force('charge', d3.forceManyBody().strength(-500))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius((d: any) => (d.size || 35) + 15));  // Dynamic collision based on node size

  // Create container groups
  const g = svg.append('g');

  // Render links
  const link = g.append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('stroke', '#94a3b8')
    .attr('stroke-width', 2)
    .attr('stroke-opacity', 0.6);

  // Render link labels
  const linkLabel = g.append('g')
    .selectAll('text')
    .data(links.filter(l => l.label))
    .join('text')
    .text(d => d.label || '')
    .attr('font-size', 12)
    .attr('fill', '#64748b')
    .attr('text-anchor', 'middle')
    .attr('dy', -5);

  // Render nodes
  const node = g.append('g')
    .selectAll('g')
    .data(nodes)
    .join('g')
    .call(d3.drag<any, any>()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended));

  // Add shapes based on node shape type
  node.each(function(d: any) {
    const nodeGroup = d3.select(this);
    const nodeSize = d.size || 35;  // Use consistent default size

    if (d.shape === 'rect') {
      nodeGroup.append('rect')
        .attr('width', nodeSize * 2)
        .attr('height', nodeSize * 1.5)
        .attr('x', -nodeSize)
        .attr('y', -(nodeSize * 0.75))
        .attr('fill', d.color || '#3b82f6')
        .attr('stroke', '#1e40af')
        .attr('stroke-width', 2)
        .attr('rx', 8);
    } else if (d.shape === 'diamond') {
      nodeGroup.append('polygon')
        .attr('points', `0,-${nodeSize} ${nodeSize},0 0,${nodeSize} -${nodeSize},0`)
        .attr('fill', d.color || '#3b82f6')
        .attr('stroke', '#1e40af')
        .attr('stroke-width', 2);
    } else {
      // Default: circle
      nodeGroup.append('circle')
        .attr('r', nodeSize)
        .attr('fill', d.color || '#3b82f6')
        .attr('stroke', '#1e40af')
        .attr('stroke-width', 2);
    }
  });

  // Add labels with dynamic sizing
  node.each(function(d: any) {
    const nodeGroup = d3.select(this);
    const nodeSize = d.size || 20;
    const label = d.label || '';

    // Calculate appropriate font size based on node size
    // Font should be roughly 50-60% of node diameter
    const baseFontSize = Math.max(10, Math.min(16, nodeSize * 0.6));

    // For long labels, wrap or truncate
    if (label.length > 12) {
      // Truncate with ellipsis
      const truncated = label.substring(0, 10) + '...';
      nodeGroup.append('text')
        .text(truncated)
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .attr('font-size', baseFontSize)
        .attr('font-weight', '600')
        .attr('fill', '#ffffff')
        .attr('font-family', 'Inter, Helvetica, Arial, sans-serif')
        .style('pointer-events', 'none');
    } else {
      nodeGroup.append('text')
        .text(label)
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .attr('font-size', baseFontSize)
        .attr('font-weight', '600')
        .attr('fill', '#ffffff')
        .attr('font-family', 'Inter, Helvetica, Arial, sans-serif')
        .style('pointer-events', 'none');
    }
  });

  // Update positions on each tick
  simulation.on('tick', () => {
    link
      .attr('x1', (d: any) => d.source.x)
      .attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x)
      .attr('y2', (d: any) => d.target.y);

    linkLabel
      .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
      .attr('y', (d: any) => (d.source.y + d.target.y) / 2);

    node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
  });

  // Drag functions
  function dragstarted(event: any, d: any) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event: any, d: any) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragended(event: any, d: any) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
}

// Render individual elements at specified positions
function renderElements(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  elements: D3Element[],
  width: number,
  height: number
) {
  const g = svg.append('g');

  elements.forEach(element => {
    const x = element.x || width / 2;
    const y = element.y || height / 2;

    switch (element.type) {
      case 'circle':
        g.append('circle')
          .attr('cx', x)
          .attr('cy', y)
          .attr('r', element.radius || 50)
          .attr('fill', element.color || element.fill || '#3b82f6')
          .attr('stroke', element.stroke || '#1e40af')
          .attr('stroke-width', element.strokeWidth || 2);
        break;

      case 'rect':
        g.append('rect')
          .attr('x', x)
          .attr('y', y)
          .attr('width', element.width || 100)
          .attr('height', element.height || 60)
          .attr('fill', element.color || element.fill || '#3b82f6')
          .attr('stroke', element.stroke || '#1e40af')
          .attr('stroke-width', element.strokeWidth || 2)
          .attr('rx', 8);
        break;

      case 'text':
        g.append('text')
          .attr('x', x)
          .attr('y', y)
          .text(element.text || element.label || '')
          .attr('font-size', element.fontSize || 16)
          .attr('fill', element.color || '#000000')
          .attr('font-family', 'Inter, Helvetica, Arial, sans-serif')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle');
        break;

      case 'line':
        g.append('line')
          .attr('x1', x)
          .attr('y1', y)
          .attr('x2', x + (element.width || 100))
          .attr('y2', y + (element.height || 0))
          .attr('stroke', element.color || '#1e40af')
          .attr('stroke-width', element.strokeWidth || 2);
        break;
    }

    // Add label if present
    if (element.label && element.type !== 'text') {
      g.append('text')
        .attr('x', x)
        .attr('y', y - (element.radius || element.height || 30) - 10)
        .text(element.label)
        .attr('font-size', 14)
        .attr('font-weight', '600')
        .attr('fill', '#1e293b')
        .attr('font-family', 'Inter, Helvetica, Arial, sans-serif')
        .attr('text-anchor', 'middle');
    }
  });
}

// Manual layout rendering
function renderManualLayout(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  elements: D3Element[],
  width: number,
  height: number
) {
  renderElements(svg, elements, width, height);
}
