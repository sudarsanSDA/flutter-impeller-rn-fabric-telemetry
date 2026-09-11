import 'dart:math';
import 'package:flutter/material.dart';

/// Supported 2D geometric shape categories.
enum ShapeKind {
  /// Circular geometric primitive.
  circle,

  /// Rounded rectangular geometric primitive.
  roundedRectangle,
}

/// State representation of an animated 2D geometric particle.
class ParticleShape {
  /// Geometry classification.
  final ShapeKind kind;

  /// Render color.
  final Color color;

  /// Width or diameter in density-independent pixels.
  final double width;

  /// Height in density-independent pixels.
  final double height;

  /// Current horizontal coordinate.
  double x;

  /// Current vertical coordinate.
  double y;

  /// Horizontal velocity vector component.
  double dx;

  /// Vertical velocity vector component.
  double dy;

  /// Current angular orientation in radians.
  double rotation;

  /// Angular velocity in radians per frame.
  final double angularVelocity;

  /// Creates a [ParticleShape] instance.
  ParticleShape({
    required this.kind,
    required this.color,
    required this.width,
    required this.height,
    required this.x,
    required this.y,
    required this.dx,
    required this.dy,
    required this.rotation,
    required this.angularVelocity,
  });

  /// Advances particle spatial coordinates and reflects off viewport boundaries.
  void update(double boundaryWidth, double boundaryHeight) {
    x += dx;
    y += dy;
    rotation += angularVelocity;

    final double halfW = width / 2.0;
    final double halfH = height / 2.0;

    if (x - halfW < 0.0) {
      x = halfW;
      dx = -dx;
    } else if (x + halfW > boundaryWidth) {
      x = boundaryWidth - halfW;
      dx = -dx;
    }

    if (y - halfH < 0.0) {
      y = halfH;
      dy = -dy;
    } else if (y + halfH > boundaryHeight) {
      y = boundaryHeight - halfH;
      dy = -dy;
    }
  }
}

/// Custom painter for rendering 100 geometric shapes on the Impeller engine canvas.
class CanvasAnimationPainter extends CustomPainter {
  /// Collection of active particles.
  final List<ParticleShape> particles;

  /// Paint object reused across render cycles.
  final Paint _paint = Paint()..style = PaintingStyle.fill;

  /// Creates a [CanvasAnimationPainter] instance.
  CanvasAnimationPainter({required this.particles});

  @override
  void paint(Canvas canvas, Size size) {
    for (final ParticleShape p in particles) {
      _paint.color = p.color;
      canvas.save();
      canvas.translate(p.x, p.y);
      canvas.rotate(p.rotation);

      if (p.kind == ShapeKind.circle) {
        canvas.drawCircle(Offset.zero, p.width / 2.0, _paint);
      } else {
        final Rect rect = Rect.fromCenter(
          center: Offset.zero,
          width: p.width,
          height: p.height,
        );
        final RRect rrect = RRect.fromRectAndRadius(
          rect,
          const Radius.circular(6.0),
        );
        canvas.drawRRect(rrect, _paint);
      }
      canvas.restore();
    }
  }

  @override
  bool shouldRepaint(covariant CanvasAnimationPainter oldDelegate) => true;
}

/// Screen 3: Workload C executing 2D graphic rasterization via Impeller CustomPainter.
class WorkloadCScreen extends StatefulWidget {
  /// Route path for [WorkloadCScreen].
  static const String routeName = '/workload_c';

  /// Creates a [WorkloadCScreen] instance.
  const WorkloadCScreen({super.key});

  @override
  State<WorkloadCScreen> createState() => _WorkloadCScreenState();
}

class _WorkloadCScreenState extends State<WorkloadCScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  final List<ParticleShape> _particles = [];
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 60),
    )..addListener(_onTick);

    _initParticles();
    _controller.forward();
  }

  void _initParticles() {
    final Random random = Random(42);
    final List<Color> palette = [
      const Color(0xFFE53935),
      const Color(0xFF1E88E5),
      const Color(0xFF43A047),
      const Color(0xFFFB8C00),
      const Color(0xFF8E24AA),
      const Color(0xFF00ACC1),
    ];

    // 50 Circles
    for (int i = 0; i < 50; i++) {
      _particles.add(
        ParticleShape(
          kind: ShapeKind.circle,
          color: palette[i % palette.length].withOpacity(0.8),
          width: 32.0,
          height: 32.0,
          x: 100.0 + random.nextDouble() * 200.0,
          y: 100.0 + random.nextDouble() * 400.0,
          dx: (random.nextDouble() * 4.0 + 1.5) * (random.nextBool() ? 1.0 : -1.0),
          dy: (random.nextDouble() * 4.0 + 1.5) * (random.nextBool() ? 1.0 : -1.0),
          rotation: random.nextDouble() * 2.0 * pi,
          angularVelocity: (random.nextDouble() * 0.06 + 0.02) * (random.nextBool() ? 1.0 : -1.0),
        ),
      );
    }

    // 50 Rounded Rectangles
    for (int i = 0; i < 50; i++) {
      _particles.add(
        ParticleShape(
          kind: ShapeKind.roundedRectangle,
          color: palette[(i + 3) % palette.length].withOpacity(0.8),
          width: 36.0,
          height: 24.0,
          x: 100.0 + random.nextDouble() * 200.0,
          y: 100.0 + random.nextDouble() * 400.0,
          dx: (random.nextDouble() * 4.0 + 1.5) * (random.nextBool() ? 1.0 : -1.0),
          dy: (random.nextDouble() * 4.0 + 1.5) * (random.nextBool() ? 1.0 : -1.0),
          rotation: random.nextDouble() * 2.0 * pi,
          angularVelocity: (random.nextDouble() * 0.06 + 0.02) * (random.nextBool() ? 1.0 : -1.0),
        ),
      );
    }

    _isInitialized = true;
  }

  void _onTick() {
    if (!mounted) return;
    final Size size = MediaQuery.of(context).size;
    for (final ParticleShape p in _particles) {
      p.update(size.width, size.height);
    }
    setState(() {});
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Workload C: Canvas Animation'),
      ),
      body: !_isInitialized
          ? const Center(child: CircularProgressIndicator())
          : CustomPaint(
              painter: CanvasAnimationPainter(particles: _particles),
              child: const SizedBox.expand(),
            ),
    );
  }
}
