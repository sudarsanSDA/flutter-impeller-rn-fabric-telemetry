import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_benchmark/main.dart';

void main() {
  testWidgets('Benchmark hub renders workload buttons', (WidgetTester tester) async {
    await tester.pumpWidget(const BenchmarkApp());
    expect(find.text('Workload A: Virtualized List'), findsOneWidget);
    expect(find.text('Workload B: JSON Deserialization'), findsOneWidget);
    expect(find.text('Workload C: Canvas Animation'), findsOneWidget);
  });
}
