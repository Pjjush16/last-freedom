package com.chasegame;

import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

public class TileInterceptorClient extends WebViewClient {

    @Override
    public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
        String url = request.getUrl().toString();
        if (url.contains("tianditu.gov.cn")) {
            try {
                URL tileUrl = new URL(url);
                HttpURLConnection conn = (HttpURLConnection) tileUrl.openConnection();
                conn.setRequestProperty("User-Agent", "ChaseGame/2.0");
                conn.setConnectTimeout(10000);
                conn.setReadTimeout(15000);
                int code = conn.getResponseCode();
                if (code == 200) {
                    InputStream is = conn.getInputStream();
                    String contentType = conn.getContentType();
                    if (contentType == null) contentType = "image/jpeg";
                    Map<String, String> headers = new HashMap<String, String>();
                    headers.put("Access-Control-Allow-Origin", "*");
                    return new WebResourceResponse(contentType, "UTF-8", code, "OK", headers, is);
                }
            } catch (Exception e) {
                // Fall through to default
            }
        }
        return super.shouldInterceptRequest(view, request);
    }
}
