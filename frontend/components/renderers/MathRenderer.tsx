import { useEffect, useState } from 'react';
import { apiPost } from '../../lib/api';

type MathElement = {
  type: string;
  expression?: string;
  domain?: [number, number];
  x?: number;
  y?: number;
  label?: string;
  color?: string;
  xRange?: [number, number];
  yRange?: [number, number];
  xLabel?: string;
  yLabel?: string;
  text?: string;
  anchor?: string;
  [key: string]: any;
};

export default function MathRenderer({ elements }: { elements: MathElement[] }) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPlot = async () => {
      console.log('[MathRenderer] Fetching plot with elements:', elements);
      setLoading(true);
      setError(null);

      try {
        // Request server-side plot generation
        const response = await apiPost<{ imageUrl: string }>('/visualize/math', { elements });
        console.log('[MathRenderer] Received response, imageUrl length:', response.imageUrl?.length);
        setImageUrl(response.imageUrl);
      } catch (err: any) {
        console.error('[MathRenderer] Error fetching math plot:', err);
        setError('Failed to generate mathematical plot. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchPlot();
  }, [elements]);

  if (loading) {
    return (
      <div style={{ width: '800px', height: '500px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ display: 'inline-block', width: '40px', height: '40px', border: '4px solid #e5e7eb', borderTop: '4px solid #2563eb', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
          <p style={{ marginTop: '16px', color: '#6b7280' }}>Rendering plot...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ width: '800px', height: '500px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#fef2f2', borderRadius: '8px', border: '2px solid #ef4444' }}>
        <div style={{ textAlign: 'center', color: '#dc2626', padding: '20px' }}>
          <p style={{ fontWeight: 'bold', marginBottom: '8px' }}>Error</p>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ width: '800px', height: '500px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {imageUrl && <img src={imageUrl} alt="Mathematical plot" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />}
    </div>
  );
}
