import React, { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';

// Dynamic import to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface PlotlyRendererProps {
  plotlySpec: {
    data: any[];
    layout?: any;
    config?: any;
  };
}

export default function PlotlyRenderer({ plotlySpec }: PlotlyRendererProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  console.log('[PlotlyRenderer] Rendering with spec:', plotlySpec);

  if (!plotlySpec) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
        <p style={{ fontSize: '16px', marginBottom: '8px' }}>Plotly Renderer Error</p>
        <p style={{ fontSize: '14px' }}>No plotlySpec provided.</p>
      </div>
    );
  }

  // Allow empty data array for equation-only displays (uses annotations instead)
  const hasData = plotlySpec.data && plotlySpec.data.length > 0;
  const hasAnnotations = plotlySpec.layout && plotlySpec.layout.annotations && plotlySpec.layout.annotations.length > 0;

  if (!hasData && !hasAnnotations) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>
        <p style={{ fontSize: '16px', marginBottom: '8px' }}>Plotly Renderer Error</p>
        <p style={{ fontSize: '14px' }}>No data or annotations provided for visualization.</p>
      </div>
    );
  }

  const defaultLayout = {
    autosize: true,
    margin: { l: 60, r: 40, t: 80, b: 60 },
    paper_bgcolor: '#ffffff',
    plot_bgcolor: '#f9fafb',
    font: { family: 'Inter, system-ui, sans-serif', size: 12 },
    ...plotlySpec.layout,
  };

  const defaultConfig = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    ...plotlySpec.config,
  };

  if (!isMounted) {
    return (
      <div style={{
        width: '100%',
        minHeight: '500px',
        backgroundColor: '#ffffff',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#6b7280'
      }}>
        Loading visualization...
      </div>
    );
  }

  return (
    <div style={{
      width: '100%',
      minHeight: '500px',
      backgroundColor: '#ffffff',
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      <Plot
        data={plotlySpec.data}
        layout={defaultLayout}
        config={defaultConfig}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler={true}
      />
    </div>
  );
}
