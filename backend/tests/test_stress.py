"""Stress test: 10,000 agents, 50 ticks, performance measurement."""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
import tracemalloc
import asyncio
import pytest
import numpy as np

from models.schemas import SimulationConfig
from simulation.engine import SimulationEngine


class TestStress:
    @pytest.mark.asyncio
    async def test_10k_agents_50_ticks(self):
        tracemalloc.start()
        cfg = SimulationConfig(num_agents=5000, max_ticks=1000, seed=42, zone_count=8)
        
        t0 = time.monotonic()
        engine = SimulationEngine(config=cfg)
        init_time = time.monotonic() - t0
        print(f"\n[STRESS] Init time (5k agents): {init_time:.2f}s")
        
        tick_times = []
        for i in range(50):
            t1 = time.monotonic()
            await engine.step(1)
            tick_times.append(time.monotonic() - t1)
        
        total_time = time.monotonic() - t0
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        avg_tick = np.mean(tick_times)
        max_tick = np.max(tick_times)
        min_tick = np.min(tick_times)
        
        print(f"[STRESS] Total time: {total_time:.2f}s")
        print(f"[STRESS] Avg tick: {avg_tick:.3f}s | Min: {min_tick:.3f}s | Max: {max_tick:.3f}s")
        print(f"[STRESS] Memory: current={current/1024/1024:.1f}MB, peak={peak/1024/1024:.1f}MB")
        print(f"[STRESS] Alive agents at end: {len(engine.alive_agents)}/{len(engine.agents)}")
        
        # Assertions
        assert max_tick < 5.0, f"Max tick time {max_tick:.2f}s exceeds 5s limit"
        assert engine.tick == 50
        assert total_time < 300, f"Total time {total_time:.2f}s exceeds 5 min limit"
        
        # Store results for report
        TestStress._results = {
            "init_time": init_time,
            "total_time": total_time,
            "avg_tick": avg_tick,
            "min_tick": min_tick,
            "max_tick": max_tick,
            "memory_current_mb": current / 1024 / 1024,
            "memory_peak_mb": peak / 1024 / 1024,
            "alive_agents": len(engine.alive_agents),
            "total_agents": len(engine.agents),
        }
