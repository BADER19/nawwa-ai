import { useState, useRef, useEffect } from 'react';
import { Mic, Square, Loader2 } from 'lucide-react';
import { api } from '../lib/api';

interface VoiceInputProps {
  onTranscription: (transcription: string, visualization: any) => void;
  disabled?: boolean;
  tierAllowed?: boolean;
}

export default function VoiceInput({ onTranscription, disabled, tierAllowed = false }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const startRecording = async () => {
    try {
      setError(null);

      // Check browser support
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError('Voice input not supported in this browser. Try Chrome or Edge.');
        return;
      }

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });

      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await sendAudioToBackend(audioBlob);

        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (err: any) {
      console.error('Error starting recording:', err);
      if (err.name === 'NotAllowedError') {
        setError('Microphone access denied. Please allow microphone access.');
      } else {
        setError('Failed to start recording. Please try again.');
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const sendAudioToBackend = async (audioBlob: Blob) => {
    setIsProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      const response = await api.post('/visualize/voice/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const { transcription, visualization, usage_count } = response.data;

      console.log('[VoiceInput] Transcription:', transcription);
      console.log('[VoiceInput] Visualization:', visualization);

      // Callback with results
      onTranscription(transcription, visualization);

    } catch (err: any) {
      console.error('[VoiceInput] Error:', err);

      if (err.response?.status === 403) {
        setError('Voice input requires PRO tier. Upgrade to unlock!');
      } else if (err.response?.status === 429) {
        setError('Daily quota exceeded. Upgrade for unlimited access.');
      } else {
        setError(err.response?.data?.detail || 'Failed to process voice. Please try again.');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Show upgrade message if tier not allowed
  if (!tierAllowed) {
    return (
      <button
        onClick={() => window.location.href = '/pricing'}
        className="p-2 rounded-lg border border-gray-300 hover:border-purple-500 hover:bg-purple-50 transition-all duration-200"
        title="Voice input requires PRO tier"
      >
        <Mic size={20} className="text-gray-400" />
      </button>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {!isRecording && !isProcessing && (
        <button
          onClick={startRecording}
          disabled={disabled}
          className={`p-2 rounded-lg border transition-all duration-200 ${
            disabled
              ? 'border-gray-200 bg-gray-50 cursor-not-allowed'
              : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50 active:scale-95'
          }`}
          title="Start voice recording"
        >
          <Mic size={20} className={disabled ? 'text-gray-400' : 'text-gray-700'} />
        </button>
      )}

      {isRecording && (
        <div className="flex items-center gap-2 px-3 py-2 bg-red-50 border border-red-300 rounded-lg animate-pulse">
          <button
            onClick={stopRecording}
            className="p-1 rounded hover:bg-red-200 transition-colors"
            title="Stop recording"
          >
            <Square size={16} className="text-red-600 fill-red-600" />
          </button>
          <span className="text-sm font-mono text-red-700">{formatTime(recordingTime)}</span>
          <span className="text-xs text-red-600">Recording...</span>
        </div>
      )}

      {isProcessing && (
        <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 border border-blue-300 rounded-lg">
          <Loader2 size={16} className="text-blue-600 animate-spin" />
          <span className="text-sm text-blue-700">Transcribing...</span>
        </div>
      )}

      {error && (
        <div className="px-3 py-2 bg-red-50 border border-red-300 rounded-lg">
          <p className="text-xs text-red-700">{error}</p>
        </div>
      )}
    </div>
  );
}
