import { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  NodeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { applySmartLayout } from '../lib/layoutEngine';

type Element = {
  type: string;
  x: number;
  y: number;
  radius?: number;
  width?: number;
  height?: number;
  color?: string;
  label?: string;
  text?: string;
  fontSize?: number;
  fontWeight?: string;
  textAlign?: string;
  points?: Array<{ x: number; y: number }>;
  src?: string;
  from_point?: { x: number; y: number };
  to_point?: { x: number; y: number };
  backgroundColor?: string;
  borderColor?: string;
  borderWidth?: number;
  opacity?: number;
  id?: string;
  [key: string]: any;
};

// Custom node component for shapes
function ShapeNode({ data }: { data: any }) {
  const {
    shapeType,
    label,
    color,
    backgroundColor,
    borderColor,
    borderWidth,
    width,
    height,
    radius,
    fontSize,
    fontWeight,
    opacity,
    src,
  } = data;

  const commonStyle = {
    padding: '12px 20px',
    borderRadius: shapeType === 'circle' ? '50%' : '8px',
    border: `${borderWidth || 2}px solid ${borderColor || '#2563eb'}`,
    backgroundColor: backgroundColor || color || '#ffffff',
    color: data.labelColor || '#1e293b',
    fontSize: `${fontSize || 14}px`,
    fontWeight: fontWeight || '600',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
    opacity: opacity || 1,
    minWidth: width || (shapeType === 'circle' ? radius * 2 : 120),
    minHeight: height || (shapeType === 'circle' ? radius * 2 : 60),
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center' as const,
    whiteSpace: 'pre-wrap' as const,
    wordBreak: 'break-word' as const,
  };

  if (shapeType === 'circle') {
    const size = (radius || 50) * 2;
    return (
      <div style={{ ...commonStyle, width: size, height: size, borderRadius: '50%' }}>
        {label || ''}
      </div>
    );
  }

  if (shapeType === 'text' || shapeType === 'textbox') {
    return (
      <div
        style={{
          padding: '8px',
          fontSize: `${fontSize || 14}px`,
          fontWeight: fontWeight || 'normal',
          color: color || '#000',
          backgroundColor: 'transparent',
          border: 'none',
          boxShadow: 'none',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          textAlign: (data.textAlign || 'left') as any,
          maxWidth: width || 200,
        }}
      >
        {label || data.text || 'Text'}
      </div>
    );
  }

  if (shapeType === 'image' && src) {
    // Proxy external images through backend to avoid CORS
    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:18001';
    const proxiedSrc = `${API_BASE}/image/proxy?url=${encodeURIComponent(src)}`;

    return (
      <div
        style={{
          padding: 0,
          backgroundColor: 'transparent',
          border: 'none',
          boxShadow: 'none',
        }}
      >
        <img
          src={proxiedSrc}
          alt={label || 'Image'}
          style={{
            width: width || 300,
            height: height || 400,
            objectFit: 'cover',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          }}
          onError={(e) => {
            console.error('Failed to load image:', src);
            e.currentTarget.style.display = 'none';
          }}
        />
      </div>
    );
  }

  // Default rectangle
  return (
    <div style={commonStyle}>
      {label || ''}
    </div>
  );
}

const nodeTypes: NodeTypes = {
  shape: ShapeNode,
};

export default function Canvas({ elements }: { elements: Element[] }) {
  // Apply smart layout styling
  const styledElements = useMemo(() => applySmartLayout(elements), [elements]);

  // Convert elements to React Flow nodes and edges
  const { nodes, edges } = useMemo(() => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];
    let nodeIdCounter = 0;
    let edgeIdCounter = 0;

    // Map to track element IDs for connectors
    const elementIdMap = new Map<string, string>();

    styledElements.forEach((el, index) => {
      const nodeId = el.id || `node-${nodeIdCounter++}`;

      if (el.id) {
        elementIdMap.set(el.id, nodeId);
      }

      // Handle connectors as edges
      if (el.type === 'connector' && el.from_point && el.to_point) {
        const edgeId = `edge-${edgeIdCounter++}`;

        // Create invisible nodes at connector endpoints if they don't exist
        const sourceId = `connector-source-${edgeId}`;
        const targetId = `connector-target-${edgeId}`;

        nodes.push({
          id: sourceId,
          type: 'default',
          position: { x: el.from_point.x, y: el.from_point.y },
          data: { label: '' },
          style: { opacity: 0, width: 1, height: 1 },
        });

        nodes.push({
          id: targetId,
          type: 'default',
          position: { x: el.to_point.x, y: el.to_point.y },
          data: { label: '' },
          style: { opacity: 0, width: 1, height: 1 },
        });

        edges.push({
          id: edgeId,
          source: sourceId,
          target: targetId,
          label: el.label || '',
          style: {
            stroke: el.color || '#6b7280',
            strokeWidth: el.borderWidth || 2,
          },
          type: 'straight',
          animated: false,
          labelStyle: {
            fill: el.color || '#000',
            fontSize: 12,
            fontWeight: '500',
          },
          labelBgStyle: {
            fill: '#ffffff',
            fillOpacity: 0.9,
          },
        });
        return;
      }

      // Handle arrow/line as edges
      if ((el.type === 'arrow' || el.type === 'line') && el.width !== undefined) {
        const edgeId = `edge-${edgeIdCounter++}`;
        const sourceId = `line-source-${edgeId}`;
        const targetId = `line-target-${edgeId}`;

        const x2 = el.x + (el.width || 0);
        const y2 = el.y + (el.height || 0);

        nodes.push({
          id: sourceId,
          type: 'default',
          position: { x: el.x, y: el.y },
          data: { label: '' },
          style: { opacity: 0, width: 1, height: 1 },
        });

        nodes.push({
          id: targetId,
          type: 'default',
          position: { x: x2, y: y2 },
          data: { label: '' },
          style: { opacity: 0, width: 1, height: 1 },
        });

        edges.push({
          id: edgeId,
          source: sourceId,
          target: targetId,
          style: {
            stroke: el.color || '#000',
            strokeWidth: 2,
          },
          type: el.type === 'arrow' ? 'default' : 'straight',
          animated: false,
        });
        return;
      }

      // Handle regular shapes as nodes
      if (['circle', 'rect', 'rectangle', 'text', 'textbox'].includes(el.type)) {
        nodes.push({
          id: nodeId,
          type: 'shape',
          position: { x: el.x, y: el.y },
          data: {
            shapeType: el.type,
            label: el.label || el.text,
            color: el.color,
            backgroundColor: el.backgroundColor,
            borderColor: el.borderColor,
            borderWidth: el.borderWidth,
            width: el.width,
            height: el.height,
            radius: el.radius,
            fontSize: el.fontSize,
            fontWeight: el.fontWeight,
            opacity: el.opacity,
            labelColor: el.labelColor,
            textAlign: el.textAlign,
          },
          style: {
            background: 'transparent',
            border: 'none',
            padding: 0,
          },
          draggable: true,
        });
      } else if (el.type === 'image') {
        // Handle images with proxy support
        nodes.push({
          id: nodeId,
          type: 'shape',
          position: { x: el.x, y: el.y },
          data: {
            shapeType: 'image',
            src: el.src,
            label: el.label,
            width: el.width,
            height: el.height,
          },
          style: {
            background: 'transparent',
            border: 'none',
            padding: 0,
          },
          draggable: true,
        });
      } else if (['triangle', 'ellipse', 'polygon', 'polyline'].includes(el.type)) {
        // For unsupported shapes, create a text node placeholder
        nodes.push({
          id: nodeId,
          type: 'shape',
          position: { x: el.x, y: el.y },
          data: {
            shapeType: 'text',
            label: `${el.type}${el.label ? ': ' + el.label : ''}`,
            color: '#666',
            fontSize: 12,
          },
          style: {
            background: 'transparent',
            border: 'none',
            padding: 0,
          },
          draggable: true,
        });
      }
    });

    return { nodes, edges };
  }, [styledElements]);

  const onNodesChange = useCallback(() => {
    // Handle node changes if needed (e.g., dragging)
  }, []);

  const onEdgesChange = useCallback(() => {
    // Handle edge changes if needed
  }, []);

  return (
    <div style={{ width: '800px', height: '500px', border: '1px solid #e5e7eb' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView={false}
        nodesDraggable={true}
        nodesConnectable={false}
        elementsSelectable={true}
        zoomOnScroll={false}
        panOnScroll={false}
        panOnDrag={true}
        preventScrolling={true}
        minZoom={1}
        maxZoom={1}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
      >
        <Background color="#f8fafc" gap={16} />
        <Controls showInteractive={false} />
        <MiniMap
          nodeColor="#2563eb"
          maskColor="rgba(0, 0, 0, 0.1)"
          style={{ backgroundColor: '#f8fafc' }}
        />
      </ReactFlow>
    </div>
  );
}
