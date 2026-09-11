# Descriptive Empirical Statistics (Multi-Tier Evaluation)

## 1. Cold Startup Latency (ms)

| tier                             | framework    |    Mean |      Std |   Min |   Median |   Max |
|:---------------------------------|:-------------|--------:|---------:|------:|---------:|------:|
| Tier-1 (SD 720G @ 60Hz)          | flutter      | 395     | 22.4117  |   365 |      396 |   446 |
| Tier-1 (SD 720G @ 60Hz)          | react_native | 294.2   |  8.16963 |   277 |      294 |   310 |
| Tier-2 (Dimensity 8300U @ 120Hz) | flutter      | 335.867 | 36.4963  |   279 |      335 |   422 |
| Tier-2 (Dimensity 8300U @ 120Hz) | react_native | 249.267 | 21.3021  |   217 |      244 |   288 |

## 2. Memory Footprint (PSS in MB)

| tier                             | framework    | test_name                      |   native_mb |   dalvik_mb |   total_mb |
|:---------------------------------|:-------------|:-------------------------------|------------:|------------:|-----------:|
| Tier-1 (SD 720G @ 60Hz)          | flutter      | memory_idle                    |        8.95 |        3.1  |      90.83 |
| Tier-1 (SD 720G @ 60Hz)          | flutter      | memory_workload_a_scroll       |       12.34 |        7.59 |     105.21 |
| Tier-1 (SD 720G @ 60Hz)          | flutter      | memory_workload_b_post_compute |       13.34 |        7.16 |     123.02 |
| Tier-1 (SD 720G @ 60Hz)          | react_native | memory_idle                    |        8.93 |        4.61 |      63.8  |
| Tier-1 (SD 720G @ 60Hz)          | react_native | memory_workload_a_scroll       |       33.52 |       14.31 |     136.47 |
| Tier-1 (SD 720G @ 60Hz)          | react_native | memory_workload_b_post_compute |       37.32 |       12.49 |     134.75 |
| Tier-2 (Dimensity 8300U @ 120Hz) | flutter      | memory_idle                    |       30.73 |        2.62 |     210.06 |
| Tier-2 (Dimensity 8300U @ 120Hz) | flutter      | memory_workload_a_scroll       |       34.04 |        6.72 |     190.86 |
| Tier-2 (Dimensity 8300U @ 120Hz) | flutter      | memory_workload_b_post_compute |       36.22 |        6.63 |     236.26 |
| Tier-2 (Dimensity 8300U @ 120Hz) | react_native | memory_idle                    |       24.1  |        5.62 |      96.87 |
| Tier-2 (Dimensity 8300U @ 120Hz) | react_native | memory_workload_a_scroll       |       59.37 |       17.22 |     159.53 |
| Tier-2 (Dimensity 8300U @ 120Hz) | react_native | memory_workload_b_post_compute |       60.05 |       13.18 |     152.43 |

## 3. Frame Latency & Jank Distribution (ms)

| tier                             | framework    | workload   |   Count |   Mean |   Std |   p50 |   p95 |   Max |   Janky_Count |   Jank_Pct |
|:---------------------------------|:-------------|:-----------|--------:|-------:|------:|------:|------:|------:|--------------:|-----------:|
| Tier-1 (SD 720G @ 60Hz)          | flutter      | workload_a |     126 |  16.84 |  1.48 | 16.7  | 16.91 | 33.31 |            98 |       77.8 |
| Tier-1 (SD 720G @ 60Hz)          | flutter      | workload_c |     125 |  16.71 |  0.59 | 16.71 | 16.95 | 21.3  |            91 |       72.8 |
| Tier-1 (SD 720G @ 60Hz)          | react_native | workload_a |     118 |  15.07 |  5.83 | 15.62 | 23.89 | 36.29 |            56 |       47.5 |
| Tier-1 (SD 720G @ 60Hz)          | react_native | workload_c |     119 |  31.02 |  5.97 | 30.9  | 44.89 | 49.85 |           119 |      100   |
| Tier-2 (Dimensity 8300U @ 120Hz) | flutter      | workload_a |     125 |   8.43 |  0.5  |  8.36 |  9.04 | 11.2  |            65 |       52   |
| Tier-2 (Dimensity 8300U @ 120Hz) | flutter      | workload_c |     125 |   8.35 |  0.11 |  8.36 |  8.55 |  8.76 |            71 |       56.8 |
| Tier-2 (Dimensity 8300U @ 120Hz) | react_native | workload_a |     118 |  17.24 |  2.89 | 18.19 | 19.31 | 20.15 |           113 |       95.8 |
| Tier-2 (Dimensity 8300U @ 120Hz) | react_native | workload_c |     119 |  12.45 |  4.62 | 10.93 | 23.38 | 28.97 |           101 |       84.9 |
