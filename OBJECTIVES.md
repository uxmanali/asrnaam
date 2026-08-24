# AsrNaam: objective and operating model

Adopted 24 August 2026. This file is the standing brief. Anything built here
should serve it, and anything that contradicts it should be raised rather than
quietly worked around.

## The thesis

AsrNaam is not a 400-page website. It is a ~2,450-name research database that
can be projected into thousands of landing pages, where each name can rank for
a cluster of queries rather than a single keyword. "Aisha" is not one query; it
is Aisha meaning, Aisha name meaning in Islam, Aisha meaning in Urdu, Ayesha
meaning, Aisha lucky number, Aisha personality, and a dozen more.

The differentiator is not "what does this name mean". Every baby-names site
answers that. It is: what does it mean, what is its Arabic root, and what does
the Ilm ul Huroof reading say. That is defensible in a way a meanings list is
not.

## The five layers

| Layer | What it is | State |
|---|---|---|
| 1 | Individual name pages, answer-first | Built. 2,450 pages, answer above the fold |
| 2 | Alphabet pages, English and Urdu | Built. 78 English, 32 Urdu, plus hubs |
| 3 | Names by meaning | Built. 19 themes, 47 pages, sorted at the Arabic root |
| 4 | Geography | Partial. 12 region pages rebuilt; country-level and geography x gender x meaning still open |
| 5 | Ilm ul Huroof as the moat | Woven through every layer |

## Traffic milestones

| Stage | Organic visitors / month |
|---|---|
| Proof of concept | 10,000 |
| Good site | 50,000 |
| **First real target** | **100,000** |
| Major site | 500,000 |
| Very large | 1,000,000+ |

The first target is 100,000 a month, roughly 3,300 a day. At that point there is
enough signal to learn which names, countries and query shapes actually drive
the business.

## Revenue model, in order

1. **Advertising first.** Plumbing is built and inert; see `ads-config.js`.
2. **Paid product second.** SEO to a free reading, then a personalised report.
   The arithmetic is better than ads: at 500,000 visitors a month, a 0.2%
   conversion on a $15 report is $15,000, before any ad revenue. Ads are the
   floor, not the ceiling.

## Where the site actually is

Measured 23 April to 22 July 2026, the site's first 91 days.

| | Clicks | Impressions | CTR |
|---|---|---|---|
| Month 1 | 34 | 14,557 | 0.23% |
| Month 2 | 368 | 95,104 | 0.39% |
| Month 3 | 996 | 268,381 | 0.37% |
| **Run rate** | **~1,350/mo** | **~333,000/mo** | **0.37%** |

Two things matter in that table.

Impressions grew eighteenfold in ninety days. The content and the crawl are
working, and average position is around 9 on mobile, which is respectable for a
site this young.

CTR did not move at all. 0.23%, 0.39%, 0.37%. Eighteen times the impressions
bought no improvement in the rate at which they convert. Growth is coming
entirely from more impressions, not from better conversion of them.

## The honest constraint

CTR is a multiplier on everything else, and it is stuck.

At 0.37%, 333,000 impressions a month yields 1,350 clicks. At a par rate for
position 9, nearer 2%, the same impressions yield 6,600. That is roughly a
fivefold difference on traffic already won, before a single new page is built
or a single position gained.

Individual queries show the problem plainly: "ibrahim in urdu" at 1,743
impressions and zero clicks, position 9.7. "muhammad name meaning in urdu",
854 impressions, zero clicks, position 8.4.

Some of that is unwinnable. A query like "ibrahim in urdu" is often answered in
the result page itself, and no title will beat a reader who already has what
they came for. But zero clicks at position 8 across thousands of impressions is
not all zero-click search.

The levers, in order:

1. **CTR.** Titles ran to a median 81 characters against roughly 60 that Google
   renders, so every one was cut mid-phrase. Fixed August 2026; watch whether
   the rate moves.
2. **Index coverage.** Sitemaps are complete, so the gap between pages built and
   pages indexed is a crawl and quality question, not a plumbing one. 6,500
   variant-spelling redirect stubs sit in the crawl path.
3. **Then rankings**, and only then more pages.

Advertising revenue follows traffic and cannot lead it. At the current run rate
a $15 RPM earns roughly $20 a month. The ad plumbing exists so the approval
clock can start, not because it pays yet.

Note on RPM: the audience is 27% Pakistan and 19% India by impressions, with the
United States and United Kingdom together under 10%. Ad rates in the dominant
markets run a fraction of the $5 to $25 the plan assumes. Model the low end, and
treat the paid product as the real business rather than a supplement to ads.

## Rules of the house

- Zero em-dashes in shipped copy. Title separator is ": ".
- Visible FAQ and FAQPage JSON-LD must always match. Structured data describing
  content the reader cannot see is a policy violation.
- The answer the searcher came for stays above the fold. Ads go below it.
- Commits are authored `Claude <noreply@anthropic.com>`.
- Deploy runs through the Mac; the sandbox cannot push.
