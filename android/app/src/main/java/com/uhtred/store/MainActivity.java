package com.uhtred.store;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;
import android.widget.FrameLayout;

import androidx.appcompat.app.AppCompatActivity;

import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.io.File;
import java.net.HttpURLConnection;
import java.net.URL;

public class MainActivity extends AppCompatActivity {

    private WebView webView;
    private ProgressBar progressBar;
    private FrameLayout loadingLayout;
    private Handler handler = new Handler(Looper.getMainLooper());
    private boolean serverReady = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);
        loadingLayout = findViewById(R.id.loadingLayout);

        setupWebView();
        startFlaskServer();
    }

    private void setupWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setCacheMode(WebSettings.LOAD_NO_CACHE);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        settings.setLayoutAlgorithm(WebSettings.LayoutAlgorithm.NARROW_COLUMNS);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setDefaultTextEncodingName("utf-8");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                if (serverReady) {
                    loadingLayout.setVisibility(View.GONE);
                    webView.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                super.onReceivedError(view, errorCode, description, failingUrl);
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                if (progressBar != null) {
                    progressBar.setProgress(newProgress);
                    progressBar.setVisibility(newProgress < 100 ? View.VISIBLE : View.GONE);
                }
            }
        });
    }

    private void startFlaskServer() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    if (!Python.isStarted()) {
                        Python.start(new AndroidPlatform(MainActivity.this));
                    }

                    Python py = Python.getInstance();
                    py.getModule("flask_launcher").callAttr("start_server",
                            getApplicationInfo().dataDir);

                    waitForServer();

                    handler.post(new Runnable() {
                        @Override
                        public void run() {
                            serverReady = true;
                            webView.loadUrl("http://127.0.0.1:5000");
                        }
                    });
                } catch (final Exception e) {
                    handler.post(new Runnable() {
                        @Override
                        public void run() {
                            loadingLayout.setVisibility(View.GONE);
                            webView.setVisibility(View.VISIBLE);
                            webView.loadDataWithBaseURL(null,
                                    "<html dir='rtl'><body style='background:#0f172a;color:#ef4444;padding:40px;text-align:center;font-family:sans-serif;margin-top:80px'>" +
                                    "<h1>خطأ في تشغيل الخادم</h1><p>" + e.getMessage() + "</p></body></html>",
                                    "text/html", "utf-8", null);
                        }
                    });
                }
            }
        }).start();
    }

    private void waitForServer() {
        int attempts = 0;
        int maxAttempts = 60;
        while (attempts < maxAttempts) {
            try {
                URL url = new URL("http://127.0.0.1:5000");
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setConnectTimeout(500);
                connection.setReadTimeout(500);
                connection.setRequestMethod("GET");
                int responseCode = connection.getResponseCode();
                connection.disconnect();
                if (responseCode == 200) {
                    return;
                }
            } catch (Exception e) {
                try {
                    Thread.sleep(500);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return;
                }
                attempts++;
            }
        }
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (webView != null) {
            webView.destroy();
        }
    }
}
