// Frontend types matching backend Pydantic models

export type Archetype = 'rational' | 'greedy' | 'cooperative' | 'random' | 'adaptive';

export type RunStatus = 'created' | 'running' | 'paused' | 'stopped' | 'completed';

export interface ResourceParams {
  resource_types: string[];
  initial_distribution: Record<string, number>;
  regeneration_rate: Record<string, number>;
  scarcity_thresholds: Record<string, number>;
}

export interface EvolutionParams {
  enabled: boolean;
  generation_length: number;
  mutation_rate: number;
  mutation_strength: number;
  crossover_rate: number;
  elitism_ratio: number;
  selection_ratio: number;
}

export interface SimulationConfig {
  num_agents: number;
  tick_rate: number;
  max_ticks: number;
  seed: number | null;
  snapshot_interval_ticks: number;
  metrics_interval_ticks: number;
  resource_params: ResourceParams;
  evolution_params: EvolutionParams;
  archetype_distribution: Record<Archetype, number>;
  shock_probability: number;
  zone_count: number;
  scenario_name: string | null;
}

export interface Agent {
  id: string;
  archetype: Archetype;
  strategy_genes: Record<string, number>;
  resources: Record<string, number>;
  wealth: number;
  energy: number;
  health: number;
  age: number;
  generation: number;
  location: string;
  alliances: string[];
  memory: Record<string, unknown>[];
  fitness: number;
  alive: boolean;
}

export interface AgentSummary {
  alive_count: number;
  dead_count: number;
  archetype_counts: Record<Archetype, number>;
  top_wealth_agents: { id: string; archetype: Archetype; wealth: number }[];
  average_resources: Record<string, number>;
}

export interface EnvironmentState {
  active_shocks: { shock_type: string; magnitude: number; zones: string[] }[];
  scarcity_flags: Record<string, boolean>;
  seasonal_modifier: number;
}

export interface SimulationMetrics {
  gini: number;
  total_wealth: number;
  average_wealth: number;
  median_wealth: number;
  total_trade_volume: number;
  cooperation_rate: number;
  reproduction_count: number;
  death_count: number;
  resource_utilization: number;
}

export interface SimulationState {
  run_id: string;
  tick: number;
  generation: number;
  status: RunStatus;
  agents_summary: AgentSummary;
  environment_state: EnvironmentState;
  metrics: SimulationMetrics;
  recent_events: TickEvent[];
  performance: Record<string, number>;
}

export interface TickEvent {
  run_id: string;
  tick: number;
  event_type: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  payload: Record<string, unknown>;
}

export interface Run {
  run_id: string;
  status: RunStatus;
  config: SimulationConfig;
  created_at: string;
  start_time: string | null;
  end_time: string | null;
  total_ticks: number;
  generations: number;
  final_metrics: Partial<SimulationMetrics>;
}

export interface MetricSeries {
  [metricName: string]: { tick: number; value: number }[];
}

export interface RunComparison {
  runs: string[];
  comparison: Record<string, Record<string, number>>;
}

export interface WebSocketMessage {
  type: string;
  run_id?: string;
  tick?: number;
  timestamp: string;
  payload: Record<string, unknown>;
}

export interface StrategyDataPoint {
  tick: number;
  rational: number;
  greedy: number;
  cooperative: number;
  random: number;
  adaptive: number;
}

export interface WealthDataPoint {
  range: string;
  count: number;
}

export const ARCHETYPE_COLORS: Record<Archetype, string> = {
  rational: '#3b82f6',
  greedy: '#ef4444',
  cooperative: '#22c55e',
  random: '#a855f7',
  adaptive: '#f59e0b',
};

export const DEFAULT_CONFIG: SimulationConfig = {
  num_agents: 1000,
  tick_rate: 10,
  max_ticks: 5000,
  seed: null,
  snapshot_interval_ticks: 25,
  metrics_interval_ticks: 1,
  resource_params: {
    resource_types: ['food', 'energy', 'material', 'currency'],
    initial_distribution: { food: 10000, energy: 8000, material: 6000, currency: 15000 },
    regeneration_rate: { food: 0.05, energy: 0.03, material: 0.02, currency: 0.0 },
    scarcity_thresholds: { food: 1000, energy: 800, material: 500, currency: 0 },
  },
  evolution_params: {
    enabled: true,
    generation_length: 100,
    mutation_rate: 0.05,
    mutation_strength: 0.1,
    crossover_rate: 0.5,
    elitism_ratio: 0.05,
    selection_ratio: 0.2,
  },
  archetype_distribution: { rational: 0.2, greedy: 0.2, cooperative: 0.2, random: 0.2, adaptive: 0.2 },
  shock_probability: 0.01,
  zone_count: 4,
  scenario_name: null,
};
