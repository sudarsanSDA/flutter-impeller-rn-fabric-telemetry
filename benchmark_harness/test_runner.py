"""Unit tests for benchmark telemetry extraction and CSV formatting."""

import os
import unittest
from runner import TelemetryExtractor, MetricRecord, BenchmarkSuite


class TestTelemetryExtractor(unittest.TestCase):
    """Verifies regex and table parsers against sample ADB command outputs."""

    def test_startup_total_time_parsing(self):
        sample_output = """
        Starting: Intent { act=android.intent.action.MAIN cat=[android.intent.category.LAUNCHER] cmp=com.benchmark.flutter_benchmark/.MainActivity }
        Status: ok
        LaunchState: COLD
        Activity: com.benchmark.flutter_benchmark/.MainActivity
        TotalTime: 482
        WaitTime: 490
        Complete
        """
        parsed = TelemetryExtractor.parse_startup_total_time(sample_output)
        self.assertEqual(parsed, 482)

    def test_meminfo_parsing(self):
        sample_output = """
        Applications Memory Usage (in Kilobytes):
        Uptime: 104523 Realtime: 203921

        ** MEMINFO in pid 1234 [com.benchmark.flutter_benchmark] **
                           Pss  Private  Private  SwapPss      Rss     Heap     Heap     Heap
                         Total    Dirty    Clean    Dirty    Total     Size    Alloc     Free
                        ------   ------   ------   ------   ------   ------   ------   ------
          Native Heap    25412    24980        0        0    31200    45056    32110    12946
          Dalvik Heap    15230    14800        0        0    22400    28672    18500    10172
                Stack       60       60        0        0       64
               Ashmem      120        0        0        0      120
            Other dev       16        0       16        0       32
             .so mmap     8412      820     5200        0    24100
            .apk mmap     2100        0      400        0     6200
            .ttf mmap      340        0      120        0      800
            .dex mmap     4500        4     2100        0     7800
            .oat mmap      890        0      210        0     2400
            TOTAL PSS:   64320
        """
        metrics = TelemetryExtractor.parse_meminfo(sample_output)
        self.assertEqual(metrics["native_heap_pss"], 25412)
        self.assertEqual(metrics["dalvik_heap_pss"], 15230)
        self.assertEqual(metrics["total_pss"], 64320)

    def test_framestats_parsing(self):
        sample_output = """
        ---PROFILEDATA---
        Flags,IntendedVsync,Vsync,OldestInputEvent,NewestInputEvent,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,
        0,1000000000,1000000000,1000000000,1000000000,1000000000,1000000000,1000000000,1000000000,1000000000,1000000000,1000000000,1008000000,1012000000,100000,100000,
        0,2000000000,2000000000,2000000000,2000000000,2000000000,2000000000,2000000000,2000000000,2000000000,2000000000,2000000000,2018000000,2022000000,100000,100000,
        ---PROFILEDATA---
        """
        total_frames, janky_frames, p95 = TelemetryExtractor.parse_framestats(sample_output)
        self.assertEqual(total_frames, 2)
        self.assertEqual(janky_frames, 1)  # Frame 2 is 22ms > 16.6ms
        self.assertGreater(p95, 0.0)

    def test_csv_export(self):
        import shutil
        test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_tmp_dir")
        test_csv_path = os.path.join(test_dir, "test_results.csv")
        suite = BenchmarkSuite(adb=None, output_file=test_csv_path)
        suite.records.append(
            MetricRecord(
                framework="flutter",
                test_name="cold_startup",
                iteration=1,
                metric_name="total_time",
                metric_value=450.0,
                unit="ms",
            )
        )
        suite.export_csv()
        self.assertTrue(os.path.exists(test_csv_path))

        with open(test_csv_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]

        self.assertEqual(lines[0], "framework,test_name,iteration,metric_name,metric_value,unit")
        self.assertEqual(lines[1], "flutter,cold_startup,1,total_time,450.0,ms")

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
