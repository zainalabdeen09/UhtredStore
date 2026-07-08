# ProGuard rules for Uhtred Store

# Keep Chaquopy Python classes
-keep class com.chaquo.python.** { *; }

# Keep WebView
-keepclassmembers class * extends android.webkit.WebView {
    public *;
}

# Keep all Python bridge classes
-keep class com.uhtred.store.** { *; }

# Keep JavaScript interface methods
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
