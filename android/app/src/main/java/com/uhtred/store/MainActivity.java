package com.uhtred.store;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.net.Uri;
import android.webkit.MimeTypeMap;

import java.io.File;
import java.io.FileOutputStream;

public class MainActivity extends AppCompatActivity {

    private WebView webView;
    private ProgressBar progressBar;
    private String serverUrl = "";
    private boolean doubleBackToExit = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);

        SharedPreferences prefs = getSharedPreferences("uhtred_prefs", MODE_PRIVATE);
        serverUrl = prefs.getString("server_url", "");

        if (serverUrl.isEmpty()) {
            showSettingsDialog();
            return;
        }

        setupWebView();
        webView.loadUrl(serverUrl);
    }

    private void setupWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setCacheMode(WebSettings.LOAD_NO_CACHE);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setDefaultTextEncodingName("utf-8");
        settings.setUserAgentString("UhtredStore-Android");

        webView.addJavascriptInterface(new WebAppInterface(), "Android");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                if (url.startsWith(serverUrl) || url.startsWith("http://127.0.0.1") || url.startsWith("http://localhost")) {
                    view.loadUrl(url);
                    return true;
                }
                if (url.startsWith("http://") || url.startsWith("https://")) {
                    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                    startActivity(intent);
                    return true;
                }
                return false;
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                progressBar.setVisibility(android.view.View.GONE);
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                if (newProgress < 100) {
                    progressBar.setVisibility(android.view.View.VISIBLE);
                    progressBar.setProgress(newProgress);
                } else {
                    progressBar.setVisibility(android.view.View.GONE);
                }
            }
        });
    }

    private void showSettingsDialog() {
        androidx.appcompat.app.AlertDialog.Builder builder = new AlertDialog.Builder(this, R.style.AppTheme);
        builder.setTitle("إعدادات الاتصال");
        builder.setMessage("أدخل عنوان IP الخاص بالحاسوب:\n(مثال: 192.168.1.100)");

        final android.widget.EditText input = new android.widget.EditText(this);
        input.setInputType(android.text.InputType.TYPE_CLASS_PHONE);
        input.setHint("192.168.1.100");
        input.setTextDirection(android.view.View.TEXT_DIRECTION_LTR);
        builder.setView(input);

        builder.setPositiveButton("اتصال", (dialog, which) -> {
            String ip = input.getText().toString().trim();
            if (!ip.isEmpty()) {
                String url = "http://" + ip + ":5000";
                serverUrl = url;
                SharedPreferences prefs = getSharedPreferences("uhtred_prefs", MODE_PRIVATE);
                prefs.edit().putString("server_url", url).apply();
                setupWebView();
                webView.loadUrl(url);
            }
        });

        builder.setNegativeButton("خروج", (dialog, which) -> finish());

        builder.setCancelable(false);
        builder.show();
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            if (doubleBackToExit) {
                super.onBackPressed();
                return;
            }
            doubleBackToExit = true;
            Toast.makeText(this, "اضغط مرة أخرى للخروج", Toast.LENGTH_SHORT).show();
            new Handler().postDelayed(() -> doubleBackToExit = false, 2000);
        }
    }

    private class WebAppInterface {
        @JavascriptInterface
        public void saveFile(String filename, String base64Data, String mimeType) {
            try {
                byte[] data = android.util.Base64.decode(base64Data, android.util.Base64.DEFAULT);
                File downloadsDir = android.os.Environment.getExternalStoragePublicDirectory(
                        android.os.Environment.DIRECTORY_DOWNLOADS);
                File file = new File(downloadsDir, filename);
                FileOutputStream fos = new FileOutputStream(file);
                fos.write(data);
                fos.close();

                Intent scanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
                scanIntent.setData(Uri.fromFile(file));
                sendBroadcast(scanIntent);

                runOnUiThread(() -> Toast.makeText(MainActivity.this,
                        "تم حفظ الملف: " + file.getAbsolutePath(), Toast.LENGTH_LONG).show());
            } catch (Exception e) {
                runOnUiThread(() -> Toast.makeText(MainActivity.this,
                        "خطأ في حفظ الملف: " + e.getMessage(), Toast.LENGTH_LONG).show());
            }
        }

        @JavascriptInterface
        public void shareFile(String filename, String base64Data, String mimeType) {
            try {
                byte[] data = android.util.Base64.decode(base64Data, android.util.Base64.DEFAULT);
                File cacheDir = getCacheDir();
                File file = new File(cacheDir, filename);
                FileOutputStream fos = new FileOutputStream(file);
                fos.write(data);
                fos.close();

                Uri uri = androidx.core.content.FileProvider.getUriForFile(
                        MainActivity.this, "com.uhtred.store.fileprovider", file);

                Intent shareIntent = new Intent(Intent.ACTION_SEND);
                shareIntent.setType(mimeType);
                shareIntent.putExtra(Intent.EXTRA_STREAM, uri);
                shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                startActivity(Intent.createChooser(shareIntent, "مشاركة الملف"));
            } catch (Exception e) {
                runOnUiThread(() -> Toast.makeText(MainActivity.this,
                        "خطأ في المشاركة: " + e.getMessage(), Toast.LENGTH_LONG).show());
            }
        }

        @JavascriptInterface
        public int getAndroidVersion() {
            return android.os.Build.VERSION.SDK_INT;
        }
    }
}
