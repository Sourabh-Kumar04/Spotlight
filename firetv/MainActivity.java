package com.spotlight.firetv;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.view.KeyEvent;

/**
 * SPOTLIGHT Fire TV wrapper — full-screen WebView hosting the SPOTLIGHT web app.
 * D-pad keys are passed through to the page (the TV UI handles arrow-key focus).
 */
public class MainActivity extends Activity {
    // Point at your hosted SPOTLIGHT instance (or 10.0.2.2 for the emulator host loopback)
    private static final String SPOTLIGHT_URL = "http://10.0.2.2:8000/tv";

    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        webView.setWebViewClient(new WebViewClient());
        setContentView(webView);
        String url = getIntent().getStringExtra("spotlight_url");
        webView.loadUrl(url != null ? url : SPOTLIGHT_URL);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        // Let the WebView handle D-pad navigation natively
        return super.onKeyDown(keyCode, event);
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }
}
