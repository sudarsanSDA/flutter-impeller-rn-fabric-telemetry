"""Host-driven automated ADB telemetry harness for cross-platform benchmarks."""

import argparse
import csv
import os
import re
import subprocess
import time
from typing import Dict, List, Optional, Tuple


class BenchmarkTarget:
    """Target configuration for an application under test."""

    def __init__(self, framework: str, package_name: str, activity_name: str):
        self.framework = framework
        self.package_name = package_name
        self.activity_name = activity_name

    @property
    def component(self) -> str:
        """Returns package/activity component identifier."""
        return f"{self.package_name}/{self.activity_name}"


TARGETS: Dict[str, BenchmarkTarget] = {
    "flutter": BenchmarkTarget(
        framework="flutter",
        package_name="com.benchmark.flutter_benchmark",
        activity_name=".MainActivity",
    ),
    "react_native": BenchmarkTarget(
        framework="react_native",
        package_name="com.react_native_benchmark",
        activity_name=".MainActivity",
    ),
}


class AdbRunner:
    """Executes ADB shell commands and queries device telemetry."""

    def __init__(self, device_id: Optional[str] = None):
        if device_id == "poco":
            self.device_id = "59VK7L6HMZFQXK5X"
        elif device_id in ("curtana", "redmi", "old"):
            self.device_id = "6ea7667c"
        else:
            self.device_id = device_id
        self.base_cmd = ["adb"]
        if self.device_id:
            self.base_cmd.extend(["-s", self.device_id])

    def get_device_info(self) -> Tuple[int, int, float]:
        """Returns (width, height, refresh_rate_hz)."""
        try:
            wm = self.shell("wm size")
            w, h = 1080, 2400
            m = re.search(r"Physical size:\s*(\d+)x(\d+)", wm)
            if m:
                w, h = int(m.group(1)), int(m.group(2))
            
            rr = 60.0
            peak = self.shell("settings get system peak_refresh_rate")
            if "120" in peak:
                rr = 120.0
            return w, h, rr
        except Exception:
            return 1080, 2400, 60.0

    def run(self, args: List[str], check: bool = True) -> str:
        """Executes an ADB command and returns standard output."""
        cmd = self.base_cmd + args
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=check,
        )
        return result.stdout.strip()

    def shell(self, command: str, check: bool = True) -> str:
        """Executes a shell command via ADB shell."""
        return self.run(["shell", command], check=check)

    def force_stop(self, package_name: str) -> None:
        """Force stops the specified package."""
        self.shell(f"am force-stop {package_name}")

    def start_cold(self, component: str) -> str:
        """Launches component with -W flag to capture startup timing."""
        return self.shell(f"am start -W -n {component}")

    def reset_gfxinfo(self, package_name: str) -> None:
        """Resets gfxinfo telemetry frame buffers."""
        self.shell(f"dumpsys gfxinfo {package_name} reset")

    def get_gfxinfo_framestats(self, package_name: str) -> str:
        """Extracts gfxinfo framestats raw data."""
        return self.shell(f"dumpsys gfxinfo {package_name} framestats")

    def get_meminfo(self, package_name: str) -> str:
        """Extracts process memory consumption statistics."""
        return self.shell(f"dumpsys meminfo {package_name}")

    def reset_surfaceflinger(self, layer: str) -> None:
        """Clears SurfaceFlinger latency buffer for specified layer."""
        escaped = layer.replace("(", r"\(").replace(")", r"\)")
        self.shell(f"dumpsys SurfaceFlinger --latency-clear {escaped}")

    def get_surfaceflinger_latency(self, layer: str) -> str:
        """Extracts SurfaceFlinger frame presentation timestamps."""
        escaped = layer.replace("(", r"\(").replace(")", r"\)")
        return self.shell(f"dumpsys SurfaceFlinger --latency {escaped}")

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int) -> None:
        """Issues programmatic touch swipe gesture."""
        self.shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")

    def tap(self, x: int, y: int) -> None:
        """Issues programmatic touch tap."""
        self.shell(f"input tap {x} {y}")


class TelemetryExtractor:
    """Parses raw ADB telemetry logs into structured metric data."""

    @staticmethod
    def parse_startup_total_time(output: str) -> Optional[int]:
        """Parses TotalTime in milliseconds from am start -W output."""
        match = re.search(r"TotalTime:\s*(\d+)", output)
        if match:
            return int(match.group(1))
        # Fallback to WaitTime if TotalTime is absent
        fallback = re.search(r"WaitTime:\s*(\d+)", output)
        if fallback:
            return int(fallback.group(1))
        return None

    @staticmethod
    def parse_meminfo(output: str) -> Dict[str, int]:
        """Extracts Native Heap PSS, Dalvik Heap PSS, and TOTAL PSS from meminfo output."""
        metrics: Dict[str, int] = {
            "native_heap_pss": 0,
            "dalvik_heap_pss": 0,
            "total_pss": 0,
        }

        # Pattern for standard Android meminfo summary table
        native_match = re.search(r"Native Heap\s+(\d+)", output, re.IGNORECASE)
        if native_match:
            metrics["native_heap_pss"] = int(native_match.group(1))

        dalvik_match = re.search(r"Dalvik Heap\s+(\d+)", output, re.IGNORECASE)
        if dalvik_match:
            metrics["dalvik_heap_pss"] = int(dalvik_match.group(1))

        total_match = re.search(r"TOTAL PSS:\s+(\d+)", output)
        if not total_match:
            total_match = re.search(r"TOTAL\s+(\d+)", output)
        if total_match:
            metrics["total_pss"] = int(total_match.group(1))

        return metrics

    @staticmethod
    def parse_framestats(output: str, jank_threshold: float = 16.666) -> Tuple[int, int, float]:
        """Parses framestats data and computes total frames, janky frames (>threshold), and p95 frametime."""
        durations_ms = TelemetryExtractor.extract_frame_durations(output)

        if not durations_ms:
            # Fallback to summary statistics if framestats table empty
            total_frames_match = re.search(r"Total frames rendered:\s*(\d+)", output)
            janky_frames_match = re.search(r"Janky frames:\s*(\d+)", output)
            p95_match = re.search(r"95th percentile:\s*(\d+)ms", output)

            total_frames = int(total_frames_match.group(1)) if total_frames_match else 0
            janky_frames = int(janky_frames_match.group(1)) if janky_frames_match else 0
            p95_frametime = float(p95_match.group(1)) if p95_match else 0.0
            return total_frames, janky_frames, p95_frametime

        total_frames = len(durations_ms)
        janky_frames = sum(1 for d in durations_ms if d > jank_threshold)
        sorted_durations = sorted(durations_ms)
        p95_index = int(0.95 * total_frames)
        p95_frametime = sorted_durations[min(p95_index, total_frames - 1)]

        return total_frames, janky_frames, round(p95_frametime, 2)

    @staticmethod
    def extract_frame_durations(output: str) -> List[float]:
        """Extracts individual frame durations in milliseconds from framestats with dynamic column indices."""
        durations_ms: List[float] = []
        in_profile_data = False
        header_map: Optional[Dict[str, int]] = None

        for line in output.splitlines():
            line = line.strip()
            if line.startswith("---PROFILEDATA---"):
                in_profile_data = not in_profile_data
                header_map = None
                continue

            if not in_profile_data or not line:
                continue

            parts = line.split(",")
            if header_map is None and "IntendedVsync" in line:
                header_map = {name.strip(): idx for idx, name in enumerate(parts) if name.strip()}
                continue

            if header_map and "IntendedVsync" in header_map and "FrameCompleted" in header_map:
                try:
                    iv_idx = header_map["IntendedVsync"]
                    fc_idx = header_map["FrameCompleted"]
                    intended_vsync = int(parts[iv_idx])
                    frame_completed = int(parts[fc_idx])
                    if intended_vsync > 0 and frame_completed > 0:
                        duration_ms = (frame_completed - intended_vsync) / 1_000_000.0
                        if 0 < duration_ms < 500:
                            durations_ms.append(round(duration_ms, 2))
                except (ValueError, IndexError):
                    continue

        return durations_ms

    @staticmethod
    def parse_surfaceflinger_latency(output: str) -> List[float]:
        """Extracts hardware present frame durations from dumpsys SurfaceFlinger --latency output."""
        durations_ms: List[float] = []
        prev_present: int = 0

        for line in output.splitlines():
            parts = line.strip().split()
            if len(parts) == 3:
                try:
                    desired, actual, ready = int(parts[0]), int(parts[1]), int(parts[2])
                    # Ignore invalid or pending frames (actual == 0 or INT64_MAX)
                    if 0 < actual < 9223372036854775800:
                        if prev_present > 0:
                            interval_ms = (actual - prev_present) / 1_000_000.0
                            if 0 < interval_ms < 500:
                                durations_ms.append(round(interval_ms, 2))
                        prev_present = actual
                except (ValueError, IndexError):
                    continue

        return durations_ms


class MetricRecord:
    """Container representing a standardized benchmark telemetry observation."""

    def __init__(
        self,
        framework: str,
        test_name: str,
        iteration: int,
        metric_name: str,
        metric_value: float,
        unit: str,
    ):
        self.framework = framework
        self.test_name = test_name
        self.iteration = iteration
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.unit = unit

    def to_row(self) -> List[str]:
        """Converts metric record to a CSV row."""
        return [
            self.framework,
            self.test_name,
            str(self.iteration),
            self.metric_name,
            str(self.metric_value),
            self.unit,
        ]


class BenchmarkSuite:
    """Orchestrates test execution and records results."""

    def __init__(self, adb: AdbRunner, output_file: str):
        self.adb = adb
        self.output_file = output_file
        self.records: List[MetricRecord] = []
        self.frame_latencies: List[Tuple[str, str, float]] = []

    def run_cold_startup(self, target: BenchmarkTarget, iterations: int = 15) -> None:
        """Executes cold startup profiling over the specified iteration count."""
        print(f"[{target.framework}] Executing cold startup profiling ({iterations} iterations)...")
        for i in range(1, iterations + 1):
            self.adb.force_stop(target.package_name)
            time.sleep(3.0)

            output = self.adb.start_cold(target.component)
            total_time = TelemetryExtractor.parse_startup_total_time(output)

            if total_time is not None:
                self.records.append(
                    MetricRecord(
                        framework=target.framework,
                        test_name="cold_startup",
                        iteration=i,
                        metric_name="total_time",
                        metric_value=float(total_time),
                        unit="ms",
                    )
                )
                print(f"  Iteration {i:02d}: {total_time} ms")
            else:
                print(f"  Iteration {i:02d}: Failed to parse startup time.")

    def run_memory_and_scroll_profiling(self, target: BenchmarkTarget) -> None:
        """Executes idle memory extraction, Workload A scroll jank profiling, compute memory, and Workload C animation."""
        print(f"[{target.framework}] Executing memory and rendering telemetry profiling...")
        self.adb.shell("settings put system accelerometer_rotation 0")
        self.adb.shell("settings put system user_rotation 0")
        self.adb.force_stop(target.package_name)
        time.sleep(2.0)
        self.adb.start_cold(target.component)
        time.sleep(3.0)

        w, h, rr = self.adb.get_device_info()
        is_high_res = (w > 1100 or h > 2500)
        btn_a = (610, 1265) if is_high_res else (540, 1140)
        btn_b = (610, 1475) if is_high_res else (540, 1330)
        btn_c = (610, 1685) if is_high_res else (540, 1525)
        btn_exec = (610, 438) if is_high_res else (540, 395)
        btn_back = (100, 200) if is_high_res else (100, 180)
        swipe_x = w // 2
        swipe_y1 = int(h * 0.66)
        swipe_y2 = int(h * 0.18)
        jank_threshold = 8.333 if rr > 90.0 else 16.666
        print(f"  Device profile: {w}x{h} @ {rr:.0f}Hz (Jank threshold = {jank_threshold:.2f} ms)")

        # 1. Idle memory
        idle_mem = TelemetryExtractor.parse_meminfo(self.adb.get_meminfo(target.package_name))
        for key, val in idle_mem.items():
            self.records.append(
                MetricRecord(
                    framework=target.framework,
                    test_name="memory_idle",
                    iteration=1,
                    metric_name=key,
                    metric_value=float(val),
                    unit="kB",
                )
            )
        print(f"  Idle Memory: Native={idle_mem['native_heap_pss']} kB, Dalvik={idle_mem['dalvik_heap_pss']} kB, Total={idle_mem['total_pss']} kB")

        # 2. Navigate to Workload A
        self.adb.tap(btn_a[0], btn_a[1])
        time.sleep(2.0)

        # Reset frametime buffers
        self.adb.reset_gfxinfo(target.package_name)
        surface_layer = f"SurfaceView[{target.package_name}/{target.package_name}.MainActivity](BLAST)#0"
        if target.framework == "flutter":
            self.adb.reset_surfaceflinger(surface_layer)

        # Execute 25 programmatic swipe gestures simulating fast scroll
        print(f"  Executing 25 programmatic fast scroll gestures on Workload A...")
        for swipe_idx in range(25):
            self.adb.swipe(swipe_x, swipe_y1, swipe_x, swipe_y2, 100)
            time.sleep(0.15)

        time.sleep(1.0)

        # Collect scroll memory
        scroll_mem = TelemetryExtractor.parse_meminfo(self.adb.get_meminfo(target.package_name))
        for key, val in scroll_mem.items():
            self.records.append(
                MetricRecord(
                    framework=target.framework,
                    test_name="memory_workload_a_scroll",
                    iteration=1,
                    metric_name=key,
                    metric_value=float(val),
                    unit="kB",
                )
            )

        # Collect framestats for Workload A
        framestats_output = self.adb.get_gfxinfo_framestats(target.package_name)
        durations_a = TelemetryExtractor.extract_frame_durations(framestats_output)
        if not durations_a and target.framework == "flutter":
            sf_output = self.adb.get_surfaceflinger_latency(surface_layer)
            durations_a = TelemetryExtractor.parse_surfaceflinger_latency(sf_output)

        if durations_a:
            total_frames = len(durations_a)
            janky_frames = sum(1 for d in durations_a if d > jank_threshold)
            p95_frametime = sorted(durations_a)[min(int(0.95 * total_frames), total_frames - 1)]
        else:
            total_frames, janky_frames, p95_frametime = 0, 0, 0.0

        for d in durations_a:
            self.frame_latencies.append((target.framework, "workload_a", d))

        self.records.append(
            MetricRecord(
                framework=target.framework,
                test_name="scroll_workload_a",
                iteration=1,
                metric_name="total_frames",
                metric_value=float(total_frames),
                unit="frames",
            )
        )
        self.records.append(
            MetricRecord(
                framework=target.framework,
                test_name="scroll_workload_a",
                iteration=1,
                metric_name="janky_frames",
                metric_value=float(janky_frames),
                unit="frames",
            )
        )
        self.records.append(
            MetricRecord(
                framework=target.framework,
                test_name="scroll_workload_a",
                iteration=1,
                metric_name="p95_frametime",
                metric_value=p95_frametime,
                unit="ms",
            )
        )
        print(f"  Workload A Framestats: Total={total_frames}, Janky={janky_frames}, p95={p95_frametime} ms")

        # 3. Workload B Navigation and Execution
        # Return to hub
        self.adb.tap(btn_back[0], btn_back[1])
        time.sleep(1.5)
        # Tap Workload B button
        self.adb.tap(btn_b[0], btn_b[1])
        time.sleep(1.5)
        # Tap Execute Benchmark button
        self.adb.tap(btn_exec[0], btn_exec[1])
        time.sleep(4.0)

        # Collect post-compute memory
        compute_mem = TelemetryExtractor.parse_meminfo(self.adb.get_meminfo(target.package_name))
        for key, val in compute_mem.items():
            self.records.append(
                MetricRecord(
                    framework=target.framework,
                    test_name="memory_workload_b_post_compute",
                    iteration=1,
                    metric_name=key,
                    metric_value=float(val),
                    unit="kB",
                )
            )
        print(f"  Post-Compute Memory: Native={compute_mem['native_heap_pss']} kB, Dalvik={compute_mem['dalvik_heap_pss']} kB, Total={compute_mem['total_pss']} kB")

        # 4. Workload C Navigation and Execution
        # Return to hub
        self.adb.tap(btn_back[0], btn_back[1])
        time.sleep(1.5)
        # Tap Workload C button
        self.adb.tap(btn_c[0], btn_c[1])
        time.sleep(2.0)
        # Reset frametime buffers
        self.adb.reset_gfxinfo(target.package_name)
        if target.framework == "flutter":
            self.adb.reset_surfaceflinger(surface_layer)

        print(f"  Sampling Workload C canvas animation for 10 seconds...")
        time.sleep(10.0)

        # Collect framestats for Workload C
        framestats_c = self.adb.get_gfxinfo_framestats(target.package_name)
        durations_c = TelemetryExtractor.extract_frame_durations(framestats_c)
        if not durations_c and target.framework == "flutter":
            sf_output_c = self.adb.get_surfaceflinger_latency(surface_layer)
            durations_c = TelemetryExtractor.parse_surfaceflinger_latency(sf_output_c)

        if durations_c:
            total_frames_c = len(durations_c)
            janky_frames_c = sum(1 for d in durations_c if d > jank_threshold)
            p95_frametime_c = sorted(durations_c)[min(int(0.95 * total_frames_c), total_frames_c - 1)]
        else:
            total_frames_c, janky_frames_c, p95_frametime_c = 0, 0, 0.0

        for d in durations_c:
            self.frame_latencies.append((target.framework, "workload_c", d))

        self.records.append(
            MetricRecord(
                framework=target.framework,
                test_name="animation_workload_c",
                iteration=1,
                metric_name="total_frames",
                metric_value=float(total_frames_c),
                unit="frames",
            )
        )
        self.records.append(
            MetricRecord(
                framework=target.framework,
                test_name="animation_workload_c",
                iteration=1,
                metric_name="janky_frames",
                metric_value=float(janky_frames_c),
                unit="frames",
            )
        )
        self.records.append(
            MetricRecord(
                framework=target.framework,
                test_name="animation_workload_c",
                iteration=1,
                metric_name="p95_frametime",
                metric_value=p95_frametime_c,
                unit="ms",
            )
        )
        print(f"  Workload C Framestats: Total={total_frames_c}, Janky={janky_frames_c}, p95={p95_frametime_c} ms")

        # Clean shutdown
        self.adb.force_stop(target.package_name)

    def export_csv(self) -> None:
        """Exports all recorded telemetry rows into the standardized CSV format."""
        header = ["framework", "test_name", "iteration", "metric_name", "metric_value", "unit"]
        os.makedirs(os.path.dirname(os.path.abspath(self.output_file)), exist_ok=True)
        with open(self.output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for record in self.records:
                writer.writerow(record.to_row())
        print(f"\nSuccessfully exported {len(self.records)} telemetry records to {self.output_file}")

        # Export individual frame durations
        out_dir = os.path.dirname(os.path.abspath(self.output_file))
        base_stem = os.path.splitext(os.path.basename(self.output_file))[0]
        lat_filename = "frame_latencies_poco.csv" if "poco" in base_stem else "frame_latencies.csv"
        latencies_file = os.path.join(out_dir, lat_filename)
        with open(latencies_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["framework", "workload", "duration_ms"])
            for framework, workload, duration in self.frame_latencies:
                writer.writerow([framework, workload, duration])
        print(f"Successfully exported {len(self.frame_latencies)} frame latency records to {latencies_file}")


def main() -> None:
    """CLI entrypoint for host benchmark execution."""
    parser = argparse.ArgumentParser(description="Dual-Framework ADB Benchmark Runner")
    parser.add_argument(
        "--framework",
        choices=["flutter", "react_native", "both"],
        default="both",
        help="Target framework benchmark to execute.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Specific ADB target device ID.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=15,
        help="Cold startup benchmark iterations.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="benchmark_results.csv",
        help="Destination path for benchmark CSV export.",
    )

    args = parser.parse_args()
    adb = AdbRunner(device_id=args.device)
    suite = BenchmarkSuite(adb=adb, output_file=args.output)

    targets_to_run: List[BenchmarkTarget] = []
    if args.framework in ("flutter", "both"):
        targets_to_run.append(TARGETS["flutter"])
    if args.framework in ("react_native", "both"):
        targets_to_run.append(TARGETS["react_native"])

    for target in targets_to_run:
        print(f"\n==================================================")
        print(f"STARTING BENCHMARK: {target.framework.upper()}")
        print(f"==================================================")
        suite.run_cold_startup(target, iterations=args.iterations)
        suite.run_memory_and_scroll_profiling(target)

    suite.export_csv()


if __name__ == "__main__":
    main()
