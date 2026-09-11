# Replication Package: Flutter Impeller vs. React Native New Architecture

This repository contains the automated telemetry harness, parity application implementations, and raw empirical datasets for the research paper:

> **"Architectural Convergence and Runtime Discrepancies: A Multi-Tier Empirical Telemetry Analysis of Flutter Impeller versus React Native Fabric and Hermes"**  
> *(Currently under review at Innovations in Systems and Software Engineering)*

---

## 1. Overview

This replication package contains the complete reproducible benchmark suite, workload implementations, external Android Debug Bridge (ADB) telemetry harnesses, and raw empirical datasets.

### Evaluated Performance Dimensions
* **Cold Startup Latency:** OS-reported process bootstrap from zygote fork to first interactive frame.
* **Proportional Set Size (PSS) Memory:** Decomposition into Native Heap, Dalvik/Hermes Heap, and OS graphics buffers across idle, virtualized list scrolling, and JSON computation states.
* **Frame Rendering Latencies & Jank Distribution:** High-frequency frametime distributions across 60 Hz (16.67 ms) and 120 Hz (8.33 ms) display refresh budgets.
* **Release Binary Footprint:** Exact single-ABI (`arm64-v8a`) release APK size comparison.

```bash
git clone https://github.com/sudarsanSDA/flutter-impeller-rn-fabric-telemetry.git
cd flutter-impeller-rn-fabric-telemetry
```

---

## 2. Hardware Testbed

All telemetry was captured on dedicated bare-metal Android smartphones:

| Specification | Tier-1 (Legacy Mid-Range Baseline) | Tier-2 (Modern High-Performance Flagship-Killer) |
| :--- | :--- | :--- |
| **Device Model** | Xiaomi Redmi Note 9 Pro (`curtana`) | Xiaomi POCO X6 Pro 5G (`duchamp` / `2311DRK48I`) |
| **SoC** | Qualcomm Snapdragon 720G (8 nm LPP) | MediaTek Dimensity 8300-Ultra (TSMC 4 nm) |
| **CPU Microarchitecture** | $2\times$ 2.3 GHz Kryo 465 Gold (Cortex-A76)<br>$6\times$ 1.8 GHz Kryo 465 Silver (Cortex-A55) | $1\times$ 3.35 GHz Cortex-A715 (Prime core)<br>$3\times$ 3.20 GHz Cortex-A715 (Performance)<br>$4\times$ 2.20 GHz Cortex-A510 (Efficiency) |
| **GPU** | Qualcomm Adreno 618 | ARM Mali-G615 MC6 |
| **RAM** | 4 GB LPDDR4X | 8 GB LPDDR5X |
| **Storage** | 64 GB UFS 2.1 | 256 GB UFS 4.0 |
| **Operating System** | Android 12 (API Level 31) | Xiaomi HyperOS / Android 14 (API Level 34) |
| **Display Budget** | $1080 \times 2400$ @ 60 Hz (16.67 ms deadline) | $1220 \times 2712$ @ 120 Hz (8.33 ms deadline) |

---

## 3. Directory Structure

```
crossplatform-benchmark/
├── benchmark_harness/
│   ├── runner.py                    # Host-driven automated ADB telemetry harness
│   ├── generate_paper_artifacts.py  # Statistical synthesis & figure generation script
│   ├── requirements.txt             # Python dependencies
│   ├── benchmark_results.csv        # Raw Tier-1 cold start & memory telemetry
│   ├── frame_latencies.csv          # Raw Tier-1 frametime telemetry
│   ├── benchmark_results_poco.csv   # Raw Tier-2 cold start & memory telemetry
│   └── frame_latencies_poco.csv     # Raw Tier-2 frametime telemetry
├── flutter_benchmark/               # Flutter 3.24 application source
│   ├── lib/                         # Screens (Hub, Workloads A, B, C)
│   └── pubspec.yaml                 # Dependencies & asset configuration
├── react_native_benchmark/          # React Native 0.76 application source
│   ├── src/                         # Screens (Hub, Workloads A, B, C)
│   └── package.json                 # Dependencies & New Architecture configuration
├── shared_assets/                   # Identical static assets & payload generators
│   ├── avatar.png                   # Fixed 40 dp avatar image asset
│   ├── list_5k.json                 # 5,000-record dataset for Workload A
│   ├── compute_payload_10k.json     # 5 MB / 10,000-record payload for Workload B
│   └── generate_assets.py           # Asset synthesis script
├── paper_artifacts/
│   ├── figures/                     # High-resolution vector PDFs and 300+ DPI PNGs
│   └── tables/                      # Formatted descriptive statistics tables
├── LICENSE                          # MIT License
└── README.md                        # Documentation
```

---

## 4. Workload Descriptions

Both applications implement identical functional workflows:
* **Screen 0 (Navigation Hub):** Landing activity providing triggers for workloads; canonical baseline for cold startup measurements.
* **Screen 1 (Workload A: List Virtualization):** Renders 5,000 JSON records in an infinitely virtualized list. Each item has a fixed 72 dp height with a 40 dp circular avatar, title, subtitle, and badge count (`ListView.builder` vs. `FlatList` with `getItemLayout`).
* **Screen 2 (Workload B: JSON Deserialization & Compute):** Loads a 5 MB payload containing 10,000 telemetry objects, sorts records descending by ISO-8601 UTC timestamp, and aggregates floating-point score values.
* **Screen 3 (Workload C: 2D Graphics Animation):** Stresses the graphics pipeline with an intensive 60-second animation featuring 100 independent bouncing geometric particles (`CustomPainter` with Impeller vs. Fabric UI thread animated vector transforms).

---

## 5. Device Calibration Protocol

Before executing benchmarks, apply the following device calibrations to eliminate background noise:
1. **Airplane Mode:** Enable Airplane Mode to disable cellular, Wi-Fi, and Bluetooth radios.
2. **Backlight Lock:** Disable auto-brightness and fix the backlight slider to 50%.
3. **Refresh Rate Lock:** Lock display refresh rate to 60 Hz on Tier-1 and 120 Hz on Tier-2.
4. **Thermal Stabilization:** Remove protective cases and enforce a minimum 3.0-second cooldown between iterations.
5. **Screen Orientation:** Lock display orientation to portrait mode:
   ```bash
   adb shell settings put system accelerometer_rotation 0
   adb shell settings put system user_rotation 0
   ```

---

## 6. Building Single-ABI Release Binaries

To ensure fair binary size comparisons, compile both applications for a single target architecture (`arm64-v8a`):

### Flutter Build
```bash
cd flutter_benchmark
flutter build apk --release --split-per-abi
# Output: flutter_benchmark/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk (7.42 MB)
```

### React Native Build
Ensure `enableSeparateBuildPerCPUArchitecture = true` in `react_native_benchmark/android/app/build.gradle`. Then run:
```bash
cd react_native_benchmark/android
./gradlew assembleRelease
# Output: react_native_benchmark/android/app/build/outputs/apk/release/app-arm64-v8a-release.apk (13.83 MB)
```

### Deploying Binaries
```bash
adb install -r flutter_benchmark/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
adb install -r react_native_benchmark/android/app/build/outputs/apk/release/app-arm64-v8a-release.apk
```

---

## 7. Telemetry Harness Execution

Install harness dependencies:
```bash
cd benchmark_harness
pip install -r requirements.txt
```

### Running the Telemetry Harness
```bash
# Execute 15 cold-start iterations and full memory/frametime profiling on connected device:
python runner.py --framework both --iterations 15
```

### Regenerating Publication Figures and Tables
```bash
python generate_paper_artifacts.py
```
This script processes the raw CSV files and regenerates all figures (`fig1_startup`, `fig2_memory`, `fig3_frametime`, `fig4_binary_size`) in vector PDF and 300+ DPI PNG formats.

---

## 8. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
