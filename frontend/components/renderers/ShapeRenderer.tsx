import React from 'react';

interface ShapeElement {
  type: 'circle' | 'rect' | 'triangle' | 'ellipse' | 'line' | 'text' | 'polygon' | 'path';
  x: number;
  y: number;
  radius?: number;
  width?: number;
  height?: number;
  color?: string;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  label?: string;
  text?: string;
  fontSize?: number;
  points?: Array<{ x: number; y: number }>;
  path?: string;
  opacity?: number;
}

interface ShapeRendererProps {
  elements: ShapeElement[];
  width?: number;
  height?: number;
}

export default function ShapeRenderer({ elements, width = 800, height = 600 }: ShapeRendererProps) {
  return (
    <div
      style={{
        width: '100%',
        minHeight: '500px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#ffffff',
        padding: '40px',
      }}
    >
      <svg width={width} height={height} style={{ border: '1px solid #e5e7eb', borderRadius: '8px' }}>
        <rect width={width} height={height} fill="#ffffff" />

        {elements.map((element, index) => {
          const fill = element.fill || element.color || '#3b82f6';
          const stroke = element.stroke || '#1e40af';
          const strokeWidth = element.strokeWidth || 2;
          const opacity = element.opacity || 1;

          switch (element.type) {
            case 'circle':
              return (
                <g key={index}>
                  <circle
                    cx={element.x}
                    cy={element.y}
                    r={element.radius || 50}
                    fill={fill}
                    stroke={stroke}
                    strokeWidth={strokeWidth}
                    opacity={opacity}
                  />
                  {element.label && (
                    <text
                      x={element.x}
                      y={element.y - (element.radius || 50) - 10}
                      fontSize={14}
                      fontWeight="500"
                      fill="#1e293b"
                      fontFamily="Inter, Helvetica, Arial, sans-serif"
                      textAnchor="middle"
                    >
                      {element.label}
                    </text>
                  )}
                </g>
              );

            case 'rect':
              return (
                <g key={index}>
                  <rect
                    x={element.x}
                    y={element.y}
                    width={element.width || 100}
                    height={element.height || 60}
                    fill={fill}
                    stroke={stroke}
                    strokeWidth={strokeWidth}
                    opacity={opacity}
                    rx={8}
                    ry={8}
                  />
                  {element.label && (
                    <text
                      x={element.x + (element.width || 100) / 2}
                      y={element.y - 10}
                      fontSize={14}
                      fontWeight="500"
                      fill="#1e293b"
                      fontFamily="Inter, Helvetica, Arial, sans-serif"
                      textAnchor="middle"
                    >
                      {element.label}
                    </text>
                  )}
                </g>
              );

            case 'ellipse':
              return (
                <g key={index}>
                  <ellipse
                    cx={element.x}
                    cy={element.y}
                    rx={(element.width || 100) / 2}
                    ry={(element.height || 60) / 2}
                    fill={fill}
                    stroke={stroke}
                    strokeWidth={strokeWidth}
                    opacity={opacity}
                  />
                  {element.label && (
                    <text
                      x={element.x}
                      y={element.y - (element.height || 60) / 2 - 10}
                      fontSize={14}
                      fontWeight="500"
                      fill="#1e293b"
                      fontFamily="Inter, Helvetica, Arial, sans-serif"
                      textAnchor="middle"
                    >
                      {element.label}
                    </text>
                  )}
                </g>
              );

            case 'triangle':
              const triWidth = element.width || 80;
              const triHeight = element.height || 80;
              const points = `${element.x + triWidth / 2},${element.y} ${element.x},${element.y + triHeight} ${element.x + triWidth},${element.y + triHeight}`;
              return (
                <g key={index}>
                  <polygon
                    points={points}
                    fill={fill}
                    stroke={stroke}
                    strokeWidth={strokeWidth}
                    opacity={opacity}
                  />
                  {element.label && (
                    <text
                      x={element.x + triWidth / 2}
                      y={element.y - 10}
                      fontSize={14}
                      fontWeight="500"
                      fill="#1e293b"
                      fontFamily="Inter, Helvetica, Arial, sans-serif"
                      textAnchor="middle"
                    >
                      {element.label}
                    </text>
                  )}
                </g>
              );

            case 'line':
              return (
                <line
                  key={index}
                  x1={element.x}
                  y1={element.y}
                  x2={element.x + (element.width || 100)}
                  y2={element.y + (element.height || 0)}
                  stroke={stroke}
                  strokeWidth={strokeWidth || 3}
                  opacity={opacity}
                />
              );

            case 'text':
              return (
                <text
                  key={index}
                  x={element.x}
                  y={element.y}
                  fontSize={element.fontSize || 16}
                  fill={element.color || '#000000'}
                  fontFamily="Inter, Helvetica, Arial, sans-serif"
                  opacity={opacity}
                >
                  {element.text || element.label || ''}
                </text>
              );

            case 'polygon':
              if (element.points && element.points.length > 0) {
                const polyPoints = element.points
                  .map(p => `${element.x + p.x},${element.y + p.y}`)
                  .join(' ');
                return (
                  <g key={index}>
                    <polygon
                      points={polyPoints}
                      fill={fill}
                      stroke={stroke}
                      strokeWidth={strokeWidth}
                      opacity={opacity}
                    />
                    {element.label && (
                      <text
                        x={element.x}
                        y={element.y - 20}
                        fontSize={14}
                        fontWeight="500"
                        fill="#1e293b"
                        fontFamily="Inter, Helvetica, Arial, sans-serif"
                        textAnchor="middle"
                      >
                        {element.label}
                      </text>
                    )}
                  </g>
                );
              }
              return null;

            case 'path':
              if (element.path) {
                return (
                  <g key={index}>
                    <path
                      d={element.path}
                      fill={fill}
                      stroke={stroke}
                      strokeWidth={strokeWidth}
                      opacity={opacity}
                      transform={`translate(${element.x},${element.y})`}
                    />
                    {element.label && (
                      <text
                        x={element.x}
                        y={element.y - 20}
                        fontSize={14}
                        fontWeight="500"
                        fill="#1e293b"
                        fontFamily="Inter, Helvetica, Arial, sans-serif"
                        textAnchor="middle"
                      >
                        {element.label}
                      </text>
                    )}
                  </g>
                );
              }
              return null;

            default:
              return null;
          }
        })}
      </svg>
    </div>
  );
}
