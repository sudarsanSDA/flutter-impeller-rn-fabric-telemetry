import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';

/** Props for the HubScreen component. */
interface HubScreenProps {
  onNavigate: (screen: 'workload_a' | 'workload_b' | 'workload_c') => void;
}

/** Screen 0: Landing menu for cold-start latency testing. */
export const HubScreen: React.FC<HubScreenProps> = ({ onNavigate }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.headerTitle}>Benchmark Hub</Text>
      <View style={styles.buttonContainer}>
        <Pressable
          testID="btn_workload_a"
          style={styles.button}
          onPress={() => onNavigate('workload_a')}>
          <Text style={styles.buttonText}>Workload A: Virtualized List</Text>
        </Pressable>

        <Pressable
          testID="btn_workload_b"
          style={styles.button}
          onPress={() => onNavigate('workload_b')}>
          <Text style={styles.buttonText}>Workload B: JSON Deserialization</Text>
        </Pressable>

        <Pressable
          testID="btn_workload_c"
          style={styles.button}
          onPress={() => onNavigate('workload_c')}>
          <Text style={styles.buttonText}>Workload C: Canvas Animation</Text>
        </Pressable>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 32,
    color: '#1F2937',
  },
  buttonContainer: {
    gap: 16,
  },
  button: {
    backgroundColor: '#2563EB',
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
