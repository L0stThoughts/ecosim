import { useRef, useEffect, useCallback } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { ARCHETYPE_COLORS } from '../types';
import type { Archetype } from '../types';

interface AgentDot {
  id: string;
  x: number;
  y: number;
  archetype: Archetype;
  wealth: number;
  alive: boolean;
}

interface AgentMapProps {
  onAgentClick?: (agentId: string) => void;
}

// Deterministic position from agent id hash
function hashPos(id: string, max: number): number {
  let h = 0;
  for (let i = 0; i < id.length; i++) {
    h = ((h << 5) - h + id.charCodeAt(i)) | 0;
  }
  return Math.abs(h) % max;
}

export default function AgentMap({ onAgentClick }: AgentMapProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const agentsRef = useRef<AgentDot[]>([]);
  const rafRef = useRef<number>(0);
  const state = useSimulationStore((s) => s.state);

  // Generate agent dots from summary (we don't have full agent list via WS,
  // so we simulate positions from archetype counts)
  useEffect(() => {
    if (!state) return;
    const counts = state.agents_summary.archetype_counts;
    const dots: AgentDot[] = [];
    let idx = 0;
    for (const [arch, count] of Object.entries(counts)) {
      for (let i = 0; i < count; i++) {
        const id = `${arch}_${i}`;
        dots.push({
          id,
          x: hashPos(id + 'x', 10000) / 10000,
          y: hashPos(id + 'y', 10000) / 10000,
          archetype: arch as Archetype,
          wealth: 20 + hashPos(id + 'w', 100),
          alive: true,
        });
        idx++;
      }
    }
    agentsRef.current = dots;
  }, [state]);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    const w = rect.width;
    const h = rect.height;

    // Background
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, w, h);

    // Grid
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 0.5;
    for (let gx = 0; gx < w; gx += 50) {
      ctx.beginPath();
      ctx.moveTo(gx, 0);
      ctx.lineTo(gx, h);
      ctx.stroke();
    }
    for (let gy = 0; gy < h; gy += 50) {
      ctx.beginPath();
      ctx.moveTo(0, gy);
      ctx.lineTo(w, gy);
      ctx.stroke();
    }

    // Agents
    const agents = agentsRef.current;
    for (let i = 0; i < agents.length; i++) {
      const a = agents[i];
      const px = a.x * w;
      const py = a.y * h;
      const radius = Math.max(1.5, Math.min(6, a.wealth / 30));
      ctx.beginPath();
      ctx.arc(px, py, radius, 0, Math.PI * 2);
      ctx.fillStyle = ARCHETYPE_COLORS[a.archetype] || '#6b7280';
      ctx.globalAlpha = 0.8;
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    // Legend
    const archetypes: Archetype[] = ['rational', 'greedy', 'cooperative', 'random', 'adaptive'];
    ctx.font = '11px Inter, system-ui, sans-serif';
    let ly = 16;
    for (const arch of archetypes) {
      ctx.fillStyle = ARCHETYPE_COLORS[arch];
      ctx.beginPath();
      ctx.arc(12, ly - 3, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#e2e8f0';
      ctx.fillText(arch, 22, ly);
      ly += 18;
    }
  }, []);

  useEffect(() => {
    draw();
  }, [state, draw]);

  // Handle resize
  useEffect(() => {
    const obs = new ResizeObserver(() => draw());
    if (canvasRef.current) obs.observe(canvasRef.current);
    return () => obs.disconnect();
  }, [draw]);

  const handleClick = useCallback(
    (e: React.MouseEvent<HTMLCanvasElement>) => {
      if (!onAgentClick || !canvasRef.current) return;
      const rect = canvasRef.current.getBoundingClientRect();
      const mx = (e.clientX - rect.left) / rect.width;
      const my = (e.clientY - rect.top) / rect.height;

      let closest: AgentDot | null = null;
      let minDist = 0.02;
      for (const a of agentsRef.current) {
        const dx = a.x - mx;
        const dy = a.y - my;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < minDist) {
          minDist = d;
          closest = a;
        }
      }
      if (closest) onAgentClick(closest.id);
    },
    [onAgentClick]
  );

  return (
    <div className="relative w-full h-full min-h-[300px] rounded-lg overflow-hidden border border-gray-800">
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-crosshair"
        onClick={handleClick}
      />
      {!state && (
        <div className="absolute inset-0 flex items-center justify-center text-gray-500">
          No simulation data
        </div>
      )}
    </div>
  );
}
