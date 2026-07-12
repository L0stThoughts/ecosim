import { useEffect, useRef, useCallback } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import type { SimulationState, TickEvent } from '../types';

interface UseWebSocketOptions {
  runId: string | null;
  enabled?: boolean;
}

export function useWebSocket({ runId, enabled = true }: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnect = 10;
  const setState = useSimulationStore((s) => s.setState);
  const addEvent = useSimulationStore((s) => s.addEvent);
  const setConnected = useSimulationStore((s) => s.setConnected);

  const connect = useCallback(() => {
    if (!runId || !enabled) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(`ws://localhost:8080/ws/simulations/${runId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      reconnectAttempts.current = 0;
    };

    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        if (msg.type === 'state.tick' && msg.payload) {
          const st: SimulationState = {
            run_id: msg.run_id || runId,
            tick: msg.tick ?? msg.payload.tick ?? 0,
            generation: msg.payload.generation ?? 0,
            status: msg.payload.status ?? 'running',
            agents_summary: msg.payload.agents_summary ?? {
              alive_count: 0,
              dead_count: 0,
              archetype_counts: { rational: 0, greedy: 0, cooperative: 0, random: 0, adaptive: 0 },
              top_wealth_agents: [],
              average_resources: {},
            },
            environment_state: msg.payload.environment_state ?? {
              active_shocks: [],
              scarcity_flags: {},
              seasonal_modifier: 1,
            },
            metrics: {
              gini: msg.payload.metrics?.gini ?? 0,
              total_wealth: msg.payload.metrics?.total_wealth ?? 0,
              average_wealth: msg.payload.metrics?.average_wealth ?? 0,
              median_wealth: msg.payload.metrics?.median_wealth ?? 0,
              total_trade_volume: msg.payload.metrics?.total_trade_volume ?? 0,
              cooperation_rate: msg.payload.metrics?.cooperation_rate ?? 0,
              reproduction_count: msg.payload.metrics?.reproduction_count ?? 0,
              death_count: msg.payload.metrics?.death_count ?? 0,
              resource_utilization: msg.payload.metrics?.resource_utilization ?? 0,
            },
            recent_events: msg.payload.recent_events ?? [],
            performance: msg.payload.performance ?? {},
          };
          setState(st);
        } else if (msg.type === 'event' && msg.payload) {
          const ev: TickEvent = {
            run_id: msg.run_id || runId,
            tick: msg.tick ?? 0,
            event_type: msg.payload.event_type ?? 'unknown',
            severity: msg.payload.severity ?? 'info',
            payload: msg.payload.details ?? msg.payload,
          };
          addEvent(ev);
        }
      } catch {
        // ignore malformed messages
      }
    };

    ws.onclose = () => {
      setConnected(false);
      if (reconnectAttempts.current < maxReconnect && enabled) {
        const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 30000);
        reconnectAttempts.current++;
        reconnectTimer.current = setTimeout(connect, delay);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [runId, enabled, setState, addEvent, setConnected]);

  const disconnect = useCallback(() => {
    if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
  }, [setConnected]);

  useEffect(() => {
    connect();
    return disconnect;
  }, [connect, disconnect]);

  return { disconnect, reconnect: connect };
}
