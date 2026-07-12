import { useState } from 'react';
import type { RunStatus } from '../types';

interface SimulationControlsProps {
  runId: string | null;
  status: RunStatus | null;
  onControl: (action: 'start' | 'pause' | 'resume' | 'stop' | 'step', body?: Record<string, unknown>) => void;
  loading?: boolean;
}

export default function SimulationControls({ runId, status, onControl, loading }: SimulationControlsProps) {
  const [speed, setSpeed] = useState(10);
  const [stepCount, setStepCount] = useState(10);

  const canStart = status === 'created' || status === 'paused';
  const canPause = status === 'running';
  const canStop = status === 'running' || status === 'paused' || status === 'created';
  const canStep = status === 'created' || status === 'paused';

  return (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-800 space-y-4">
      <h3 className="text-sm font-semibold text-gray-300">Controls</h3>

      {/* Main buttons */}
      <div className="flex flex-wrap gap-2">
        <button
          disabled={!canStart || loading || !runId}
          onClick={() => onControl(status === 'paused' ? 'resume' : 'start')}
          className="px-4 py-2 rounded-md bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium transition-colors"
        >
          {status === 'paused' ? '▶ Resume' : '▶ Start'}
        </button>
        <button
          disabled={!canPause || loading}
          onClick={() => onControl('pause')}
          className="px-4 py-2 rounded-md bg-yellow-600 hover:bg-yellow-500 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium transition-colors"
        >
          ⏸ Pause
        </button>
        <button
          disabled={!canStop || loading}
          onClick={() => onControl('stop')}
          className="px-4 py-2 rounded-md bg-red-600 hover:bg-red-500 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium transition-colors"
        >
          ⏹ Stop
        </button>
        <button
          disabled={!canStep || loading}
          onClick={() => onControl('step', { ticks: stepCount })}
          className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium transition-colors"
        >
          ⏭ Step {stepCount}
        </button>
      </div>

      {/* Step count */}
      <div className="flex items-center gap-3">
        <label className="text-xs text-gray-400">Steps:</label>
        <input
          type="number"
          min={1}
          max={1000}
          value={stepCount}
          onChange={(e) => setStepCount(Math.max(1, parseInt(e.target.value) || 1))}
          className="w-20 px-2 py-1 rounded bg-gray-800 border border-gray-700 text-sm text-gray-200"
        />
      </div>

      {/* Speed slider */}
      <div className="space-y-1">
        <div className="flex justify-between text-xs text-gray-400">
          <span>Speed</span>
          <span>{speed} ticks/s</span>
        </div>
        <input
          type="range"
          min={1}
          max={60}
          value={speed}
          onChange={(e) => setSpeed(parseInt(e.target.value))}
          className="w-full accent-blue-500"
        />
      </div>

      {/* Status badge */}
      <div className="flex items-center gap-2">
        <div
          className={`w-2 h-2 rounded-full ${
            status === 'running'
              ? 'bg-emerald-400 animate-pulse'
              : status === 'paused'
              ? 'bg-yellow-400'
              : status === 'stopped' || status === 'completed'
              ? 'bg-red-400'
              : 'bg-gray-500'
          }`}
        />
        <span className="text-xs text-gray-400 uppercase tracking-wider">{status ?? 'No run'}</span>
      </div>
    </div>
  );
}
