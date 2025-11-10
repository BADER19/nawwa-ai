import { useState, useEffect, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { apiPost } from '../../lib/api';
import MathExpressionsPanel from './MathExpressionsPanel';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

type MathFunction = {
  id: string;
  expression: string;
  color: string;
  visible: boolean;
};

type Annotation = {
  x: number;
  y: number;
  label: string;
  type: string;
};

type FunctionData = {
  function: {
    points: { x: number[]; y: number[] };
    expression: string;
  };
  derivative?: {
    points: { x: number[]; y: number[] };
    expression: string;
  };
  integral?: {
    points: { x: number[]; y: number[] };
    expression: string;
  };
  annotations?: Annotation[];
  parameters: string[];
  x_range: [number, number];
  y_range: [number, number];
};

const COLORS = ['#2563eb', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

export default function MathInteractiveRenderer({
  initialExpression,
  initialExpressions
}: {
  initialExpression?: string;
  initialExpressions?: string[];
}) {
  // Initialize functions based on what was provided
  const initializeFunctions = () => {
    if (initialExpressions && initialExpressions.length > 0) {
      // Multiple expressions provided
      return initialExpressions.map((expr, index) => ({
        id: String(index + 1),
        expression: expr,
        color: COLORS[index % COLORS.length],
        visible: true
      }));
    } else if (initialExpression) {
      // Single expression provided
      return [{
        id: '1',
        expression: initialExpression,
        color: COLORS[0],
        visible: true
      }];
    } else {
      // No expression provided, use default
      return [{
        id: '1',
        expression: 'x**2 - 4*x + 3',
        color: COLORS[0],
        visible: true
      }];
    }
  };

  const [functions, setFunctions] = useState<MathFunction[]>(initializeFunctions());

  const [functionsData, setFunctionsData] = useState<Map<string, FunctionData>>(new Map());
  const [loading, setLoading] = useState(false);
  const [showDerivatives, setShowDerivatives] = useState(false);
  const [showIntegrals, setShowIntegrals] = useState(false);
  const [showAnnotations, setShowAnnotations] = useState(true);
  const [parameters, setParameters] = useState<Map<string, number>>(new Map());
  const [xRange, setXRange] = useState<[number, number]>([-10, 10]);
  const [yRange, setYRange] = useState<[number, number]>([-10, 10]);

  // Debounce timer
  const [debounceTimer, setDebounceTimer] = useState<NodeJS.Timeout | null>(null);

  const fetchFunctionData = useCallback(async (func: MathFunction) => {
    try {
      const paramValues: Record<string, number> = {};
      parameters.forEach((value, key) => {
        paramValues[key] = value;
      });

      const response = await apiPost<FunctionData>('/visualize/math/interactive', {
        expression: func.expression,
        x_range: xRange,
        y_range: yRange,
        include_derivative: showDerivatives,
        include_integral: showIntegrals,
        include_annotations: showAnnotations,
        parameters: Object.keys(paramValues).length > 0 ? paramValues : undefined
      });

      setFunctionsData(prev => {
        const newMap = new Map(prev);
        newMap.set(func.id, response);
        return newMap;
      });

      // Extract parameters and add sliders
      if (response.parameters && response.parameters.length > 0) {
        setParameters(prev => {
          const newParams = new Map(prev);
          response.parameters.forEach(param => {
            if (!newParams.has(param)) {
              newParams.set(param, 1); // Default value
            }
          });
          return newParams;
        });
      }
    } catch (error) {
      console.error(`Error fetching data for ${func.expression}:`, error);
    }
  }, [xRange, yRange, showDerivatives, showIntegrals, showAnnotations, parameters]);

  const debouncedFetchAll = useCallback(() => {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }

    const timer = setTimeout(() => {
      setLoading(true);
      Promise.all(functions.filter(f => f.visible).map(f => fetchFunctionData(f)))
        .finally(() => setLoading(false));
    }, 400);

    setDebounceTimer(timer);
  }, [functions, fetchFunctionData, debounceTimer]);

  useEffect(() => {
    debouncedFetchAll();
    return () => {
      if (debounceTimer) clearTimeout(debounceTimer);
    };
  }, [functions, showDerivatives, showIntegrals, showAnnotations, parameters, xRange, yRange]);

  const addFunction = () => {
    const newId = String(Date.now());
    setFunctions(prev => [...prev, {
      id: newId,
      expression: 'sin(x)',
      color: COLORS[prev.length % COLORS.length],
      visible: true
    }]);
  };

  const removeFunction = (id: string) => {
    setFunctions(prev => prev.filter(f => f.id !== id));
    setFunctionsData(prev => {
      const newMap = new Map(prev);
      newMap.delete(id);
      return newMap;
    });
  };

  const updateFunction = (id: string, expression: string) => {
    setFunctions(prev => prev.map(f => f.id === id ? { ...f, expression } : f));
  };

  const toggleFunction = (id: string) => {
    setFunctions(prev => prev.map(f => f.id === id ? { ...f, visible: !f.visible } : f));
  };

  // Generate Plotly traces
  const traces: any[] = [];
  const annotations: any[] = [];

  functions.forEach(func => {
    if (!func.visible) return;

    const data = functionsData.get(func.id);
    if (!data) return;

    // Main function trace
    traces.push({
      x: data.function.points.x,
      y: data.function.points.y,
      type: 'scatter',
      mode: 'lines',
      name: data.function.expression,
      line: {
        color: func.color,
        width: 3
      },
      hovertemplate: '<b>(%{x:.2f}, %{y:.2f})</b><extra></extra>'
    });

    // Derivative trace
    if (showDerivatives && data.derivative) {
      traces.push({
        x: data.derivative.points.x,
        y: data.derivative.points.y,
        type: 'scatter',
        mode: 'lines',
        name: `f'(x) = ${data.derivative.expression}`,
        line: {
          color: func.color,
          width: 2,
          dash: 'dash'
        },
        opacity: 0.7,
        hovertemplate: '<b>Derivative: (%{x:.2f}, %{y:.2f})</b><extra></extra>'
      });
    }

    // Integral trace
    if (showIntegrals && data.integral) {
      traces.push({
        x: data.integral.points.x,
        y: data.integral.points.y,
        type: 'scatter',
        mode: 'lines',
        name: `∫f(x) = ${data.integral.expression}`,
        line: {
          color: func.color,
          width: 2,
          dash: 'dot'
        },
        opacity: 0.5,
        hovertemplate: '<b>Integral: (%{x:.2f}, %{y:.2f})</b><extra></extra>'
      });
    }

    // Annotation points
    if (showAnnotations && data.annotations) {
      const annotationPoints = data.annotations.map(ann => ({
        x: ann.x,
        y: ann.y,
        type: ann.type
      }));

      if (annotationPoints.length > 0) {
        traces.push({
          x: annotationPoints.map(p => p.x),
          y: annotationPoints.map(p => p.y),
          type: 'scatter',
          mode: 'markers',
          name: 'Critical Points',
          marker: {
            color: '#ef4444',
            size: 10,
            symbol: 'circle'
          },
          showlegend: false,
          hovertemplate: '<b>(%{x:.2f}, %{y:.2f})</b><extra></extra>'
        });
      }

      // Add annotations as text
      data.annotations.forEach(ann => {
        annotations.push({
          x: ann.x,
          y: ann.y,
          text: ann.label,
          showarrow: true,
          arrowhead: 2,
          arrowsize: 1,
          arrowwidth: 2,
          arrowcolor: '#ef4444',
          ax: 30,
          ay: -30,
          font: {
            size: 11,
            color: '#374151'
          },
          bgcolor: 'rgba(255, 255, 255, 0.9)',
          bordercolor: '#ef4444',
          borderwidth: 1,
          borderpad: 4
        });
      });
    }
  });

  return (
    <div style={{ width: '100%', display: 'flex', gap: '20px' }}>
      {/* Control Panel */}
      <div style={{ width: '300px', flexShrink: 0 }}>
        <MathExpressionsPanel
          functions={functions}
          onAddFunction={addFunction}
          onRemoveFunction={removeFunction}
          onUpdateFunction={updateFunction}
          onToggleFunction={toggleFunction}
        />

        {/* Options */}
        <div style={{ marginTop: '20px', padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
          <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: '#1e293b' }}>Options</h3>

          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showDerivatives}
              onChange={(e) => setShowDerivatives(e.target.checked)}
              style={{ width: '16px', height: '16px' }}
            />
            <span style={{ fontSize: '13px', color: '#475569' }}>Show Derivatives</span>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showIntegrals}
              onChange={(e) => setShowIntegrals(e.target.checked)}
              style={{ width: '16px', height: '16px' }}
            />
            <span style={{ fontSize: '13px', color: '#475569' }}>Show Integrals</span>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showAnnotations}
              onChange={(e) => setShowAnnotations(e.target.checked)}
              style={{ width: '16px', height: '16px' }}
            />
            <span style={{ fontSize: '13px', color: '#475569' }}>Show Annotations</span>
          </label>
        </div>

        {/* Parameter Sliders */}
        {parameters.size > 0 && (
          <div style={{ marginTop: '20px', padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: '#1e293b' }}>Parameters</h3>
            {Array.from(parameters.entries()).map(([param, value]) => (
              <div key={param} style={{ marginBottom: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <label style={{ fontSize: '13px', fontWeight: '500', color: '#475569' }}>{param}</label>
                  <span style={{ fontSize: '12px', color: '#64748b' }}>{value.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="-5"
                  max="5"
                  step="0.1"
                  value={value}
                  onChange={(e) => {
                    const newValue = parseFloat(e.target.value);
                    setParameters(prev => {
                      const newParams = new Map(prev);
                      newParams.set(param, newValue);
                      return newParams;
                    });
                  }}
                  style={{ width: '100%' }}
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Plot Area */}
      <div style={{ flex: 1, position: 'relative' }}>
        {loading && (
          <div style={{ position: 'absolute', top: '10px', right: '10px', padding: '8px 12px', backgroundColor: 'rgba(37, 99, 235, 0.1)', border: '1px solid #2563eb', borderRadius: '4px', fontSize: '12px', color: '#2563eb', zIndex: 10 }}>
            Updating...
          </div>
        )}

        <Plot
          data={traces}
          layout={{
            title: {
              text: 'Interactive Mathematical Visualization',
              font: { size: 18, color: '#1e293b', family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }
            },
            xaxis: {
              title: { text: 'x' },
              gridcolor: '#e5e7eb',
              zerolinecolor: '#94a3b8',
              zerolinewidth: 2,
              range: xRange
            },
            yaxis: {
              title: { text: 'y' },
              gridcolor: '#e5e7eb',
              zerolinecolor: '#94a3b8',
              zerolinewidth: 2,
              range: yRange
            },
            plot_bgcolor: '#ffffff',
            paper_bgcolor: '#ffffff',
            annotations: annotations,
            hovermode: 'closest',
            legend: {
              x: 1,
              xanchor: 'right',
              y: 1,
              bgcolor: 'rgba(255, 255, 255, 0.9)',
              bordercolor: '#e5e7eb',
              borderwidth: 1
            },
            margin: { l: 60, r: 40, t: 60, b: 50 }
          }}
          config={{
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            toImageButtonOptions: {
              format: 'png',
              filename: 'math_plot',
              height: 800,
              width: 1200
            }
          }}
          style={{ width: '100%', height: '600px' }}
          useResizeHandler={true}
        />
      </div>
    </div>
  );
}
