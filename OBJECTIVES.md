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

## The honest constraint

Traffic, not monetisation, is the binding constraint. At the current 235 clicks
a month, advertising at a $15 RPM earns about $3.50. The ad work exists so the
approval clock starts and the plumbing is ready, not because it pays yet.

The levers that matter, in order:

1. **Index coverage.** Google shows roughly 1,996 names indexed against 2,450
   live. Closing that gap is free traffic on pages that already exist.
2. **Click-through rate.** 235 clicks from 86,088 impressions is 0.27% at an
   average position around 9. Par at that position is nearer 2%. Ranking is
   already there; the clicks are not.
3. **Then rankings**, and only then more pages.

Building Layer 4 before fixing CTR would add impressions to a funnel that
converts at a seventh of par.

## Rules of the house

- Zero em-dashes in shipped copy. Title separator is ": ".
- Visible FAQ and FAQPage JSON-LD must always match. Structured data describing
  content the reader cannot see is a policy violation.
- The answer the searcher came for stays above the fold. Ads go below it.
- Commits are authored `Claude <noreply@anthropic.com>`.
- Deploy runs through the Mac; the sandbox cannot push.
