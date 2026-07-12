import { useSimulationStore } from '../store/simulationStore';

function MetricCard({ label, value, unit }: { label: string; value: string | number; unit?: string }) {
  return (
    <div className="bg-gray-900 rounded-lg p-3 border border-gray-800">
      <div className="text-xs text-gray-500 uppercase tracking-wider">{label}</div>
      <div className="text-xl font-bold text-gray-100 mt-1">
        {value}
        {unit && <span className="text-sm text-gray-400 ml-1">{unit}</span>}
      </div>
    </div>
  );
}

export default function MetricsPanel() {
  const state = useSimulationStore((s) => s.state);

  if (!state) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="bg-gray-900 rounded-lg p-3 border border-gray-800 h-16 animate-pulse" />
        ))}
      </div>
    );
  }

  const m = state.metrics;
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      <MetricCard label="Gini Coefficient" value={m.gini.toFixed(3)} />
      <MetricCard label="Total Wealth" value={m.total_wealth.toLocaleString()} />
      <MetricCard label="Agents Alive" value={state.agents_summary.alive_count.toLocaleString()} />
      <MetricCard label="Tick" value={state.tick.toLocaleString()} />
      <MetricCard label="Generation" value={state.generation} />
    </div>
  );
}
