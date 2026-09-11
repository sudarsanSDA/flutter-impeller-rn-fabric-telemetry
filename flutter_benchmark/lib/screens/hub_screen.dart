import 'package:flutter/material.dart';

/// Screen 0: Navigation Hub serving as the cold-start landing view.
class HubScreen extends StatelessWidget {
  /// Route path for [HubScreen].
  static const String routeName = '/';

  /// Creates a [HubScreen] instance.
  const HubScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Benchmark Hub'),
        centerTitle: true,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              ElevatedButton(
                key: const Key('btn_workload_a'),
                onPressed: () {
                  Navigator.pushNamed(context, '/workload_a');
                },
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16.0),
                ),
                child: const Text(
                  'Workload A: Virtualized List',
                  style: TextStyle(fontSize: 16.0),
                ),
              ),
              const SizedBox(height: 16.0),
              ElevatedButton(
                key: const Key('btn_workload_b'),
                onPressed: () {
                  Navigator.pushNamed(context, '/workload_b');
                },
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16.0),
                ),
                child: const Text(
                  'Workload B: JSON Deserialization',
                  style: TextStyle(fontSize: 16.0),
                ),
              ),
              const SizedBox(height: 16.0),
              ElevatedButton(
                key: const Key('btn_workload_c'),
                onPressed: () {
                  Navigator.pushNamed(context, '/workload_c');
                },
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16.0),
                ),
                child: const Text(
                  'Workload C: Canvas Animation',
                  style: TextStyle(fontSize: 16.0),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
