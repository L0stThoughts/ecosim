import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import client from '../api/client';
import type { Run } from '../types';

export default function RunHistory() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    client.get<Run[]>('/runs')
      .then((res) => setRuns(res.data))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-center text-gray-400">Loading history…</div>;
  if (error) return <div className="p-8 text-center text-red-400">Error: {error}</div>;

  const completed = runs.filter((r) => r.status === 'completed' || r.status === 'stopped');

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Run History</h1>
          <Link to="/" className="text-blue-400 hover:underline text-sm">← Back</Link>
        </div>

        {completed.length === 0 ? (
          <p className="text-gray-500">No completed runs yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400">
                  <th className="text-left py-2 px-3">Run ID</th>
                  <th className="text-left py-2 px-3">Status</th>
                  <th className="text-right py-2 px-3">Agents</th>
                  <th className="text-right py-2 px-3">Ticks</th>
                  <th className="text-right py-2 px-3">Generations</th>
                  <th className="text-left py-2 px-3">Created</th>
                  <th className="text-right py-2 px-3">Gini</th>
                  <th className="text-right py-2 px-3">Avg Wealth</th>
                </tr>
              </thead>
              <tbody>
                {completed.map((run) => (
                  <tr key={run.run_id} className="border-b border-gray-900 hover:bg-gray-900/50">
                    <td className="py-2 px-3">
                      <Link to={`/sim/${run.run_id}`} className="text-blue-400 hover:underline font-mono text-xs">
                        {run.run_id.slice(0, 8)}
                      </Link>
                    </td>
                    <td className="py-2 px-3">
                      <span className={run.status === 'completed' ? 'text-green-400' : 'text-yellow-400'}>
                        {run.status}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-right">{run.config.num_agents}</td>
                    <td className="py-2 px-3 text-right">{run.total_ticks}</td>
                    <td className="py-2 px-3 text-right">{run.generations}</td>
                    <td className="py-2 px-3 text-gray-400">{new Date(run.created_at).toLocaleString()}</td>
                    <td className="py-2 px-3 text-right">{run.final_metrics.gini?.toFixed(3) ?? '—'}</td>
                    <td className="py-2 px-3 text-right">{run.final_metrics.average_wealth?.toFixed(1) ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
