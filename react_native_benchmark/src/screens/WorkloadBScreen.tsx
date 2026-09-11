import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { BenchmarkRecord } from '../types/benchmark';

/** Props for WorkloadBScreen. */
interface WorkloadBScreenProps {
  onBack: () => void;
}

/** Pre-loaded raw payload string to benchmark deserialization and computation. */
const rawPayloadString: string = JSON.stringify(
  require('../../assets/data/payload_10k.json'),
);

/** Screen 2: Workload B measuring CPU parsing, sorting, and score aggregation on Hermes. */
export const WorkloadBScreen: React.FC<WorkloadBScreenProps> = ({ onBack }) => {
  const [duration, setDuration] = useState<string>('');
  const [scoreSum, setScoreSum] = useState<string>('');
  const [processing, setProcessing] = useState<boolean>(false);

  /** Executes deserialization, timestamp sorting, and score summation. */
  const executeBenchmark = () => {
    setProcessing(true);

    // Defer slightly to ensure UI renders loading indicator
    setTimeout(() => {
      const startTime = performance.now();

      // 1. Deserialization
      const records: BenchmarkRecord[] = JSON.parse(rawPayloadString);

      // 2. Sort descending by ISO-8601 timestamp
      records.sort((a, b) => (b.timestamp > a.timestamp ? 1 : b.timestamp < a.timestamp ? -1 : 0));

      // 3. Sum numeric metrics.score across dataset
      let sum = 0;
      const len = records.length;
      for (let i = 0; i < len; i++) {
        sum += records[i].metrics.score;
      }

      const endTime = performance.now();
      const elapsedMs = Math.round(endTime - startTime);

      setDuration(`${elapsedMs} ms`);
      setScoreSum(sum.toFixed(4));
      setProcessing(false);
    }, 16);
  };

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <Pressable onPress={onBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>Back</Text>
        </Pressable>
        <Text style={styles.topBarTitle}>Workload B: JSON Deserialization</Text>
      </View>

      <ScrollView contentContainerStyle={styles.contentContainer}>
        <Pressable
          testID="btn_execute_benchmark"
          style={[styles.actionButton, processing && styles.actionButtonDisabled]}
          onPress={executeBenchmark}
          disabled={processing}>
          {processing ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.actionButtonText}>Execute Benchmark</Text>
          )}
        </Pressable>

        <View style={styles.fieldGroup}>
          <Text style={styles.fieldLabel}>Hermes Execution Duration</Text>
          <TextInput
            testID="txt_duration"
            style={styles.textInput}
            value={duration}
            editable={false}
            placeholder="Awaiting execution..."
            placeholderTextColor="#9CA3AF"
          />
        </View>

        <View style={styles.fieldGroup}>
          <Text style={styles.fieldLabel}>Aggregated Score Sum</Text>
          <TextInput
            testID="txt_score_sum"
            style={styles.textInput}
            value={scoreSum}
            editable={false}
            placeholder="Awaiting execution..."
            placeholderTextColor="#9CA3AF"
          />
        </View>
      </ScrollView>
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
  contentContainer: {
    padding: 24,
  },
  actionButton: {
    backgroundColor: '#2563EB',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 24,
  },
  actionButtonDisabled: {
    backgroundColor: '#93C5FD',
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  fieldGroup: {
    marginBottom: 16,
  },
  fieldLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 6,
  },
  textInput: {
    height: 48,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 14,
    fontSize: 16,
    backgroundColor: '#F9FAFB',
    color: '#111827',
  },
});
