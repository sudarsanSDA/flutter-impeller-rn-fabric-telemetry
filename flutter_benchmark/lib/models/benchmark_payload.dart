/// Nested metric payload object.
class MetricData {
  /// Numeric score evaluated during benchmark summation.
  final double score;

  /// Quantity count metric.
  final int count;

  /// Category classification.
  final String category;

  /// Creates a [MetricData] instance.
  const MetricData({
    required this.score,
    required this.count,
    required this.category,
  });

  /// Deserializes a [MetricData] from a JSON map.
  factory MetricData.fromJson(Map<String, dynamic> json) {
    return MetricData(
      score: (json['score'] as num).toDouble(),
      count: json['count'] as int,
      category: json['category'] as String,
    );
  }
}

/// Model representing a single record in the compute benchmark payload.
class BenchmarkRecord {
  /// Global unique identifier.
  final String guid;

  /// ISO-8601 UTC timestamp string.
  final String timestamp;

  /// Activity status flag.
  final bool isActive;

  /// Associated classification tags.
  final List<String> tags;

  /// Nested metrics payload.
  final MetricData metrics;

  /// Creates a [BenchmarkRecord] instance.
  const BenchmarkRecord({
    required this.guid,
    required this.timestamp,
    required this.isActive,
    required this.tags,
    required this.metrics,
  });

  /// Deserializes a [BenchmarkRecord] from a JSON map.
  factory BenchmarkRecord.fromJson(Map<String, dynamic> json) {
    return BenchmarkRecord(
      guid: json['guid'] as String,
      timestamp: json['timestamp'] as String,
      isActive: json['isActive'] as bool,
      tags: (json['tags'] as List<dynamic>).map((e) => e as String).toList(),
      metrics: MetricData.fromJson(json['metrics'] as Map<String, dynamic>),
    );
  }
}

/// Execution outcome of a compute workload pass.
class BenchmarkResult {
  /// Duration of parsing and computation in milliseconds.
  final int durationMs;

  /// Aggregated score across all processed records.
  final double totalScore;

  /// Creates a [BenchmarkResult] instance.
  const BenchmarkResult({
    required this.durationMs,
    required this.totalScore,
  });
}
