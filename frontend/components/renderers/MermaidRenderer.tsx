import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

interface MermaidRendererProps {
  mermaidCode: string;
}

// Minimal Elegance Theme - Black & White with Accent Color
const MINIMAL_ELEGANCE_THEME = {
  theme: 'base' as const,
  themeVariables: {
    // Primary colors - Black, White, and sophisticated accent
    primaryColor: '#ffffff',
    primaryTextColor: '#000000',
    primaryBorderColor: '#000000',

    // Secondary elements
    secondaryColor: '#f5f5f5',
    secondaryTextColor: '#000000',
    secondaryBorderColor: '#000000',

    // Accent color - Deep charcoal for subtle highlights
    tertiaryColor: '#2a2a2a',
    tertiaryTextColor: '#ffffff',
    tertiaryBorderColor: '#000000',

    // Lines and edges - thin, elegant
    lineColor: '#000000',

    // Background
    background: '#ffffff',
    mainBkg: '#ffffff',
    secondBkg: '#f5f5f5',

    // Text
    textColor: '#000000',
    fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
    fontSize: '14px',

    // Borders - thin and elegant
    nodeBorder: '#000000',
    clusterBorder: '#000000',
    defaultLinkColor: '#000000',

    // Edge styling
    edgeLabelBackground: '#ffffff',

    // Flowchart specific
    nodeTextColor: '#000000',

    // Class diagram
    classText: '#000000',

    // State diagram
    labelColor: '#000000',

    // Sequence diagram
    actorBorder: '#000000',
    actorBkg: '#ffffff',
    actorTextColor: '#000000',
    actorLineColor: '#000000',
    signalColor: '#000000',
    signalTextColor: '#000000',
    labelBoxBkgColor: '#f5f5f5',
    labelBoxBorderColor: '#000000',
    labelTextColor: '#000000',
    loopTextColor: '#000000',
    activationBorderColor: '#000000',
    activationBkgColor: '#f5f5f5',
    sequenceNumberColor: '#000000',
  },
};

export default function MermaidRenderer({ mermaidCode }: MermaidRendererProps) {
  const mermaidRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  console.log('[MermaidRenderer] Received mermaidCode:', mermaidCode);
  console.log('[MermaidRenderer] Code length:', mermaidCode?.length || 0);

  useEffect(() => {
    console.log('[MermaidRenderer useEffect] Starting render with code:', mermaidCode);
    // Initialize Mermaid with custom theme
    mermaid.initialize({
      startOnLoad: false,
      ...MINIMAL_ELEGANCE_THEME,
      flowchart: {
        curve: 'linear', // Clean straight lines for minimal aesthetic
        padding: 20,
        nodeSpacing: 80,
        rankSpacing: 100,
        htmlLabels: true,
      },
      sequence: {
        diagramMarginX: 50,
        diagramMarginY: 30,
        boxTextMargin: 10,
        noteMargin: 15,
        messageMargin: 50,
      },
      gantt: {
        titleTopMargin: 30,
        barHeight: 30,
        barGap: 10,
        topPadding: 75,
        leftPadding: 150,
        gridLineStartPadding: 40,
        fontSize: 14,
      },
    });

    const renderDiagram = async () => {
      if (!mermaidRef.current || !mermaidCode) return;

      try {
        setError(null);

        // Clear previous content
        mermaidRef.current.innerHTML = '';

        // Generate unique ID
        const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        // Render the diagram
        const { svg } = await mermaid.render(id, mermaidCode);

        // Insert the SVG
        mermaidRef.current.innerHTML = svg;

        // Apply additional custom styles for minimal elegance
        const svgElement = mermaidRef.current.querySelector('svg');
        if (svgElement) {
          svgElement.style.maxWidth = '100%';
          svgElement.style.height = 'auto';

          // Make lines thinner and more elegant
          const paths = svgElement.querySelectorAll('path.path, line');
          paths.forEach((path) => {
            (path as SVGElement).style.strokeWidth = '1.5';
          });

          // Ensure clean typography
          const texts = svgElement.querySelectorAll('text');
          texts.forEach((text) => {
            (text as SVGElement).style.fontFamily = '"Inter", "Helvetica Neue", Arial, sans-serif';
            (text as SVGElement).style.fontWeight = '400';
            (text as SVGElement).style.letterSpacing = '0.01em';
          });

          // Add subtle shadows to nodes for depth
          const rects = svgElement.querySelectorAll('rect.node, rect.label-container');
          rects.forEach((rect) => {
            (rect as SVGElement).style.filter = 'drop-shadow(0 2px 8px rgba(0, 0, 0, 0.08))';
          });
        }

      } catch (err) {
        console.error('Mermaid rendering error:', err);
        setError(err instanceof Error ? err.message : 'Failed to render diagram');
      }
    };

    renderDiagram();
  }, [mermaidCode]);

  if (error) {
    return (
      <div style={{
        width: '100%',
        minHeight: '400px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#fafafa',
        border: '1px solid #e0e0e0',
        borderRadius: '4px',
        padding: '40px',
      }}>
        <div style={{
          fontSize: '14px',
          color: '#666',
          marginBottom: '12px',
          fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
        }}>
          Diagram rendering error
        </div>
        <div style={{
          fontSize: '12px',
          color: '#999',
          fontFamily: 'monospace',
          whiteSpace: 'pre-wrap',
          maxWidth: '600px',
          textAlign: 'center',
        }}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div style={{
      width: '100%',
      minHeight: '400px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#ffffff',
      padding: '40px',
      fontFamily: '"Inter", "Helvetica Neue", Arial, sans-serif',
    }}>
      <div
        ref={mermaidRef}
        style={{
          width: '100%',
          display: 'flex',
          justifyContent: 'center',
        }}
      />
    </div>
  );
}
