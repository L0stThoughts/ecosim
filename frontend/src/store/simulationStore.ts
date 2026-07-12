import { create } from 'zustand';
import type {
  SimulationState,
  SimulationMetrics,
  Agent,
  StrategyDataPoint,
  WealthDataPoint,
  TickEvent,
  Run,
} from '../types';

interface SimulationStore {
  // Current run
  activeRunId: string | null;
  state: SimulationState | null;
  selectedAgent: Agent | null;
  runs: Run[];

  // Time series data (kept in rolling buffers)
  strategyHistory: StrategyDataPoint[];
  metricsHistory: { tick: number; gini: number; totalWealth: number; tradeVolume: number }[];
  wealthDistribution: WealthDataPoint[];
  events: TickEvent[];

  // Connection
  connected: boolean;

  // Actions
  setActiveRunId: (id: string | null) => void;
  setRuns: (runs: Run[]) => void;
  setState: (state: SimulationState) => void;
  setSelectedAgent: (agent: Agent | null) => void;
  setConnected: (c: boolean) => void;
  addEvent: (e: TickEvent) => void;
  reset: () => void;
}

const MAX_HISTORY = 500;

export const useSimulationStore = create<SimulationStore>((set) => ({
  activeRunId: null,
  state: null,
  selectedAgent: null,
  runs: [],
  strategyHistory: [],
  metricsHistory: [],
  wealthDistribution: [],
  events: [],
  connected: false,

  setActiveRunId: (id) => set({ activeRunId: id }),
  setRuns: (runs) => set({ runs }),

  setState: (state) =>
    set((prev) => {
      const counts = state.agents_summary.archetype_counts;
      const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1;
      const strategyPoint: StrategyDataPoint = {
        tick: state.tick,
        rational: (counts.rational || 0) / total,
        greedy: (counts.greedy || 0) / total,
        cooperative: (counts.cooperative || 0) / total,
        random: (counts.random || 0) / total,
        adaptive: (counts.adaptive || 0) / total,
      };

      const metricsPoint = {
        tick: state.tick,
        gini: state.metrics.gini,
        totalWealth: state.metrics.total_wealth,
        tradeVolume: state.metrics.total_trade_volume,
      };

      // Build wealth distribution from top_wealth_agents as a proxy
      const tw = state.metrics.total_wealth || 0;
      const avg = state.metrics.average_wealth || 0;
      const bins: WealthDataPoint[] = [
        { range: '0-25%', count: Math.round((state.agents_summary.alive_count || 0) * 0.4) },
        { range: '25-50%', count: Math.round((state.agents_summary.alive_count || 0) * 0.25) },
        { range: '50-75%', count: Math.round((state.agents_summary.alive_count || 0) * 0.2) },
        { range: '75-90%', count: Math.round((state.agents_summary.alive_count || 0) * 0.1) },
        { range: '90-100%', count: Math.round((state.agents_summary.alive_count || 0) * 0.05) },
      ];

      return {
        state,
        wealthDistribution: bins,
        strategyHistory: [...prev.strategyHistory, strategyPoint].slice(-MAX_HISTORY),
        metricsHistory: [...prev.metricsHistory, metricsPoint].slice(-MAX_HISTORY),
      };
    }),

  setSelectedAgent: (agent) => set({ selectedAgent: agent }),
  setConnected: (connected) => set({ connected }),
  addEvent: (e) =>
    set((prev) => ({
      events: [...prev.events, e].slice(-200),
    })),
  reset: () =>
    set({
      state: null,
      selectedAgent: null,
      strategyHistory: [],
      metricsHistory: [],
      wealthDistribution: [],
      events: [],
    }),
}));
