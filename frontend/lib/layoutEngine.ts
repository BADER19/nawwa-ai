// Smart layout engine that adds visual polish to raw LLM output

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
  [key: string]: any;
};

// Professional color palette
const COLORS = {
  primary: '#2563eb',      // Blue
  secondary: '#14b8a6',    // Teal
  accent: '#f59e0b',       // Amber
  success: '#10b981',      // Green
  warning: '#f97316',      // Orange
  danger: '#ef4444',       // Red
  neutral: '#6b7280',      // Gray
  background: '#f8fafc',   // Light gray
  text: '#1e293b',         // Dark gray
  textLight: '#64748b',    // Medium gray
};

// Modern styling defaults
const STYLE_DEFAULTS = {
  rect: {
    rx: 8,                          // Rounded corners
    ry: 8,
    shadow: {
      color: 'rgba(0, 0, 0, 0.1)',
      blur: 12,
      offsetX: 0,
      offsetY: 4,
    },
    stroke: COLORS.primary,
    strokeWidth: 2,
    fill: '#ffffff',
  },
  circle: {
    shadow: {
      color: 'rgba(0, 0, 0, 0.1)',
      blur: 12,
      offsetX: 0,
      offsetY: 4,
    },
    stroke: COLORS.primary,
    strokeWidth: 2,
    fill: '#ffffff',
  },
  connector: {
    stroke: COLORS.neutral,
    strokeWidth: 2,
    smooth: true, // Enable curve smoothing
  },
  text: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: 14,
    fontWeight: '500',
    fill: COLORS.text,
  },
};

/**
 * Apply smart layout and styling to elements
 */
export function applySmartLayout(elements: Element[]): Element[] {
  if (!elements || elements.length === 0) return [];

  const styled: Element[] = [];
  const elementMap = new Map<string, Element>();

  // First pass: apply styling and collect element positions
  for (const el of elements) {
    const styledEl = { ...el };

    // Apply type-specific styling
    if (el.type === 'rect' || el.type === 'rectangle') {
      // Smart color selection based on background color
      const bgColor = el.backgroundColor || COLORS.background;
      const textColor = isLightColor(bgColor) ? COLORS.text : '#ffffff';

      Object.assign(styledEl, {
        backgroundColor: bgColor,
        borderColor: el.borderColor || darkenColor(bgColor, 20),
        borderWidth: el.borderWidth || 2,
        rx: 8,
        ry: 8,
        shadow: STYLE_DEFAULTS.rect.shadow,
        // Enhance label styling
        labelColor: textColor,
        fontSize: el.fontSize || 14,
        fontWeight: el.fontWeight || '600',
      });
    } else if (el.type === 'circle') {
      const bgColor = el.backgroundColor || el.color || COLORS.background;
      const textColor = isLightColor(bgColor) ? COLORS.text : '#ffffff';

      Object.assign(styledEl, {
        backgroundColor: bgColor,
        borderColor: el.borderColor || darkenColor(bgColor, 20),
        borderWidth: el.borderWidth || 2,
        shadow: STYLE_DEFAULTS.circle.shadow,
        labelColor: textColor,
        fontSize: el.fontSize || 14,
        fontWeight: el.fontWeight || '600',
      });
    } else if (el.type === 'connector') {
      Object.assign(styledEl, {
        color: el.color || COLORS.neutral,
        borderWidth: el.borderWidth || 2,
        smooth: true,
        arrowStyle: 'triangle',
        labelBg: '#ffffff',
        labelPadding: 8,
      });
    } else if (el.type === 'textbox' || el.type === 'text') {
      Object.assign(styledEl, {
        fontSize: el.fontSize || 14,
        fontWeight: el.fontWeight || 'normal',
        color: el.color || COLORS.text,
        fontFamily: STYLE_DEFAULTS.text.fontFamily,
      });
    }

    styled.push(styledEl);
    if (el.id) {
      elementMap.set(el.id, styledEl);
    }
  }

  // Second pass: adjust connector endpoints to attach to shape edges
  for (const el of styled) {
    if (el.type === 'connector' && el.from_point && el.to_point) {
      // Find if connector is between two identified elements
      // This would require element IDs in the spec - skip for now
      // Future enhancement: calculate edge attachment points
    }
  }

  return styled;
}

/**
 * Auto-layout elements in a flowchart pattern
 */
export function autoLayoutFlowchart(elements: Element[]): Element[] {
  const nodes = elements.filter(e => e.type === 'rect' || e.type === 'circle');
  const connectors = elements.filter(e => e.type === 'connector');
  const others = elements.filter(e => e.type !== 'rect' && e.type !== 'circle' && e.type !== 'connector');

  // Apply vertical flowchart layout
  const startX = 100;
  const startY = 80;
  const verticalGap = 120;
  const horizontalGap = 200;

  let currentY = startY;
  let maxWidth = 0;

  const laid = nodes.map((node, idx) => {
    const width = node.width || 180;
    const height = node.height || 80;
    maxWidth = Math.max(maxWidth, width);

    const laidNode = {
      ...node,
      x: startX + (800 - width) / 4, // Center-ish
      y: currentY,
      width,
      height,
    };

    currentY += height + verticalGap;
    return laidNode;
  });

  // Reconnect connectors to new positions
  const laidConnectors = connectors.map(conn => {
    // Simple pass-through for now
    // Future: calculate proper edge attachment
    return conn;
  });

  return [...laid, ...laidConnectors, ...others];
}

/**
 * Check if a color is light (for contrast calculation)
 */
function isLightColor(color: string): boolean {
  const hex = color.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  return brightness > 155;
}

/**
 * Darken a hex color by a percentage
 */
function darkenColor(color: string, percent: number): string {
  const hex = color.replace('#', '');
  const r = Math.max(0, parseInt(hex.substr(0, 2), 16) - Math.round(255 * percent / 100));
  const g = Math.max(0, parseInt(hex.substr(2, 2), 16) - Math.round(255 * percent / 100));
  const b = Math.max(0, parseInt(hex.substr(4, 2), 16) - Math.round(255 * percent / 100));
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

/**
 * Lighten a hex color by a percentage
 */
function lightenColor(color: string, percent: number): string {
  const hex = color.replace('#', '');
  const r = Math.min(255, parseInt(hex.substr(0, 2), 16) + Math.round(255 * percent / 100));
  const g = Math.min(255, parseInt(hex.substr(2, 2), 16) + Math.round(255 * percent / 100));
  const b = Math.min(255, parseInt(hex.substr(4, 2), 16) + Math.round(255 * percent / 100));
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}
