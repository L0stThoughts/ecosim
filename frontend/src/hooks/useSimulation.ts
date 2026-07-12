import { useCallback, useState } from 'react';
import client from '../api/client';
import { useSimulationStore } from '../store/simulationStore';
import type { Run, SimulationConfig, Agent } from '../types';

export function useSimulation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setRuns, setActiveRunId, setSelectedAgent } = useSimulationStore();

  const wrap = useCallback(async <T>(fn: () => Promise<T>): Promise<T | null> => {
    setLoading(true);
    setError(null);
    try {
      const result = await fn();
      return result;
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchRuns = useCallback(async () => {
    const res = await wrap(async () => {
      const r = await client.get<{ data: Run[] }>('/api/v1/runs');
      return r.data.data;
    });
    if (res) setRuns(res);
    return res;
  }, [wrap, setRuns]);

  const createRun = useCallback(
    async (config: SimulationConfig) => {
      const res = await wrap(async () => {
        const r = await client.post<{ data: Run }>('/api/v1/runs', { config });
        return r.data.data;
      });
      if (res) {
        setActiveRunId(res.run_id);
        await fetchRuns();
      }
      return res;
    },
    [wrap, setActiveRunId, fetchRuns]
  );

  const controlRun = useCallback(
    async (runId: string, action: 'start' | 'pause' | 'resume' | 'stop' | 'step', body?: Record<string, unknown>) => {
      return wrap(async () => {
        const r = await client.post(`/api/v1/runs/${runId}/${action}`, body ?? {});
        return r.data.data;
      });
    },
    [wrap]
  );

  const fetchAgent = useCallback(
    async (runId: string, agentId: string) => {
      const res = await wrap(async () => {
        const r = await client.get<{ data: Agent }>(`/api/v1/runs/${runId}/agents/${agentId}`);
        return r.data.data;
      });
      if (res) setSelectedAgent(res);
      return res;
    },
    [wrap, setSelectedAgent]
  );

  return { loading, error, fetchRuns, createRun, controlRun, fetchAgent };
}
