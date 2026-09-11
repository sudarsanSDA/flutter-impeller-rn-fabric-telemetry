import 'react-native';
import React from 'react';
import { it, expect } from '@jest/globals';
import renderer from 'react-test-renderer';
import { HubScreen } from '../src/screens/HubScreen';
import { WorkloadAScreen } from '../src/screens/WorkloadAScreen';
import { WorkloadBScreen } from '../src/screens/WorkloadBScreen';
import { WorkloadCScreen } from '../src/screens/WorkloadCScreen';

it('renders HubScreen correctly', () => {
  const tree = renderer.create(<HubScreen onNavigate={() => {}} />).toJSON();
  expect(tree).toBeDefined();
});

it('renders WorkloadAScreen correctly', () => {
  const tree = renderer.create(<WorkloadAScreen onBack={() => {}} />).toJSON();
  expect(tree).toBeDefined();
});

it('renders WorkloadBScreen correctly', () => {
  const tree = renderer.create(<WorkloadBScreen onBack={() => {}} />).toJSON();
  expect(tree).toBeDefined();
});

it('renders WorkloadCScreen correctly', () => {
  const tree = renderer.create(<WorkloadCScreen onBack={() => {}} autoPlay={false} />).toJSON();
  expect(tree).toBeDefined();
});
