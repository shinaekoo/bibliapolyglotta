package kr.bible.originalis;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowInsets;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.IOException;
import java.io.InputStream;

/** Shows the bundled web app (assets/index.html + assets/data) in a WebView. */
public class MainActivity extends Activity {
    private static final String HOST = "appassets.androidplatform.net";
    private static final String START = "https://" + HOST + "/index.html";
    private WebView web;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        web = new WebView(this);
        web.setBackgroundColor(getColor(R.color.bg));
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setTextZoom(100);
        web.setWebViewClient(new Client());

        // Android 15+ draws edge-to-edge: keep content clear of the status and navigation bars.
        web.setOnApplyWindowInsetsListener((v, insets) -> {
            int l, t, r, b;
            if (Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets i = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout() | WindowInsets.Type.ime());
                l = i.left; t = i.top; r = i.right; b = i.bottom;
            } else {
                l = insets.getSystemWindowInsetLeft(); t = insets.getSystemWindowInsetTop();
                r = insets.getSystemWindowInsetRight(); b = insets.getSystemWindowInsetBottom();
            }
            v.setPadding(l, t, r, b);
            return insets;
        });

        setContentView(web);
        // Back key: go back inside the page history first (Android 13+ uses the new back callback).
        if (Build.VERSION.SDK_INT >= 33) {
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                    android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT,
                    () -> { if (web.canGoBack()) web.goBack(); else finish(); });
        }
        if (state != null) web.restoreState(state);
        else web.loadUrl(START);
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    private class Client extends WebViewClient {
        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
            Uri u = req.getUrl();
            if (!HOST.equals(u.getHost())) return null;
            String path = u.getPath();
            if (path == null || path.equals("/")) path = "/index.html";
            try {
                InputStream in = getAssets().open(path.substring(1));
                String mime = path.endsWith(".json") ? "application/json"
                        : path.endsWith(".js") ? "text/javascript"
                        : path.endsWith(".css") ? "text/css"
                        : path.endsWith(".png") ? "image/png" : "text/html";
                return new WebResourceResponse(mime, "utf-8", in);
            } catch (IOException e) {
                return new WebResourceResponse("text/plain", "utf-8", 404, "Not Found", null, null);
            }
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
            Uri u = req.getUrl();
            if (HOST.equals(u.getHost())) return false;
            try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception ignored) { }
            return true;
        }
    }
}
