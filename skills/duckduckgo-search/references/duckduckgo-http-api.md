# DuckDuckGo HTTP API Reference

> **Implementation note:** This document describes the HTTP protocol between client and server. The actual Rust implementation uses `primp::Client` with `Impersonate::Chrome` (or `Random`) to send these requests with browser fingerprint simulation, which is required to bypass anti-bot checks on DuckDuckGo and Bing.

DuckDuckGo does not publish an official search API. The endpoints below are reverse-engineered from its web interface and the `duckduckgo-search` Python library.

**Base URLs:**
- `https://duckduckgo.com` — vqd token acquisition, images, videos, news, answers
- `https://html.duckduckgo.com` — text search HTML endpoint
- `https://lite.duckduckgo.com` — text search lite endpoint

---

## 1. vqd Token Acquisition

The `vqd` token is required for all JSON APIs (images, videos, news).

```
GET https://duckduckgo.com?q={url_encoded_query}
```

### Request headers

```
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
```

### Response

Returns an HTML page. Extract `vqd` using regex:

| Pattern | Example match |
|---------|---------------|
| `vqd="([\d-]+)"` | `vqd="12345678901234567"` |
| `vqd=([\d-]+)` | `vqd=12345678901234567` |
| `vqd:"([\d-]+)"` | `vqd:"12345678901234567"` |

**Note:** If the request times out or returns non-200, DuckDuckGo may be blocked in your network. Use Bing text search as fallback.

---

## 2. Images Search

```
GET https://duckduckgo.com/i.js
```

### Query parameters

| Param | Required | Description | Example |
|-------|----------|-------------|---------|
| `o` | Yes | Output format | `json` |
| `q` | Yes | Search query | `cute cats` |
| `l` | Yes | Region | `us-en`, `cn-zh`, `wt-wt` |
| `vqd` | Yes | vqd token from step 1 | `12345678901234567` |
| `p` | Yes | Safe search | `1` (on/moderate), `-1` (off) |
| `f` | No | Filter string (comma-separated) | `time:Day,size:Medium,color:Red` |
| `s` | No | Pagination offset | `100` |

### Filter components for `f`

Build the filter string by joining non-empty segments with commas:

| Segment | Values |
|---------|--------|
| `time:{value}` | `Day`, `Week`, `Month`, `Year` |
| `size:{value}` | `Small`, `Medium`, `Large`, `Wallpaper` |
| `color:{value}` | `color`, `Monochrome`, `Red`, `Orange`, `Yellow`, `Green`, `Blue`, `Purple`, `Pink`, `Brown`, `Black`, `Gray`, `Teal`, `White` |
| `type:{value}` | `photo`, `clipart`, `gif`, `transparent`, `line` |
| `layout:{value}` | `Square`, `Tall`, `Wide` |
| `license:{value}` | `any`, `Public`, `Share`, `ShareCommercially`, `Modify`, `ModifyCommercially` |

Example: `f=time:Week,size:Medium,type:photo`

### Response

```json
{
  "results": [
    {
      "title": "Cute Cat",
      "image": "https://example.com/full.jpg",
      "thumbnail": "https://example.com/thumb.jpg",
      "url": "https://example.com/page",
      "height": 1080,
      "width": 1920,
      "source": "Bing"
    }
  ],
  "next": "https://duckduckgo.com/i.js?o=json&q=cute+cats&s=100"
}
```

### Response fields

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | Image results |
| `results[].title` | string | Image title |
| `results[].image` | string | Full-resolution image URL |
| `results[].thumbnail` | string | Thumbnail URL |
| `results[].url` | string | Source page URL |
| `results[].height` | integer | Image height |
| `results[].width` | integer | Image width |
| `results[].source` | string | Provider |
| `next` | string \| null | Next page URL fragment (extract `s` param for pagination) |

---

## 3. Videos Search

```
GET https://duckduckgo.com/v.js
```

### Query parameters

| Param | Required | Description | Example |
|-------|----------|-------------|---------|
| `l` | Yes | Region | `us-en` |
| `o` | Yes | Output format | `json` |
| `q` | Yes | Search query | `python tutorial` |
| `vqd` | Yes | vqd token | `12345678901234567` |
| `p` | Yes | Safe search | `1` (on), `-1` (moderate), `-2` (off) |
| `f` | No | Filter string | `publishedAfter:d,videoDefinition:high` |
| `s` | No | Pagination offset | `50` |

### Filter components for `f`

| Segment | Values |
|---------|--------|
| `publishedAfter:{value}` | `d` (day), `w` (week), `m` (month) |
| `videoDefinition:{value}` | `high`, `standard` |
| `videoDuration:{value}` | `short`, `medium`, `long` |
| `videoLicense:{value}` | `creativeCommon`, `youtube` |

Example: `f=publishedAfter:w,videoDuration:medium`

### Response

```json
{
  "results": [
    {
      "title": "Learn Python - Full Course",
      "content": "https://www.youtube.com/watch?v=rfscVS0vtbw",
      "description": "This course will give you a full introduction...",
      "duration": "4:26:52",
      "embed_html": "<iframe ...></iframe>",
      "embed_url": "https://www.youtube.com/embed/rfscVS0vtbw?autoplay=1",
      "image_token": "abc123...",
      "images": {
        "large": "https://tse1.mm.bing.net/th/id/OVP...",
        "medium": "https://tse1.mm.bing.net/th/id/OVP...",
        "motion": "https://tse2.mm.bing.net/th/id/OM...",
        "small": "https://tse1.mm.bing.net/th/id/OVP..."
      },
      "provider": "Bing",
      "published": "2018-07-11T18:00:42.0000000",
      "publisher": "YouTube",
      "statistics": { "viewCount": 48629843 },
      "uploader": "freeCodeCamp.org"
    }
  ],
  "next": "https://duckduckgo.com/v.js?l=us-en&o=json&q=...&s=50"
}
```

### Response fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Video title |
| `content` | string | Direct video URL |
| `description` | string | Video description |
| `duration` | string | Duration (`H:MM:SS` or `M:SS`) |
| `embed_html` | string | HTML iframe snippet |
| `embed_url` | string | Embeddable player URL |
| `image_token` | string | Internal image identifier |
| `images` | object | Thumbnails: `large`, `medium`, `motion`, `small` |
| `provider` | string | Search provider |
| `published` | string (ISO 8601) | Publication date |
| `publisher` | string | Platform name |
| `statistics` | object | `{ viewCount: integer }` |
| `uploader` | string | Channel/creator name |
| `next` | string \| null | Pagination URL |

---

## 4. News Search

```
GET https://duckduckgo.com/news.js
```

### Query parameters

| Param | Required | Description | Example |
|-------|----------|-------------|---------|
| `l` | Yes | Region | `us-en` |
| `o` | Yes | Output format | `json` |
| `noamp` | Yes | Disable AMP | `1` |
| `q` | Yes | Search query | `AI technology` |
| `vqd` | Yes | vqd token | `12345678901234567` |
| `p` | Yes | Safe search | `1` (on), `-1` (moderate), `-2` (off) |
| `df` | No | Time filter | `d`, `w`, `m` |
| `s` | No | Pagination offset | `15` |

### Response

```json
{
  "results": [
    {
      "date": 1714210581,
      "title": "China orders Meta to unwind...",
      "excerpt": "BEIJING/SINGAPORE, April 27...",
      "url": "https://www.msn.com/...",
      "image": "https://www.reuters.com/...",
      "source": "Reuters"
    }
  ],
  "next": "https://duckduckgo.com/news.js?l=us-en&o=json&noamp=1&q=...&s=15"
}
```

### Response fields

| Field | Type | Description |
|-------|------|-------------|
| `date` | integer (Unix timestamp) | Publication date. Convert to ISO 8601: `new Date(date * 1000).toISOString()` |
| `title` | string | Article headline |
| `excerpt` | string | Article excerpt/summary |
| `url` | string | Article URL |
| `image` | string \| null | Featured image URL |
| `source` | string | Publisher name |
| `next` | string \| null | Pagination URL |

---

## 5. Answers (Instant Answers)

```
GET https://duckduckgo.com
```

The answers are embedded in the initial HTML response (same request used for vqd token extraction). Look for structured data in the page HTML rather than a separate JSON endpoint.

Alternative: Some DuckDuckGo clients parse the API response at `https://duckduckgo.com/html/?q={query}` and extract the "Instant Answer" box from the HTML.

---

## 6. Suggestions

```
GET https://duckduckgo.com/ac/
```

### Query parameters

| Param | Required | Description | Example |
|-------|----------|-------------|---------|
| `q` | Yes | Partial query | `pyth` |
| `type` | Yes | Response format | `list` |

### Response

```json
["pyth", ["python", "python tutorial", "python online"]]
```

Format: `[original_query, [suggestion1, suggestion2, ...]]`

---

## 7. Text Search — DuckDuckGo Lite (HTML)

When JSON APIs are unavailable, use the Lite HTML endpoint. It returns simpler HTML than the main DuckDuckGo site.

```
POST https://lite.duckduckgo.com/lite/
```

### Request headers

```
Content-Type: application/x-www-form-urlencoded
Referer: https://lite.duckduckgo.com/
```

### Request body (form-urlencoded)

| Field | Required | Description |
|-------|----------|-------------|
| `q` | Yes | Search query |
| `b` | Yes | Empty string (submit button marker) |
| `kl` | No | Region code |
| `df` | No | Time limit (`d`, `w`, `m`, `y`) |

### Response

HTML page. Extract results using XPath or CSS selectors:

| Selector | Meaning |
|----------|---------|
| `//table[last()]//tr` | Result rows |
| `.//a//@href` (first row of each 4-row block) | URL |
| `.//a//text()` (first row) | Title |
| `.//td[@class='result-snippet']//text()` (second row) | Snippet |

Results are grouped in 4-row blocks. Skip blocks where the URL is empty or starts with `https://duckduckgo.com/y.js?`.

### Pagination

Find the next page form: `//form[./input[contains(@value, 'ext')]]`
Extract all hidden `<input>` fields and re-POST them.

---

## 8. Text Search — DuckDuckGo HTML

```
POST https://html.duckduckgo.com/html
```

Similar to Lite but returns richer HTML. Request structure is identical.

Result selectors:

| Selector | Meaning |
|----------|---------|
| `//div[contains(@class, 'body')]` | Result blocks |
| `.//h2//text()` | Title |
| `./a/@href` | URL |
| `./a//text()` | Body snippet |

---

## Safesearch parameter values

| Endpoint | `on` | `moderate` | `off` |
|----------|------|------------|-------|
| Images (`i.js`) | `1` | `1` | `-1` |
| Videos (`v.js`) | `1` | `-1` | `-2` |
| News (`news.js`) | `1` | `-1` | `-2` |

---

## Region codes

| Code | Region |
|------|--------|
| `wt-wt` | Global |
| `us-en` | United States |
| `cn-zh` | China |
| `uk-en` | United Kingdom |
| `jp-jp` | Japan |
| `kr-kr` | Korea |
| `de-de` | Germany |
| `fr-fr` | France |
