import React, { useState, useEffect } from 'react';
import { BackHandler, SafeAreaView, StatusBar, StyleSheet } from 'react-native';
import { HubScreen } from './src/screens/HubScreen';
import { WorkloadAScreen } from './src/screens/WorkloadAScreen';
import { WorkloadBScreen } from './src/screens/WorkloadBScreen';
import { WorkloadCScreen } from './src/screens/WorkloadCScreen';

type ScreenName = 'hub' | 'workload_a' | 'workload_b' | 'workload_c';

/** Root benchmark application component managing active screen state via core useState. */
function App(): React.JSX.Element {
  const [currentScreen, setCurrentScreen] = useState<ScreenName>('hub');

  useEffect(() => {
    if (!BackHandler || typeof BackHandler.addEventListener !== 'function') {
      return;
    }

    const backAction = () => {
      if (currentScreen !== 'hub') {
        setCurrentScreen('hub');
        return true;
      }
      return false;
    };

    const backHandler = BackHandler.addEventListener('hardwareBackPress', backAction);
    return () => backHandler?.remove?.();
  }, [currentScreen]);

  return (
    <SafeAreaView style={styles.root}>
      <StatusBar barStyle="dark-content" backgroundColor="#F9FAFB" />
      {currentScreen === 'hub' && (
        <HubScreen onNavigate={screen => setCurrentScreen(screen)} />
      )}
      {currentScreen === 'workload_a' && (
        <WorkloadAScreen onBack={() => setCurrentScreen('hub')} />
      )}
      {currentScreen === 'workload_b' && (
        <WorkloadBScreen onBack={() => setCurrentScreen('hub')} />
      )}
      {currentScreen === 'workload_c' && (
        <WorkloadCScreen onBack={() => setCurrentScreen('hub')} />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
});

export default App;
