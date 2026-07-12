import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { useSimulationStore } from '../store/simulationStore';
import { ARCHETYPE_COLORS } from '../types';

export default function StrategyEvolution() {
  const history = useSimulationStore((s) => s.strategyHistory);
  const sampled = history.length > 200 ? history.filter((_, i) => i % Math.ceil(history.length / 200) === 0) : history;

  return (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
      <h3 className="text-sm font-semibold text-gray-300 mb-3">Strategy Evolution</h3>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={sampled}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="tick" tick={{ fill: '#9ca3af', fontSize: 11 }} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} domain={[0, 1]} tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`} />
          <Tooltip
            contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8 }}
            formatter={(value: number) => `${(value * 100).toFixed(1)}%`}
          />
          <Area type="monotone" dataKey="cooperative" stackId="1" fill={ARCHETYPE_COLORS.cooperative} stroke={ARCHETYPE_COLORS.cooperative} />
          <Area type="monotone" dataKey="rational" stackId="1" fill={ARCHETYPE_COLORS.rational} stroke={ARCHETYPE_COLORS.rational} />
          <Area type="monotone" dataKey="adaptive" stackId="1" fill={ARCHETYPE_COLORS.adaptive} stroke={ARCHETYPE_COLORS.adaptive} />
          <Area type="monotone" dataKey="random" stackId="1" fill={ARCHETYPE_COLORS.random} stroke={ARCHETYPE_COLORS.random} />
          <Area type="monotone" dataKey="greedy" stackId="1" fill={ARCHETYPE_COLORS.greedy} stroke={ARCHETYPE_COLORS.greedy} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
