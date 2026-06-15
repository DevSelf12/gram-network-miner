// Cloudflare Worker — Gram Network API Proxy (all endpoints)
// Deploy: https://dash.cloudflare.com → Workers & Pages → Create → Paste code → Deploy

export default {
  async fetch(request, env) {
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);
    const path = url.pathname;  // e.g. /get_user_data.php or /start_mining.php

    // Only allow known endpoints
    const allowed = ["/get_user_data.php", "/start_mining.php", "/claim_mining.php", "/claim_daily.php"];
    if (!allowed.includes(path) && path !== "/") {
      return new Response(
        JSON.stringify({ success: false, message: "Unknown endpoint" }),
        { status: 404, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    // Root — health check
    if (path === "/") {
      return new Response(
        JSON.stringify({ status: "ok", endpoints: allowed }),
        { headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    // Get initData
    let initData;
    if (request.method === "GET") {
      initData = url.searchParams.get("initData");
    } else {
      const body = await request.text();
      const params = new URLSearchParams(body);
      initData = params.get("initData");
    }

    if (!initData) {
      return new Response(
        JSON.stringify({ success: false, message: "Missing initData" }),
        { status: 400, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }

    // Forward to Gram Network
    const targetUrl = `https://app.gramnetwork.online/api${path}?initData=${encodeURIComponent(initData)}`;
    const method = request.method === "POST" ? "POST" : "GET";

    try {
      const resp = await fetch(targetUrl, {
        method,
        headers: {
          "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
          "Accept": "application/json",
          "Origin": "https://app.gramnetwork.online",
          "Referer": "https://app.gramnetwork.online/",
          ...(method === "POST" ? { "Content-Type": "application/x-www-form-urlencoded" } : {}),
        },
        ...(method === "POST" ? { body: `initData=${encodeURIComponent(initData)}` } : {}),
      });

      const body = await resp.text();
      return new Response(body, {
        status: resp.status,
        headers: { "Content-Type": "application/json", ...corsHeaders },
      });
    } catch (e) {
      return new Response(
        JSON.stringify({ success: false, message: e.message }),
        { status: 502, headers: { "Content-Type": "application/json", ...corsHeaders } }
      );
    }
  },
};
