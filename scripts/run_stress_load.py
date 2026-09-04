#!/usr/bin/env python3
##################################################
# scripts/run_stress_load.py
# High-Performance Async Load Generator for Sharegy
##################################################

import argparse
import asyncio
import json
import math
import os
import random
import sys
import time
from datetime import datetime
from typing import List, Dict, Any

try:
    import aiohttp
except ImportError:
    print("Error: aiohttp is required. Install with: pip install aiohttp")
    sys.exit(1)


class StressMetrics:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.total_requests = 0
        self.success_requests = 0
        self.error_requests = 0
        self.status_codes: Dict[int, int] = {}
        self.latencies: List[float] = []
        self.ingest_requests = 0
        self.dashboard_requests = 0
        self.start_time = time.time()

    async def record(self, status: int, latency_ms: float, req_type: str = "query"):
        async with self.lock:
            self.total_requests += 1
            if 200 <= status < 300:
                self.success_requests += 1
            else:
                self.error_requests += 1

            self.status_codes[status] = self.status_codes.get(status, 0) + 1
            self.latencies.append(latency_ms)

            if req_type == "ingest":
                self.ingest_requests += 1
            else:
                self.dashboard_requests += 1

    def get_summary(self) -> Dict[str, Any]:
        duration = max(time.time() - self.start_time, 0.001)
        lat = sorted(self.latencies) if self.latencies else [0.0]
        count = len(lat)

        def percentile(p: float) -> float:
            if not lat:
                return 0.0
            idx = int(math.ceil((p / 100.0) * count)) - 1
            return lat[max(0, min(idx, count - 1))]

        rps = self.total_requests / duration

        return {
            "duration_s": round(duration, 2),
            "total_requests": self.total_requests,
            "success_requests": self.success_requests,
            "error_requests": self.error_requests,
            "error_rate_pct": round((self.error_requests / max(self.total_requests, 1)) * 100, 2),
            "rps": round(rps, 2),
            "ingest_count": self.ingest_requests,
            "dashboard_count": self.dashboard_requests,
            "latency_min_ms": round(min(lat), 2) if lat else 0.0,
            "latency_p50_ms": round(percentile(50), 2),
            "latency_p90_ms": round(percentile(90), 2),
            "latency_p95_ms": round(percentile(95), 2),
            "latency_p99_ms": round(percentile(99), 2),
            "latency_max_ms": round(max(lat), 2) if lat else 0.0,
            "status_codes": dict(self.status_codes),
        }


def generate_device_telemetry(device: Dict[str, Any]) -> Dict[str, Any]:
    role = device.get("role", "consumer")
    base_w = float(device.get("base_power", 50.0))

    if role == "producer":
        # PV: fluctuating generation with sunlight noise
        fluctuation = random.uniform(0.7, 1.2)
        power_w = round(max(0.0, base_w * fluctuation), 1)
    elif role == "storage":
        # Battery: charging (-W) or discharging (+W)
        power_w = round(base_w + random.uniform(-100.0, 100.0), 1)
    elif role == "grid":
        # Grid meter: net exchange
        power_w = round(base_w + random.uniform(-50.0, 50.0), 1)
    else:
        # Consumer: active or idle
        if random.random() < 0.2:
            power_w = 0.0
        else:
            power_w = round(max(0.0, base_w * random.uniform(0.8, 1.3)), 1)

    return {
        "identifier": device["identifier"],
        "name": device.get("name", device["identifier"]),
        "power_w": power_w,
        "role": role,
    }


async def user_worker(
    user_data: Dict[str, Any],
    base_url: str,
    session: aiohttp.ClientSession,
    metrics: StressMetrics,
    stop_event: asyncio.Event,
    ingest_interval_s: float,
    query_interval_s: float,
    sem: asyncio.Semaphore,
):
    token = user_data["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Host": "sharegy.de",
    }
    devices = user_data.get("devices", [])

    async def run_telemetry_loop():
        while not stop_event.is_set():
            if devices:
                payload_devices = [generate_device_telemetry(d) for d in devices]
                payload = {"devices": payload_devices}
                url = f"{base_url}/api/devices/telemetry/push/"

                t0 = time.time()
                async with sem:
                    try:
                        async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=10.0)) as resp:
                            lat_ms = (time.time() - t0) * 1000.0
                            await metrics.record(resp.status, lat_ms, "ingest")
                    except asyncio.TimeoutError:
                        lat_ms = (time.time() - t0) * 1000.0
                        await metrics.record(408, lat_ms, "ingest")
                    except Exception:
                        lat_ms = (time.time() - t0) * 1000.0
                        await metrics.record(599, lat_ms, "ingest")

            await asyncio.sleep(ingest_interval_s + random.uniform(-0.2, 0.2))

    async def run_query_loop():
        endpoints = [
            "/api/energy/dashboard/me/",
            "/api/devices/",
            "/api/devices/status/",
        ]
        while not stop_event.is_set():
            endpoint = random.choice(endpoints)
            url = f"{base_url}{endpoint}"

            t0 = time.time()
            async with sem:
                try:
                    async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10.0)) as resp:
                        lat_ms = (time.time() - t0) * 1000.0
                        await metrics.record(resp.status, lat_ms, "query")
                except asyncio.TimeoutError:
                    lat_ms = (time.time() - t0) * 1000.0
                    await metrics.record(408, lat_ms, "query")
                except Exception:
                    lat_ms = (time.time() - t0) * 1000.0
                    await metrics.record(599, lat_ms, "query")

            await asyncio.sleep(query_interval_s + random.uniform(-0.3, 0.3))

    await asyncio.gather(run_telemetry_loop(), run_query_loop())


async def monitor_loop(metrics: StressMetrics, stop_event: asyncio.Event, interval_s: float = 2.0):
    print(f"{'Time':<8} | {'Reqs':<8} | {'RPS':<8} | {'Succ%':<7} | {'p50(ms)':<9} | {'p95(ms)':<9} | {'p99(ms)':<9} | {'Codes'}")
    print("-" * 75)
    last_reqs = 0
    last_t = time.time()

    while not stop_event.is_set():
        await asyncio.sleep(interval_s)
        now_t = time.time()
        elapsed = now_t - last_t
        curr_reqs = metrics.total_requests
        delta_reqs = curr_reqs - last_reqs
        inst_rps = delta_reqs / max(elapsed, 0.001)

        summary = metrics.get_summary()
        succ_rate = 100.0 - summary["error_rate_pct"]
        codes_str = " ".join(f"{k}:{v}" for k, v in summary["status_codes"].items())

        time_str = f"{int(summary['duration_s'])}s"
        print(
            f"{time_str:<8} | {curr_reqs:<8} | {inst_rps:<8.1f} | {succ_rate:<6.1f}% | "
            f"{summary['latency_p50_ms']:<9.1f} | {summary['latency_p95_ms']:<9.1f} | "
            f"{summary['latency_p99_ms']:<9.1f} | {codes_str}"
        )

        last_reqs = curr_reqs
        last_t = now_t


async def main():
    parser = argparse.ArgumentParser(description="Async Stress Test Load Generator for Sharegy")
    parser.add_argument("--tokens-file", type=str, default="stress_test_tokens.json", help="Path to tokens JSON file")
    parser.add_argument("--base-url", type=str, default="https://sharegy.de", help="Target base URL")
    parser.add_argument("--users-limit", type=int, default=200, help="Limit number of concurrent users from token file")
    parser.add_argument("--duration", type=int, default=30, help="Test duration in seconds (default: 30)")
    parser.add_argument("--concurrency", type=int, default=100, help="Max concurrent HTTP requests (semaphore)")
    parser.add_argument("--ingest-interval", type=float, default=2.0, help="Interval (seconds) between device telemetry pushes per user")
    parser.add_argument("--query-interval", type=float, default=3.0, help="Interval (seconds) between dashboard queries per user")
    parser.add_argument("--stage-name", type=str, default="Stress Test Stage", help="Name of this test stage")
    args = parser.parse_args()

    if not os.path.isfile(args.tokens_file):
        print(f"Error: Tokens file '{args.tokens_file}' not found.")
        print("Please run: python manage.py seed_stress_test --users=... first.")
        sys.exit(1)

    with open(args.tokens_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_users = data.get("users", [])
    active_users = all_users[:args.users_limit]
    total_active_devices = sum(len(u.get("devices", [])) for u in active_users)

    print("=" * 75)
    print(f"⚡ {args.stage_name.upper()}")
    print(f"   Target URL:             {args.base_url}")
    print(f"   Simulated Users:        {len(active_users)}")
    print(f"   Simulated Devices:      {total_active_devices}")
    print(f"   Max HTTP Concurrency:   {args.concurrency}")
    print(f"   Test Duration:          {args.duration}s")
    print(f"   Ingest Interval/User:   {args.ingest_interval}s")
    print(f"   Query Interval/User:    {args.query_interval}s")
    print("=" * 75)

    metrics = StressMetrics()
    stop_event = asyncio.Event()
    sem = asyncio.Semaphore(args.concurrency)

    connector = aiohttp.TCPConnector(limit=args.concurrency * 2, limit_per_host=args.concurrency * 2, ttl_dns_cache=300)

    async with aiohttp.ClientSession(connector=connector) as session:
        # Launch monitor loop
        monitor_task = asyncio.create_task(monitor_loop(metrics, stop_event))

        # Launch user worker tasks
        user_tasks = [
            asyncio.create_task(
                user_worker(
                    user_data=u,
                    base_url=args.base_url.rstrip("/"),
                    session=session,
                    metrics=metrics,
                    stop_event=stop_event,
                    ingest_interval_s=args.ingest_interval,
                    query_interval_s=args.query_interval,
                    sem=sem,
                )
            )
            for u in active_users
        ]

        # Run for specified duration
        await asyncio.sleep(args.duration)
        stop_event.set()

        # Await completion
        await asyncio.gather(*user_tasks, return_exceptions=True)
        await monitor_task

    # Print final summary report
    summary = metrics.get_summary()
    print("=" * 75)
    print("📊 FINAL BENCHMARK SUMMARY")
    print("=" * 75)
    print(f"  Duration:            {summary['duration_s']} s")
    print(f"  Total Requests:      {summary['total_requests']}")
    print(f"  Throughput (RPS):    {summary['rps']} req/s")
    print(f"  Successful (2xx):    {summary['success_requests']} ({100.0 - summary['error_rate_pct']}%)")
    print(f"  Errors / Timeouts:   {summary['error_requests']} ({summary['error_rate_pct']}%)")
    print(f"  Telemetry Ingests:   {summary['ingest_count']}")
    print(f"  Dashboard Queries:   {summary['dashboard_count']}")
    print(f"  Latency Min:         {summary['latency_min_ms']} ms")
    print(f"  Latency Median(p50): {summary['latency_p50_ms']} ms")
    print(f"  Latency p90:         {summary['latency_p90_ms']} ms")
    print(f"  Latency p95:         {summary['latency_p95_ms']} ms")
    print(f"  Latency p99:         {summary['latency_p99_ms']} ms")
    print(f"  Latency Max:         {summary['latency_max_ms']} ms")
    print(f"  Status Codes:        {summary['status_codes']}")
    print("=" * 75)

    # Dump stage summary JSON
    out_file = f"stress_result_{len(active_users)}u_{total_active_devices}d.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"💾 Result saved to {out_file}\n")


if __name__ == "__main__":
    asyncio.run(main())
