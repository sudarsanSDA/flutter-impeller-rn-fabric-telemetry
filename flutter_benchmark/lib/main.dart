import 'package:flutter/material.dart';
import 'screens/hub_screen.dart';
import 'screens/workload_a_screen.dart';
import 'screens/workload_b_screen.dart';
import 'screens/workload_c_screen.dart';

/// Application entry point.
void main() {
  runApp(const BenchmarkApp());
}

/// Root widget configuring benchmark theme and route declarations.
class BenchmarkApp extends StatelessWidget {
  /// Creates a [BenchmarkApp] instance.
  const BenchmarkApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Benchmark',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      initialRoute: HubScreen.routeName,
      routes: {
        HubScreen.routeName: (context) => const HubScreen(),
        WorkloadAScreen.routeName: (context) => const WorkloadAScreen(),
        WorkloadBScreen.routeName: (context) => const WorkloadBScreen(),
        WorkloadCScreen.routeName: (context) => const WorkloadCScreen(),
      },
    );
  }
}
