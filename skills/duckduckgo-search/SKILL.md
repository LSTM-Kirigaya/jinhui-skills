---
name: duckduckgo-search
description: Integrate DuckDuckGo web search into a Rust project by calling Bing and DuckDuckGo HTTP APIs directly with browser fingerprint simulation. Use when building search functionality that needs text, news, image, or video results without relying on third-party CLI wrappers. Covers the primp HTTP client, vqd token extraction, Bing HTML parsing, DuckDuckGo JSON APIs, and cross-language HTTP concepts.
---

# DuckDuckGo Search via Direct HTTP (Rust)

Integrate DuckDuckGo search into a Rust application by calling HTTP endpoints directly, using `primp` for browser fingerprint simulation to bypass anti-bot measures.

## Why direct HTTP with primp?

- **No external CLI dependencies** — Pure Rust, no Python or `ddgs` CLI required
- **Browser fingerprint simulation** — `primp` mimics real Chrome/Firefox/Safari TLS and HTTP/2 signatures
- **Full control** — You own the request logic, retry strategy, and error handling
- **Performance** — Single binary, no process spawning overhead

## Architecture

```
┌─────────────┐     ┌─────────────────────┐     ┌──────────────────┐
|  User query |────▶|  primp::Client      |────▶|  Bing / DDG API  |
└─────────────┘     |  (with impersonate) |     └──────────────────┘
                    └─────────────────────┘              │
                              │                          ▼
                              ▼                   ┌──────────────┐
                        ┌──────────┐              |  HTML / JSON |
                        |  Parse   │◀─────────────└──────────────┘
                        |  results |
                        └──────────┘
```

**Text search** uses Bing HTML (`GET https://www.bing.com/search`).
**News / Videos / Images** use DuckDuckGo JSON APIs (`GET https://duckduckgo.com/*.js`) with a vqd token.
**Content extraction** uses `r.jina.ai` or DuckDuckGo extract.

## Prerequisites

Add to `Cargo.toml`:

```toml
[dependencies]
primp = "1.2"
reqwest = { version = "0.12", features = ["json", "cookies"] }
scraper = "0.22"
regex = "1"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
urlencoding = "2"
chrono = "0.4"
```

## Core implementation

### 1. Create the HTTP client

```rust
use primp::ClientBuilder;
use regex::Regex;

struct DdgClient {
    client: primp::Client,
    vqd_regex: Regex,
}

impl DdgClient {
    fn new() -> Result<Self, String> {
        let client = ClientBuilder::new()
            .impersonate(primp::Impersonate::Chrome)
            .timeout(Duration::from_secs(30))
            .connect_timeout(Duration::from_secs(15))
            .build()
            .map_err(|e| e.to_string())?;

        let vqd_regex = Regex::new(r#"vqd=["']?([\d-]+)["']?"#).unwrap();
        Ok(DdgClient { client, vqd_regex })
    }
}
```

`Impersonate::Chrome` (or `Random`) sets the TLS JA3 fingerprint, ALPN, HTTP/2 settings, and headers to match a real Chrome browser.

### 2. Obtain vqd token (required for DDG JSON APIs)

```rust
async fn get_vqd(&self, query: &str) -> Result<String, String> {
    let url = format!("https://duckduckgo.com?q={}", urlencoding::encode(query));
    let resp = self.client.get(&url).send().await
        .map_err(|e| format!("vqd request failed: {e}"))?;

    let body = resp.bytes().await.map_err(|e| e.to_string())?;

    if let Some(m) = self.vqd_regex.find(&String::from_utf8_lossy(&body)) {
        let matched = m.as_str();
        if let Some(val) = matched.strip_prefix("vqd=\"") {
            return Ok(val.trim_end_matches('"').to_string());
        }
        if let Some(val) = matched.strip_prefix("vqd=") {
            return Ok(val.to_string());
        }
    }

    Err("Could not extract vqd token".to_string())
}
```

### 3. Text search via Bing

Bing is more accessible than DuckDuckGo HTML in many network environments.

```rust
async fn text_search(&self, query: &str, max_results: usize) -> Result<Vec<SearchResult>, String> {
    let cookie_cd = "m=en-us&u=en-us";
    let cookie_s = "mkt=en-us&ui=en-us";

    let resp = self.client
        .get("https://www.bing.com/search")
        .header("Cookie", format!("_EDGE_CD={}; _EDGE_S={}", cookie_cd, cookie_s))
        .query(&[("q", query), ("pq", query), ("cc", "en")])
        .send()
        .await
        .map_err(|e| format!("Bing search failed: {e}"))?;

    let html = resp.text().await.map_err(|e| e.to_string())?;
    let document = Html::parse_document(&html);
    let item_selector = Selector::parse("li.b_algo").unwrap();

    let mut results = Vec::new();
    for item in document.select(&item_selector) {
        let href = item.select(&Selector::parse("h2 a").unwrap())
            .next()
            .and_then(|a| a.value().attr("href"))
            .map(|s| s.to_string());

        let title = item.select(&Selector::parse("h2 a").unwrap())
            .next()
            .map(|a| a.text().collect::<String>().trim().to_string())
            .unwrap_or_default();

        let body = item.select(&Selector::parse("p").unwrap())
            .next()
            .map(|p| p.text().collect::<String>().trim().to_string())
            .unwrap_or_default();

        let href = match href {
            Some(h) if h.starts_with("https://www.bing.com/ck/a?") => {
                unwrap_bing_url(&h).unwrap_or(h)
            }
            Some(h) => h,
            None => continue,
        };

        results.push(SearchResult { title, href, body });
        if results.len() >= max_results { break; }
    }

    Ok(results)
}
```

**Bing URL unwrapping:**

Bing wraps URLs in `https://www.bing.com/ck/a?u=a1...`. Decode with Base64 URL-safe:

```rust
fn unwrap_bing_url(raw_url: &str) -> Option<String> {
    let parsed = url::Url::parse(raw_url).ok()?;
    let u = parsed.query_pairs().find(|(k, _)| k == "u")?.1;
    if u.len() <= 2 { return None; }
    let b64_part = &u[2..];
    let padding = "=".repeat((-(b64_part.len() as i32)) as usize % 4);
    let decoded = base64::Engine::decode(
        &base64::engine::general_purpose::URL_SAFE,
        format!("{}{}", b64_part, padding),
    ).ok()?;
    String::from_utf8(decoded).ok()
}
```

### 4. DuckDuckGo JSON APIs (news / videos / images)

All require the vqd token obtained in step 2.

**News:**
```
GET https://duckduckgo.com/news.js
Params: l, o=json, noamp=1, q, vqd, p, df, s
```

**Videos:**
```
GET https://duckduckgo.com/v.js
Params: l, o=json, q, vqd, p, f, s
```

**Images:**
```
GET https://duckduckgo.com/i.js
Params: o=json, q, l, vqd, p, ct=AT, f, s
```

Common pattern:
```rust
async fn news_search(&self, query: &str, max_results: usize) -> Result<Vec<NewsResult>, String> {
    let vqd = self.get_vqd(query).await?;
    let mut params: Vec<(&str, String)> = vec![
        ("l", "us-en".to_string()),
        ("o", "json".to_string()),
        ("noamp", "1".to_string()),
        ("q", query.to_string()),
        ("vqd", vqd),
        ("p", "1".to_string()),
    ];

    let mut results = Vec::new();
    for _ in 0..5 {
        let resp = self.client
            .get("https://duckduckgo.com/news.js")
            .header("Referer", "https://duckduckgo.com/")
            .query(&params)
            .send()
            .await?;

        let json: serde_json::Value = resp.json().await?;
        let items = json.get("results").and_then(|r| r.as_array()).cloned().unwrap_or_default();

        for item in items {
            results.push(NewsResult {
                date: normalize_date(item.get("date")),
                title: item.get("title").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                body: item.get("excerpt").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                url: item.get("url").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                image: item.get("image").and_then(|v| v.as_str()).map(|s| s.to_string()),
                source: item.get("source").and_then(|v| v.as_str()).unwrap_or("").to_string(),
            });
            if results.len() >= max_results { return Ok(results); }
        }

        // Pagination
        if let Some(next) = json.get("next").and_then(|v| v.as_str()) {
            if let Some(s_val) = extract_query_param(next, "s") {
                params.retain(|(k, _)| *k != "s");
                params.push(("s", s_val));
            } else { break; }
        } else { break; }
    }

    Ok(results)
}
```

### 5. Web content extraction

Use `r.jina.ai` as a lightweight extraction service:

```rust
async fn extract(&self, url: &str) -> Result<ExtractResult, String> {
    let resp = self.client
        .get(format!("https://r.jina.ai/http://{}", url.trim_start_matches("https://").trim_start_matches("http://")))
        .send()
        .await
        .map_err(|e| format!("extract failed: {e}"))?;

    let text = resp.text().await.map_err(|e| e.to_string())?;
    Ok(ExtractResult { url: url.to_string(), content: text })
}
```

## Network environment considerations

| Endpoint | Accessibility | Fallback |
|----------|---------------|----------|
| Bing (`bing.com`) | Widely accessible | None needed for text |
| DuckDuckGo (`duckduckgo.com`) | Blocked in some regions | Skip images/videos/news |
| `r.jina.ai` | Widely accessible | Use `web_fetch` directly |

If DuckDuckGo is blocked:
- Text search still works via Bing
- Images/videos/news require vqd token (unavailable if duckduckgo.com is blocked)
- Consider SearXNG instances as additional fallback

## Anti-bot summary

| Measure | How `primp` handles it |
|---------|------------------------|
| TLS fingerprint (JA3/JA4) | `Impersonate::Chrome` mimics Chrome's TLS signature |
| HTTP/2 fingerprint | Correct SETTINGS frame, pseudo-header order, stream priorities |
| User-Agent | Real Chrome/Firefox/Safari UA string |
| Headers | Complete browser header set (Accept, Accept-Language, Sec-Fetch-*, etc.) |
| Cookie jar | `cookie_store(true)` or `ClientBuilder` default |

Without `primp`, plain `reqwest` will be blocked by Bing/DuckDuckGo anti-bot systems.

## Error handling

| Symptom | Cause | Action |
|---------|-------|--------|
| Empty results | Rate limited or fingerprint rejected | Retry with `Impersonate::Firefox` or `Random` |
| "Could not extract vqd" | DuckDuckGo blocked | Skip DDG APIs, use Bing only |
| Timeout | Network slow | Reduce `max_results`, add retry |
| `unwrap_bing_url` fails | Bing changed URL format | Log and return raw URL |

## References

- `references/duckduckgo-http-api.md` — Complete DuckDuckGo JSON/HTTP endpoint documentation (images, videos, news, suggestions, instant answers)
- `references/bing-text-search.md` — Bing HTML parsing, URL decoding, pagination, and cookie requirements
