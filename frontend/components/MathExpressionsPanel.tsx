import { useState } from 'react';

type MathFunction = {
  id: string;
  expression: string;
  color: string;
  visible: boolean;
};

type Props = {
  functions: MathFunction[];
  onAddFunction: () => void;
  onRemoveFunction: (id: string) => void;
  onUpdateFunction: (id: string, expression: string) => void;
  onToggleFunction: (id: string) => void;
};

export default function MathExpressionsPanel({
  functions,
  onAddFunction,
  onRemoveFunction,
  onUpdateFunction,
  onToggleFunction
}: Props) {
  return (
    <div style={{ padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: '600', color: '#1e293b' }}>Functions</h3>
        <button
          onClick={onAddFunction}
          style={{
            padding: '4px 12px',
            fontSize: '12px',
            fontWeight: '500',
            color: '#2563eb',
            backgroundColor: '#eff6ff',
            border: '1px solid #2563eb',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          + Add
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {functions.map(func => (
          <div
            key={func.id}
            style={{
              padding: '12px',
              backgroundColor: '#ffffff',
              borderRadius: '6px',
              border: '1px solid #e5e7eb'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              {/* Visibility Toggle */}
              <button
                onClick={() => onToggleFunction(func.id)}
                style={{
                  width: '24px',
                  height: '24px',
                  border: 'none',
                  backgroundColor: 'transparent',
                  cursor: 'pointer',
                  fontSize: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title={func.visible ? 'Hide' : 'Show'}
              >
                {func.visible ? '👁️' : '👁️‍🗨️'}
              </button>

              {/* Color Indicator */}
              <div
                style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '3px',
                  backgroundColor: func.color,
                  border: '1px solid #e5e7eb'
                }}
              />

              {/* Label */}
              <span style={{ fontSize: '12px', fontWeight: '500', color: '#64748b', flex: 1 }}>
                f(x) =
              </span>

              {/* Delete Button */}
              {functions.length > 1 && (
                <button
                  onClick={() => onRemoveFunction(func.id)}
                  style={{
                    width: '24px',
                    height: '24px',
                    border: 'none',
                    backgroundColor: 'transparent',
                    color: '#ef4444',
                    cursor: 'pointer',
                    fontSize: '16px',
                    fontWeight: 'bold'
                  }}
                  title="Remove"
                >
                  ×
                </button>
              )}
            </div>

            {/* Expression Input */}
            <input
              type="text"
              value={func.expression}
              onChange={(e) => onUpdateFunction(func.id, e.target.value)}
              placeholder="Enter expression (e.g., x**2)"
              style={{
                width: '100%',
                padding: '8px',
                fontSize: '13px',
                border: '1px solid #cbd5e1',
                borderRadius: '4px',
                fontFamily: 'monospace',
                backgroundColor: func.visible ? '#ffffff' : '#f1f5f9'
              }}
              disabled={!func.visible}
            />

            {/* Example Hints */}
            {func.expression === '' && (
              <div style={{ marginTop: '6px', fontSize: '11px', color: '#94a3b8' }}>
                Examples: x**2, sin(x), a*x + b
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Quick Examples */}
      <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #e5e7eb' }}>
        <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '6px' }}>
          Quick examples:
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
          {['x**2', 'sin(x)', 'exp(x)', 'log(x)', 'abs(x)'].map(example => (
            <button
              key={example}
              onClick={() => {
                if (functions.length > 0) {
                  onUpdateFunction(functions[0].id, example);
                }
              }}
              style={{
                padding: '4px 8px',
                fontSize: '10px',
                fontFamily: 'monospace',
                color: '#475569',
                backgroundColor: '#ffffff',
                border: '1px solid #cbd5e1',
                borderRadius: '3px',
                cursor: 'pointer'
              }}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
