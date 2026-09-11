/** Model representing a virtualized list item. */
export interface ListItem {
  id: number;
  title: string;
  subtitle: string;
  badge_count: number;
}

/** Metrics nested object within benchmark payload. */
export interface MetricData {
  score: number;
  count: number;
  category: string;
}

/** Single record in the deserialization benchmark dataset. */
export interface BenchmarkRecord {
  guid: string;
  timestamp: string;
  isActive: boolean;
  description: string;
  tags: string[];
  metrics: MetricData;
}

/** Result metrics for Workload B compute execution. */
export interface BenchmarkResult {
  durationMs: number;
  totalScore: number;
}

/** Shape geometry type discriminator. */
export type ShapeKind = 'circle' | 'roundedRectangle';

/** State configuration for animated 2D geometric particle. */
export interface ParticleShape {
  id: number;
  kind: ShapeKind;
  color: string;
  width: number;
  height: number;
  x: number;
  y: number;
  dx: number;
  dy: number;
  rotation: number;
  angularVelocity: number;
}
