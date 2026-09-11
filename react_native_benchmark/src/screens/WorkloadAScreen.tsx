import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  Image,
  StyleSheet,
  ActivityIndicator,
  Pressable,
} from 'react-native';
import { ListItem } from '../types/benchmark';

/** Fixed row height in density-independent pixels. */
const ITEM_HEIGHT = 72;

/** Props for WorkloadAScreen. */
interface WorkloadAScreenProps {
  onBack: () => void;
}

/** Screen 1: Workload A executing FlatList virtualization with 5,000 items. */
export const WorkloadAScreen: React.FC<WorkloadAScreenProps> = ({ onBack }) => {
  const [items, setItems] = useState<ListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    /** Loads static mock dataset into state once on mount. */
    const loadData = () => {
      const dataset: ListItem[] = require('../../assets/data/list_5k.json');
      setItems(dataset);
      setLoading(false);
    };

    loadData();
  }, []);

  const getItemLayout = useCallback(
    (_data: ArrayLike<ListItem> | null | undefined, index: number) => ({
      length: ITEM_HEIGHT,
      offset: ITEM_HEIGHT * index,
      index,
    }),
    [],
  );

  const renderItem = useCallback(({ item }: { item: ListItem }) => {
    return (
      <View style={styles.row}>
        <View style={styles.avatarContainer}>
          <Image
            source={require('../../assets/images/avatar.png')}
            style={styles.avatar}
            resizeMode="cover"
          />
        </View>

        <View style={styles.textColumn}>
          <Text style={styles.title} numberOfLines={1}>
            {item.title}
          </Text>
          <Text style={styles.subtitle} numberOfLines={1} ellipsizeMode="tail">
            {item.subtitle}
          </Text>
        </View>

        <View style={styles.badgeContainer}>
          <Text style={styles.badgeText}>{item.badge_count}</Text>
        </View>
      </View>
    );
  }, []);

  const keyExtractor = useCallback((item: ListItem) => item.id.toString(), []);

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <Pressable onPress={onBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>Back</Text>
        </Pressable>
        <Text style={styles.topBarTitle}>Workload A: Virtualized List</Text>
      </View>

      {loading ? (
        <View style={styles.centered}>
          <ActivityIndicator size="large" color="#2563EB" />
        </View>
      ) : (
        <FlatList
          testID="virtualized_flat_list"
          data={items}
          renderItem={renderItem}
          keyExtractor={keyExtractor}
          getItemLayout={getItemLayout}
          windowSize={5}
          maxToRenderPerBatch={10}
          removeClippedSubviews={true}
          initialNumToRender={15}
        />
      )}
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
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  row: {
    height: ITEM_HEIGHT,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#EEEEEE',
  },
  avatarContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    overflow: 'hidden',
    backgroundColor: '#E5E7EB',
  },
  avatar: {
    width: 40,
    height: 40,
  },
  textColumn: {
    flex: 1,
    marginLeft: 12,
    marginRight: 12,
    justifyContent: 'center',
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  badgeContainer: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#CFD8DC',
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#263238',
  },
});
