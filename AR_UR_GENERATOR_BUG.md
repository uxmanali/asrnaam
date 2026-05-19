# AR/UR generator: unescaped `<span lang="en">` leaking into meta attributes

**Status:** rendered HTML cleaned in commit (see Phase 2 of Agent C SEO sweep). Root cause unfixed — will regenerate next time the AR/UR pipeline runs.

**Affected pages:** 704 (352 under `ar/names/`, 352 under `ur/names/`)

## Symptom

The `<meta name="description">`, `og:description`, and `twitter:description` tags on affected pages contain raw `<span lang="en">…</span>` markup *inside* the `content="…"` attribute. Because the inner `"` characters terminate the attribute prematurely, browsers and crawlers parse the description as `رافع: <span lang=` (truncated mid-tag) instead of the intended full text.

### Example (pre-fix)

```html
<meta name="description" content="رافع: <span lang="en">exalter</span>, الواحد الذي <span lang="en">raises</span> عالٍ — قراءة الحروف، الجذر العربي، ومعنى الاسم في علم الحروف على أَسْرَنام.">
```

When parsed, the description becomes `رافع: <span lang=` — useless to search engines.

### After Phase 2 cleanup

```html
<meta name="description" content="رافع: exalter, الواحد الذي raises عالٍ — قراءة الحروف، الجذر العربي، ومعنى الاسم في علم الحروف على أَسْرَنام.">
```

Spans stripped, attribute now valid.

## Root cause

The AR/UR page generator pulls the dictionary meaning from a source that wraps English glosses in `<span lang="en">…</span>` (legitimate for the page body — it lets fonts switch on inline English). When the generator templates the meaning into the `<meta>` `content` attribute, it does not HTML-escape or strip those spans.

### 3 additional edge cases

`ar/names/munir/`, `ar/names/naveed/`, `ur/names/naveed/` had truncated `<span lang="` tags with no closing `>` — meaning the upstream meaning string itself was clipped mid-tag, suggesting the corruption happened before generation too. These were hand-cleaned.

## Recommended upstream fix

In the AR/UR generator, before emitting `<meta name="description">`, `og:description`, and `twitter:description`:

1. **Strip all HTML tags from the meaning text** (regex: `<[^>]+>` → empty) — meta attributes do not render HTML.
2. **HTML-escape** the resulting plain text (`"` → `&quot;`, `<` → `&lt;`, etc.) — defensive against future formatting.
3. (Optional) trim to 160 chars at a clean word boundary.

The same source meaning is rendered with full markup inside the page `<body>` (in `.qf-value` cells, `<h1>`, etc.) — those should remain unchanged. The fix only applies to the meta head attributes.

## Verification after upstream fix

```bash
grep -rl 'name="description" content="[^"]*<span lang=' --include=index.html ar/names ur/names | wc -l
# Expected: 0
```
