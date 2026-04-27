# Bing Text Search Fallback

> **Implementation note:** This document describes the HTTP protocol between client and server. The actual Rust implementation uses `primp::Client` with `Impersonate::Chrome` (or `Random`) to send these requests with browser fingerprint simulation, which is required to bypass anti-bot checks on Bing.

When DuckDuckGo endpoints are blocked or return no results, Bing search serves as a reliable fallback for text search. The `duckduckgo-search` Python library uses Bing as its default backend for text queries.

## Endpoint

```
GET https://www.bing.com/search
```

## Request

### Headers

```
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
```

### Cookies (required for region targeting)

| Cookie | Format | Example |
|--------|--------|---------|
| `_EDGE_CD` | `m={lang}-{country}&u={lang}-{country}` | `m=en-us&u=en-us` |
| `_EDGE_S` | `mkt={lang}-{country}&ui={lang}-{country}` | `mkt=en-us&ui=en-us` |

The region code format is `{lang}-{country}` in lowercase (e.g., `en-us`, `zh-cn`).

### Query parameters

| Param | Required | Description | Example |
|-------|----------|-------------|---------|
| `q` | Yes | Search query | `Rust programming` |
| `pq` | Yes | Same as `q` | `Rust programming` |
| `cc` | Yes | Language code (2-letter) | `en`, `zh` |
| `filters` | No | Time filter | `ex1:"ez1"` |
| `first` | No | Result offset (for pagination) | `11` |
| `FORM` | No | Pagination form ID | `PERE`, `PERE1`, `PERE2` |

### Time filter (`filters`)

Calculate the filter code based on current date:

| Period | Code formula | Example (day 95100) |
|--------|--------------|---------------------|
| Day | `ez1` | `ex1:"ez1"` |
| Week | `ez2` | `ex1:"ez2"` |
| Month | `ez3` | `ex1:"ez3"` |
| Year | `ez5_{d-365}_{d}` | `ex1:"ez5_94735_95100"` |

Where `d = floor(current_unix_time / 86400)`.

### Pagination

| Page | `first` | `FORM` |
|------|---------|--------|
| 1 | (omitted) | (omitted) |
| 2 | `11` | `PERE` |
| 3 | `21` | `PERE1` |
| 4 | `31` | `PERE2` |
| N | `(N-1)*10 + 1` | `PERE{N-2}` |

## Response

HTML page. Extract results using XPath or CSS selectors:

| Selector | Meaning |
|----------|---------|
| `//li[contains(@class, 'b_algo')]` | Result items |
| `.//h2/a/@href` | URL (may be Bing-wrapped) |
| `.//h2/a//text()` | Title |
| `.//p//text()` | Body snippet |

## URL unwrapping

Bing wraps result URLs in a redirect:

```
https://www.bing.com/ck/a?!&&p=...&u=a1b2c3...
```

To decode the original URL:

1. Parse the query string and extract the `u` parameter
2. Remove the first 2 characters from `u` (e.g., `a1` prefix)
3. Base64 URL-safe decode the remainder
4. Pad with `=` to a multiple of 4 if needed

### Pseudocode

```
function unwrapBingUrl(wrappedUrl):
    parsed = parseUrl(wrappedUrl)
    uValues = parsed.query.u
    if uValues is empty: return null
    
    u = uValues[0]
    if length(u) <= 2: return null
    
    b64Part = u.substring(2)
    padding = repeat("=", (-length(b64Part)) % 4)
    decoded = base64UrlSafeDecode(b64Part + padding)
    return decoded.asString()
```

### Example

| Wrapped URL | `u` param | After stripping prefix | Decoded |
|-------------|-----------|------------------------|---------|
| `https://www.bing.com/ck/a?u=a1aHR0cHM6Ly9leGFtcGxlLmNvbQ` | `a1aHR0cHM6Ly9leGFtcGxlLmNvbQ` | `aHR0cHM6Ly9leGFtcGxlLmNvbQ` | `https://example.com` |

## Filtering ads

Skip results where `href` starts with:
- `https://www.bing.com/aclick?` — paid advertisement
- `https://www.bing.com/ck/a?` with unwrapping failure — tracking link

## Error patterns

| HTML content | Meaning |
|--------------|---------|
| `There are no results for` | Empty result set |
| `class="b_algo"` not found | Parse failure or anti-bot block |
