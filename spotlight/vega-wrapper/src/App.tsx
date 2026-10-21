import {WebView} from '@amazon-devices/webview';
import * as React from 'react';
import {useRef} from 'react';
import {View, StyleSheet} from 'react-native';
import {
  useHideSplashScreenCallback,
  usePreventHideSplashScreen,
} from '@amazon-devices/react-native-kepler';
import {
  SslErrorData,
  WebViewErrorEvent,
  WebViewHttpErrorEvent,
  WebViewNavigationEvent,
} from '@amazon-devices/webview/dist/types/WebViewTypes';

export const App = () => {
  const webRef = useRef(null);
  const [currentUri, setCurrentUri] = React.useState("http://10.0.2.2:8000/tv");
  // By default splash screen is shown in app launch, as the splash
  // screen images are bundled in this app (assets/raw/ folder)
  // Declare that application wants to extend splash screen lifecycle
  usePreventHideSplashScreen();
  const hideSplashScreenCallback = useHideSplashScreenCallback();
  return (
    <View style={styles.container}>
      <WebView
        ref={webRef}
        style={styles.webview}
        allowSystemKeyEvents={true}
        allowsDefaultMediaControl={true}
        domStorageEnabled={true}
        hasTVPreferredFocus={true}
        javaScriptEnabled={true}
        mediaPlaybackRequiresUserAction={false}
        mixedContentMode="compatibility"
        source={{
          uri: currentUri,
        }}
        onLoad={(_event: WebViewNavigationEvent) => {
          console.info('Page loading completed...');
          // Hide the splash screen
          hideSplashScreenCallback();
        }}
        onLoadStart={(_event: WebViewNavigationEvent) => {
          console.info('Page loading started...');
        }}
        onError={({
          nativeEvent: {code, url, description},
        }: WebViewErrorEvent) => {
          console.error(`[onError]: (${code}: ${url}) ${description}`);
          // If the emulator host gateway 10.0.2.2 fails, fallback to host LAN IP
          if (currentUri.includes("10.0.2.2")) {
            console.warn("Retrying with host IP 192.168.222.77:8000/tv...");
            setCurrentUri("http://192.168.222.77:8000/tv");
          }
        }}
        onHttpError={({
          nativeEvent: {url, statusCode: code, description, isMainFrame},
        }: WebViewHttpErrorEvent) => {
          console.error(`[onHttpError]: (${code}: ${url}) ${description}`);
          console.error(`[onHttpError]: isMainFrame: ${isMainFrame}`);
        }}
        onSslError={({code, url, description}: SslErrorData) => {
          console.error(`[onSslError]: (${code}: ${url}) ${description}`);
        }}
      />
    </View>
  );
};

// Styles for layout, which are necessary for proper focus behavior
const styles = StyleSheet.create({
  container: {flex: 1},
  webview: {backgroundColor: '#000000'},
});
