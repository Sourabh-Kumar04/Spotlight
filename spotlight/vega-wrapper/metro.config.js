const path = require('path');
const fs = require('fs');
const {getDefaultConfig, mergeConfig} = require('@react-native/metro-config');

const extraNodeModules = path.resolve(__dirname, 'node_modules');
const realNodeModules = fs.existsSync(extraNodeModules) ? fs.realpathSync(extraNodeModules) : extraNodeModules;

const config = {
  watchFolders: [extraNodeModules, realNodeModules],
  resolver: {
    nodeModulesPaths: [extraNodeModules, realNodeModules],
    extraNodeModules: {
      'react-native': path.resolve(realNodeModules, 'react-native'),
      'react': path.resolve(realNodeModules, 'react'),
      '@amazon-devices/webview': path.resolve(realNodeModules, '@amazon-devices/webview'),
      '@amazon-devices/react-native-kepler': path.resolve(realNodeModules, '@amazon-devices/react-native-kepler'),
    },
  },
};
 
module.exports = mergeConfig(getDefaultConfig(__dirname), config);