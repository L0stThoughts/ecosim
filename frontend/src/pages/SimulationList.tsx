import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSimulation } from '../hooks/useSimulation';
import { useSimulationStore } from '../store/simulationStore';
import { DEFAULT_CONFIG } from '../types';
import type { SimulationConfig } from '../types';

export default function SimulationList() {
  const navigate = useNavigate();
  const { runs, setActiveRunId } = useSimulationStore();
  const { fetchRuns, createRun, loading, error } = useSimulation();
  const [showCreate, setShowCreate] = useState(false);
  const [config, setConfig] = useState<SimulationConfig>({ ...DEFAULT_CONFIG });

  useEffect(() => {
    fetchRuns();
  }, [fetchRuns]);

  const handleCreate = useCallback(async () => {
    const run = await createRun(config);
    if (run) {
      setShowCreate(false);
      navigate('/');
    }
  }, [config, createRun, navigate]);

  const handleSelectRun = useCallback(
    (runId: string) => {
      setActiveRunId(runId);
      navigate('/');
    },
    [setActiveRunId, navigate]
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-100">Simulations</h1>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-500 text-sm font-medium transition-colors"
        >
          + New Simulation
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-900/30 border border-red-800 rounded-lg text-sm text-red-300">{error}</div>
      )}

      {showCreate && (
        <div className="bg-gray-900 rounded-lg p-6 border border-gray-800 space-y-4">
          <h2 className="text-lg font-semibold text-gray-200">Create Simulation</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-xs text-gray-400 block mb-1">Agents</label>
              <input
                type="number"
                value={config.num_agents}
                onChange={(e) => setConfig({ ...config, num_agents: parseInt(e.target.value) || 100 })}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Max Ticks</label>
              <input
                type="number"
                value={config.max_ticks}
                onChange={(e) => setConfig({ ...config, max_ticks: parseInt(e.target.value) || 1000 })}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Tick Rate</label>
              <input
                type="number"
                value={config.tick_rate}
                onChange={(e) => setConfig({ ...config, tick_rate: parseInt(e.target.value) || 5 })}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Seed (optional)</label>
              <input
                type="number"
                value={config.seed ?? ''}
                onChange={(e) => setConfig({ ...config, seed: e.target.value ? parseInt(e.target.value) : null })}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200"
                placeholder="Random"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Zones</label>
              <input
                type="number"
                value={config.zone_count}
                onChange={(e) => setConfig({ ...config, zone_count: parseInt(e.target.value) || 1 })}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Shock Probability</label>
              <input
                type="number"
                step="0.01"
                value={config.shock_probability}
                onChange={(e) => setConfig({ ...config, shock_probability: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200"
              />
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleCreate}
              disabled={loading}
              className="px-4 py-2 rounded-md bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-sm font-medium transition-colors"
            >
              {loading ? 'Creating...' : 'Create & Go'}
            </button>
            <button
              onClick={() => setShowCreate(false)}
              className="px-4 py-2 rounded-md bg-gray-700 hover:bg-gray-600 text-sm font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Runs table */}
      <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-800/50">
            <tr>
              <th className="px-4 py-3 text-left text-xs text-gray-400 uppercase tracking-wider">Run ID</th>
              <th className="px-4 py-3 text-left text-xs text-gray-400 uppercase tracking-wider">Status</th>
              <th className="px-4 py-3 text-left text-xs text-gray-400 uppercase tracking-wider">Ticks</th>
              <th className="px-4 py-3 text-left text-xs text-gray-400 uppercase tracking-wider">Gen</th>
              <th className="px-4 py-3 text-left text-xs text-gray-400 uppercase tracking-wider">Created</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {runs.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  No simulations yet. Create one to get started.
                </td>
              </tr>
            ) : (
              runs.map((run) => (
                <tr key={run.run_id} className="hover:bg-gray-800/30 transition-colors">
                  <td className="px-4 py-3 font-mono text-gray-300">{run.run_id}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs ${
                        run.status === 'running'
                          ? 'bg-emerald-900/50 text-emerald-400'
                          : run.status === 'paused'
                          ? 'bg-yellow-900/50 text-yellow-400'
                          : run.status === 'completed'
                          ? 'bg-blue-900/50 text-blue-400'
                          : 'bg-gray-800 text-gray-400'
                      }`}
                    >
                      {run.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-400">{run.total_ticks}</td>
                  <td className="px-4 py-3 text-gray-400">{run.generations}</td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{new Date(run.created_at).toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleSelectRun(run.run_id)}
                      className="text-xs text-blue-400 hover:text-blue-300"
                    >
                      Open →
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
