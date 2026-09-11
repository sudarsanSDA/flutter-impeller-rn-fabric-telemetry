import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
} from 'react-native';
import type { LayoutChangeEvent } from 'react-native';
import type { ParticleShape, ShapeKind } from '../types/benchmark';

/** Props for WorkloadCScreen. */
export interface WorkloadCScreenProps {
  onBack: () => void;
  autoPlay?: boolean;
}

const PALETTE = [
  'rgba(229, 57, 53, 0.8)',
  'rgba(30, 136, 229, 0.8)',
  'rgba(67, 160, 71, 0.8)',
  'rgba(251, 140, 0, 0.8)',
  'rgba(142, 36, 170, 0.8)',
  'rgba(0, 172, 193, 0.8)',
];

function createRng(initialSeed: number) {
  let s = initialSeed;
  return () => {
    s = (s * 1664525 + 1013904223) % 4294967296;
    return s / 4294967296;
  };
}

function generateInitialParticles(): ParticleShape[] {
  const rng = createRng(42);
  const list: ParticleShape[] = [];

  // 50 Circles
  for (let i = 0; i < 50; i++) {
    list.push({
      id: i,
      kind: 'circle' as ShapeKind,
      color: PALETTE[i % PALETTE.length],
      width: 32,
      height: 32,
      x: 100 + rng() * 150,
      y: 100 + rng() * 300,
      dx: (rng() * 4 + 1.5) * (rng() > 0.5 ? 1 : -1),
      dy: (rng() * 4 + 1.5) * (rng() > 0.5 ? 1 : -1),
      rotation: Math.round(rng() * 360),
      angularVelocity: Math.round(rng() * 4 + 1) * (rng() > 0.5 ? 1 : -1),
    });
  }

  // 50 Rounded Rectangles
  for (let i = 0; i < 50; i++) {
    list.push({
      id: 50 + i,
      kind: 'roundedRectangle' as ShapeKind,
      color: PALETTE[(i + 3) % PALETTE.length],
      width: 36,
      height: 24,
      x: 100 + rng() * 150,
      y: 100 + rng() * 300,
      dx: (rng() * 4 + 1.5) * (rng() > 0.5 ? 1 : -1),
      dy: (rng() * 4 + 1.5) * (rng() > 0.5 ? 1 : -1),
      rotation: Math.round(rng() * 360),
      angularVelocity: Math.round(rng() * 4 + 1) * (rng() > 0.5 ? 1 : -1),
    });
  }

  return list;
}

/** Screen 3: Workload C rasterizing 100 animated 2D geometric shapes for 60 seconds. */
export const WorkloadCScreen: React.FC<WorkloadCScreenProps> = ({
  onBack,
  autoPlay = true,
}) => {
  const [particles, setParticles] = useState<ParticleShape[]>(generateInitialParticles);
  const particlesRef = useRef<ParticleShape[]>(particles);
  const animationFrameId = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);
  const canvasWidthRef = useRef<number>(360);
  const canvasHeightRef = useRef<number>(600);

  const handleLayout = (e: LayoutChangeEvent) => {
    const { width, height } = e.nativeEvent.layout;
    if (width > 0 && height > 0) {
      canvasWidthRef.current = width;
      canvasHeightRef.current = height;
    }
  };

  useEffect(() => {
    particlesRef.current = particles;
  }, [particles]);

  useEffect(() => {
    if (!autoPlay) {
      return;
    }

    startTimeRef.current = Date.now();

    const tick = () => {
      const now = Date.now();
      const elapsed = (now - startTimeRef.current) / 1000;
      if (elapsed >= 60) {
        return;
      }

      const list = particlesRef.current;
      const boundaryWidth = canvasWidthRef.current;
      const boundaryHeight = canvasHeightRef.current;

      const updated = list.map(p => {
        let newX = p.x + p.dx;
        let newY = p.y + p.dy;
        let newDx = p.dx;
        let newDy = p.dy;
        const newRot = (p.rotation + p.angularVelocity) % 360;

        const halfW = p.width / 2;
        const halfH = p.height / 2;

        if (newX - halfW < 0) {
          newX = halfW;
          newDx = -newDx;
        } else if (newX + halfW > boundaryWidth) {
          newX = boundaryWidth - halfW;
          newDx = -newDx;
        }

        if (newY - halfH < 0) {
          newY = halfH;
          newDy = -newDy;
        } else if (newY + halfH > boundaryHeight) {
          newY = boundaryHeight - halfH;
          newDy = -newDy;
        }

        return {
          ...p,
          x: newX,
          y: newY,
          dx: newDx,
          dy: newDy,
          rotation: newRot,
        };
      });

      particlesRef.current = updated;
      setParticles(updated);

      if (typeof requestAnimationFrame === 'function') {
        animationFrameId.current = requestAnimationFrame(tick);
      }
    };

    if (typeof requestAnimationFrame === 'function') {
      animationFrameId.current = requestAnimationFrame(tick);
    }

    return () => {
      if (animationFrameId.current !== null && typeof cancelAnimationFrame === 'function') {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [autoPlay]);

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <Pressable onPress={onBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>Back</Text>
        </Pressable>
        <Text style={styles.topBarTitle}>Workload C: Canvas Animation</Text>
      </View>

      <View style={styles.canvasContainer} onLayout={handleLayout}>
        {particles.map(p => {
          const isCircle = p.kind === 'circle';
          return (
            <View
              key={p.id}
              style={[
                styles.particle,
                {
                  width: p.width,
                  height: p.height,
                  backgroundColor: p.color,
                  borderRadius: isCircle ? p.width / 2 : 6,
                  transform: [
                    { translateX: p.x - p.width / 2 },
                    { translateY: p.y - p.height / 2 },
                    { rotate: `${p.rotation}deg` },
                  ],
                },
              ]}
            />
          );
        })}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  topBar: {
    height: 56,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    backgroundColor: '#F9FAFB',
    zIndex: 10,
  },
  backButton: {
    paddingVertical: 8,
    paddingRight: 16,
  },
  backButtonText: {
    fontSize: 16,
    color: '#2563EB',
    fontWeight: '600',
  },
  topBarTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  canvasContainer: {
    flex: 1,
    position: 'relative',
    overflow: 'hidden',
    backgroundColor: '#F8FAFC',
  },
  particle: {
    position: 'absolute',
    top: 0,
    left: 0,
  },
});

export default WorkloadCScreen;
