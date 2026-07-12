import { useCallback } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { useWebSocket } from '../hooks/useWebSocket';
import { useSimulation } from '../hooks/useSimulation';
import AgentMap from '../components/AgentMap';
import WealthChart from '../components/WealthChart';
import StrategyEvolution from '../components/StrategyEvolution';
import MetricsPanel from '../components/MetricsPanel';
import SimulationControls from '../components/SimulationControls';
import AgentInspector from '../components/AgentInspector';

export default function Dashboard() {
  const { activeRunId, state, connected, setSelectedAgent } = useSimulationStore();
  const { controlRun, loading } = useSimulation();

  useWebSocket({ runId: activeRunId, enabled: !!activeRunId });

  const handleControl = useCallback(
    (action: 'start' | 'pause' | 'resume' | 'stop' | 'step', body?: Record<string, unknown>) => {
      if (activeRunId) controlRun(activeRunId, action, body);
    },
    [activeRunId, controlRun]
  );

  const handleAgentClick = useCallback(
    (_agentId: string) => {
      // In a real app we'd fetch the full agent. For now set a stub.
      setSelectedAgent(null);
    },
    [setSelectedAgent]
  );

  return (
    <div className="space-y-4">
      {/* Connection status */}
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <div className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400' : 'bg-red-400'}`} />
        {connected ? 'Connected' : 'Disconnected'}
        {activeRunId && <span className="ml-2 font-mono text-gray-600">Run: {activeRunId}</span>}
      </div>

      {/* Metrics row */}
      <MetricsPanel />

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Agent map - takes 3 cols */}
        <div className="lg:col-span-3 h-[400px]">
          <AgentMap onAgentClick={handleAgentClick} />
        </div>

        {/* Right sidebar */}
        <div className="space-y-4">
          <SimulationControls
            runId={activeRunId}
            status={state?.status ?? null}
            onControl={handleControl}
            loading={loading}
          />
          <AgentInspector onClose={() => setSelectedAgent(null)} />
        </div>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <WealthChart />
        <StrategyEvolution />
      </div>

      {/* Events log */}
      <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
        <h3 className="text-sm font-semibold text-gray-300 mb-2">Event Log</h3>
        <EventLog />
      </div>
    </div>
  );
}

function EventLog() {
  const events = useSimulationStore((s) => s.events);
  if (events.length === 0) {
    return <p className="text-sm text-gray-500">No events yet</p>;
  }
  return (
    <div className="max-h-48 overflow-y-auto space-y-1">
      {events
        .slice()
        .reverse()
        .map((e, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span className="text-gray-600 font-mono w-14">T{e.tick}</span>
            <span
              className={`px-1.5 py-0.5 rounded text-xs ${
                e.severity === 'warning'
                  ? 'bg-yellow-900/50 text-yellow-400'
                  : e.severity === 'error' || e.severity === 'critical'
                  ? 'bg-red-900/50 text-red-400'
                  : 'bg-gray-800 text-gray-400'
              }`}
            >
              {e.event_type}
            </span>
            <span className="text-gray-500 truncate">{JSON.stringify(e.payload)}</span>
          </div>
        ))}
    </div>
  );
}
