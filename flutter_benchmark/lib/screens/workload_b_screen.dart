import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/benchmark_payload.dart';

/// Worker isolate entrypoint for payload parsing, sorting, and aggregation.
BenchmarkResult executePayloadComputation(String rawJson) {
  final Stopwatch stopwatch = Stopwatch()..start();
  final List<dynamic> parsed = jsonDecode(rawJson) as List<dynamic>;
  final List<BenchmarkRecord> records = parsed
      .map((e) => BenchmarkRecord.fromJson(e as Map<String, dynamic>))
      .toList();

  records.sort((BenchmarkRecord a, BenchmarkRecord b) => b.timestamp.compareTo(a.timestamp));

  double scoreSum = 0.0;
  for (final BenchmarkRecord record in records) {
    scoreSum += record.metrics.score;
  }

  stopwatch.stop();
  return BenchmarkResult(
    durationMs: stopwatch.elapsedMilliseconds,
    totalScore: scoreSum,
  );
}

/// Screen 2: Workload B measuring CPU parsing, sorting, and numeric computation.
class WorkloadBScreen extends StatefulWidget {
  /// Route path for [WorkloadBScreen].
  static const String routeName = '/workload_b';

  /// Creates a [WorkloadBScreen] instance.
  const WorkloadBScreen({super.key});

  @override
  State<WorkloadBScreen> createState() => _WorkloadBScreenState();
}

class _WorkloadBScreenState extends State<WorkloadBScreen> {
  final TextEditingController _mainDurationController = TextEditingController();
  final TextEditingController _workerDurationController = TextEditingController();
  final TextEditingController _scoreSumController = TextEditingController();

  bool _isProcessing = false;

  @override
  void dispose() {
    _mainDurationController.dispose();
    _workerDurationController.dispose();
    _scoreSumController.dispose();
    super.dispose();
  }

  Future<void> _executeBenchmark() async {
    setState(() {
      _isProcessing = true;
    });

    final String rawJson = await rootBundle.loadString('assets/data/payload_10k.json');

    // 1. Execute on main isolate
    final BenchmarkResult mainResult = executePayloadComputation(rawJson);

    // 2. Execute on worker isolate via compute()
    final BenchmarkResult workerResult = await compute(executePayloadComputation, rawJson);

    if (mounted) {
      setState(() {
        _mainDurationController.text = '${mainResult.durationMs} ms';
        _workerDurationController.text = '${workerResult.durationMs} ms';
        _scoreSumController.text = mainResult.totalScore.toStringAsFixed(4);
        _isProcessing = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Workload B: JSON Deserialization'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ElevatedButton(
              key: const Key('btn_execute_benchmark'),
              onPressed: _isProcessing ? null : _executeBenchmark,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16.0),
              ),
              child: _isProcessing
                  ? const SizedBox(
                      height: 20.0,
                      width: 20.0,
                      child: CircularProgressIndicator(strokeWidth: 2.0),
                    )
                  : const Text(
                      'Execute Benchmark',
                      style: TextStyle(fontSize: 16.0),
                    ),
            ),
            const SizedBox(height: 24.0),
            TextField(
              key: const Key('txt_main_duration'),
              controller: _mainDurationController,
              readOnly: true,
              decoration: const InputDecoration(
                labelText: 'Main Isolate Duration',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16.0),
            TextField(
              key: const Key('txt_worker_duration'),
              controller: _workerDurationController,
              readOnly: true,
              decoration: const InputDecoration(
                labelText: 'Worker Isolate Duration',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16.0),
            TextField(
              key: const Key('txt_score_sum'),
              controller: _scoreSumController,
              readOnly: true,
              decoration: const InputDecoration(
                labelText: 'Aggregated Score Sum',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
