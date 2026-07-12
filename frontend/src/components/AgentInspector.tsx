import { useSimulationStore } from '../store/simulationStore';
import { ARCHETYPE_COLORS } from '../types';
import type { Agent } from '../types';

interface AgentInspectorProps {
  onClose: () => void;
}

export default function AgentInspector({ onClose }: AgentInspectorProps) {
  const agent = useSimulationStore((s) => s.selectedAgent);

  if (!agent) {
    return (
      <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-sm font-semibold text-gray-300">Agent Inspector</h3>
        </div>
        <p className="text-sm text-gray-500">Click an agent on the map to inspect</p>
      </div>
    );
  }

  const genes = Object.entries(agent.strategy_genes);
  const resources = Object.entries(agent.resources);

  return (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-800 space-y-3">
      <div className="flex justify-between items-center">
        <h3 className="text-sm font-semibold text-gray-300">Agent Inspector</h3>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-300 text-xs">✕ Close</button>
      </div>

      <div className="flex items-center gap-2">
        <div
          className="w-3 h-3 rounded-full"
          style={{ backgroundColor: ARCHETYPE_COLORS[agent.archetype] }}
        />
        <span className="text-sm font-mono text-gray-200">{agent.id}</span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-800 text-gray-400 capitalize">
          {agent.archetype}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2 text-xs">
        <div className="bg-gray-800 p-2 rounded">
          <div className="text-gray-500">Wealth</div>
          <div className="font-bold text-gray-200">{agent.wealth.toFixed(1)}</div>
        </div>
        <div className="bg-gray-800 p-2 rounded">
          <div className="text-gray-500">Age</div>
          <div className="font-bold text-gray-200">{agent.age}</div>
        </div>
        <div className="bg-gray-800 p-2 rounded">
          <div className="text-gray-500">Generation</div>
          <div className="font-bold text-gray-200">{agent.generation}</div>
        </div>
        <div className="bg-gray-800 p-2 rounded">
          <div className="text-gray-500">Fitness</div>
          <div className="font-bold text-gray-200">{agent.fitness.toFixed(2)}</div>
        </div>
        <div className="bg-gray-800 p-2 rounded">
          <div className="text-gray-500">Energy</div>
          <div className="font-bold text-gray-200">{agent.energy.toFixed(0)}</div>
        </div>
        <div className="bg-gray-800 p-2 rounded">
          <div className="text-gray-500">Health</div>
          <div className="font-bold text-gray-200">{agent.health.toFixed(0)}</div>
        </div>
      </div>

      {genes.length > 0 && (
        <div>
          <div className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Strategy Genes</div>
          <div className="space-y-1">
            {genes.map(([k, v]) => (
              <div key={k} className="flex items-center gap-2">
                <span className="text-xs text-gray-400 w-28 truncate">{k}</span>
                <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: `${(v * 100).toFixed(0)}%` }}
                  />
                </div>
                <span className="text-xs text-gray-400 w-10 text-right">{v.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {resources.length > 0 && (
        <div>
          <div className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Resources</div>
          <div className="grid grid-cols-2 gap-1">
            {resources.map(([k, v]) => (
              <div key={k} className="flex justify-between text-xs bg-gray-800 px-2 py-1 rounded">
                <span className="text-gray-400 capitalize">{k}</span>
                <span className="text-gray-200 font-mono">{v.toFixed(1)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {agent.alliances.length > 0 && (
        <div>
          <div className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Alliances</div>
          <div className="flex flex-wrap gap-1">
            {agent.alliances.map((a) => (
              <span key={a} className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-mono">
                {a}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
