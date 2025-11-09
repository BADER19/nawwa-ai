import React from 'react';

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

export default function ConceptualRenderer({ elements }: { elements: Element[] | null }) {
  console.log('[ConceptualRenderer] Rendering with elements:', elements);

  if (!elements || elements.length === 0) {
    console.warn('[ConceptualRenderer] No elements provided - this renderer requires element-based data');
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
        <p style={{ fontSize: '16px', marginBottom: '8px' }}>ConceptualRenderer Error</p>
        <p style={{ fontSize: '14px' }}>No diagram elements received. This visualization may require a different renderer.</p>
      </div>
    );
  }

  // Check if this is an AI-generated image visualization
  const hasImage = elements.length === 1 && elements[0].type === 'image' && elements[0].src;

  // If it's an AI-generated image, display it full-size centered
  if (hasImage) {
    const imageElement = elements[0];
    const [imageError, setImageError] = React.useState(false);
    const [imageLoaded, setImageLoaded] = React.useState(false);

    // Use proxy endpoint for external URLs to avoid CORS issues
    // Data URLs (base64) can be used directly
    const imageSrc = imageElement.src.startsWith('data:')
      ? imageElement.src
      : `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:18001'}/image/proxy?url=${encodeURIComponent(imageElement.src)}`;

    return (
      <div style={{
        width: '100%',
        height: '100%',
        minHeight: '600px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f8fafc',
        padding: '20px',
        borderRadius: '8px',
        position: 'relative'
      }}>
        {!imageLoaded && !imageError && (
          <div style={{ textAlign: 'center', color: '#64748b' }}>
            <div style={{
              width: '40px',
              height: '40px',
              border: '3px solid #e2e8f0',
              borderTopColor: '#3b82f6',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 12px'
            }} />
            <p>Loading image...</p>
          </div>
        )}
        {imageError ? (
          <div style={{ textAlign: 'center', color: '#ef4444' }}>
            <p style={{ fontSize: '16px', marginBottom: '8px' }}>Failed to load image</p>
            <p style={{ fontSize: '14px', color: '#64748b' }}>URL: {imageElement.src}</p>
            <a
              href={imageElement.src}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                color: '#3b82f6',
                textDecoration: 'underline',
                fontSize: '14px',
                marginTop: '8px',
                display: 'inline-block'
              }}
            >
              Open image in new tab
            </a>
          </div>
        ) : (
          <img
            src={imageSrc}
            alt="AI Generated Visualization"
            style={{
              maxWidth: '100%',
              maxHeight: '100%',
              objectFit: 'contain',
              borderRadius: '8px',
              boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
              display: imageLoaded ? 'block' : 'none'
            }}
            onLoad={() => {
              console.log('[ConceptualRenderer] Image loaded successfully:', imageElement.src);
              setImageLoaded(true);
            }}
            onError={(e) => {
              console.error('[ConceptualRenderer] Image failed to load:', imageElement.src, e);
              setImageError(true);
            }}
          />
        )}
        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // Render SVG-based diagram
  const width = 800;
  const height = 600;

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
      <svg width={width} height={height} style={{ border: '1px solid #e5e7eb', borderRadius: '8px' }}>
        <rect width={width} height={height} fill="#ffffff" />

        {elements.map((element, index) => {
          const fill = element.backgroundColor || element.color || '#3b82f6';
          const stroke = element.borderColor || '#1e40af';
          const strokeWidth = element.borderWidth || 2;
          const opacity = element.opacity || 1;

          // Render connectors/arrows
          if (element.type === 'connector' && element.from_point && element.to_point) {
            const { from_point, to_point } = element;
            const midX = (from_point.x + to_point.x) / 2;
            const midY = (from_point.y + to_point.y) / 2;

            return (
              <g key={index}>
                <line
                  x1={from_point.x}
                  y1={from_point.y}
                  x2={to_point.x}
                  y2={to_point.y}
                  stroke={stroke}
                  strokeWidth={strokeWidth}
                  markerEnd="url(#arrowhead)"
                />
                {element.label && (
                  <text
                    x={midX}
                    y={midY - 5}
                    fontSize={12}
                    fill="#64748b"
                    fontFamily="Inter, Helvetica, Arial, sans-serif"
                    textAnchor="middle"
                    style={{ backgroundColor: '#ffffff', padding: '2px 4px' }}
                  >
                    {element.label}
                  </text>
                )}
              </g>
            );
          }

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
                      y={element.y}
                      fontSize={element.fontSize || 14}
                      fontWeight={element.fontWeight || '600'}
                      fill="#ffffff"
                      fontFamily="Inter, Helvetica, Arial, sans-serif"
                      textAnchor="middle"
                      dominantBaseline="middle"
                    >
                      {element.label}
                    </text>
                  )}
                </g>
              );

            case 'rect':
            case 'rectangle':
              const rectWidth = element.width || 150;
              const rectHeight = element.height || 50;
              return (
                <g key={index}>
                  <rect
                    x={element.x}
                    y={element.y}
                    width={rectWidth}
                    height={rectHeight}
                    fill={fill}
                    stroke={stroke}
                    strokeWidth={strokeWidth}
                    opacity={opacity}
                    rx={8}
                    ry={8}
                  />
                  {element.label && (
                    <text
                      x={element.x + rectWidth / 2}
                      y={element.y + rectHeight / 2}
                      fontSize={element.fontSize || 14}
                      fontWeight={element.fontWeight || '600'}
                      fill="#1e293b"
                      fontFamily="Inter, Helvetica, Arial, sans-serif"
                      textAnchor="middle"
                      dominantBaseline="middle"
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
                      y={element.y}
                      fontSize={element.fontSize || 14}
                      fontWeight={element.fontWeight || '600'}
                      fill="#ffffff"
                      fontFamily="Inter, Helvetica, Arial, sans-serif"
                      textAnchor="middle"
                      dominantBaseline="middle"
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
                      y={element.y + triHeight / 2}
                      fontSize={element.fontSize || 14}
                      fontWeight={element.fontWeight || '600'}
                      fill="#ffffff"
                      fontFamily="Inter, Helvetica, Arial, sans-serif"
                      textAnchor="middle"
                      dominantBaseline="middle"
                    >
                      {element.label}
                    </text>
                  )}
                </g>
              );

            case 'text':
            case 'textbox':
              return (
                <text
                  key={index}
                  x={element.x}
                  y={element.y}
                  fontSize={element.fontSize || 16}
                  fontWeight={element.fontWeight || 'normal'}
                  fill={element.color || '#000000'}
                  fontFamily="Inter, Helvetica, Arial, sans-serif"
                  opacity={opacity}
                >
                  {element.text || element.label || ''}
                </text>
              );

            case 'line':
            case 'arrow':
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
                  markerEnd={element.type === 'arrow' ? 'url(#arrowhead)' : undefined}
                />
              );

            default:
              return null;
          }
        })}

        {/* Arrow marker definition */}
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="3"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path d="M0,0 L0,6 L9,3 z" fill="#1e40af" />
          </marker>
        </defs>
      </svg>
    </div>
  );
}
