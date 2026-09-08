# AsrNaam audit suite

    python3 audit/run.py                      # everything
    python3 audit/run.py --only L0 L1         # the layers that catch wrong facts
    python3 audit/run.py --only L0.4          # one check
    python3 audit/run.py --json report.json   # machine-readable

Exit code is non-zero if any high-severity check fails, so it can gate a deploy.

## The rule this suite exists to enforce

**Every check must name an ORACLE: the independent thing it compares the site
against.** A check that compares the site to itself, or to a value the site
generated, cannot find a generator bug.

That is precisely how the abjad defect survived every audit before this one.
The earlier audits checked links, hreflang, schema validity, duplicate content,
CLS and page speed. All of those compare structure to structure. None of them
ever recomputed a number the site had generated, so a generator that dropped
the letter ya from 1,003 pages passed every one of them.

The three specific blind spots, named so they stay closed:

1. **No audit ever recomputed a derived value.** Generated data was treated as
   ground truth. Layer L0 exists for this.
2. **No audit ever compared the four language mirrors of the same fact.** Any
   two mirrors disagreeing proves one is wrong with no reference data at all.
   Layer L1 exists for this.
3. **Audits ran where the work had been done, not where the traffic was.** The
   English pages were checked most; the Urdu pages carry every top query. Every
   check here runs across all four locales by default.

## Layers, strongest oracle first

| Layer | Oracle | Finds |
|---|---|---|
| **L0** Recompute | Arithmetic from source data | Wrong numbers, wrong letters, generator bugs |
| **L1** Cross-surface | Another surface of the site that must agree | Mirrors disagreeing about the same fact |
| **L2** Self-consistent | The other half of the same page | Visible text diverging from JSON-LD |
| **L3** Structure | The filesystem and the HTTP contract | Broken links, sitemap drift, duplicate titles |
| **L4** Language | The page's declared language | Untranslated text, placeholders, boilerplate |
| **L5** Unsourced | **None exists** | Claims that need sourcing or removal |

L5 never reports a pass. A claim with no oracle is not verified, and calling it
verified is the failure mode this whole suite is built to avoid.

## Adding a check

```python
@check('L0.8','L0','What must be true',
       'The independent thing this compares against.')
def l0_8():
    return [F(slug, 'what is wrong', locale)]
```

If you cannot write a real sentence for the oracle argument, the check does not
belong in L0-L4. Put it in L5 and say so.

## What this suite still cannot see

Stated plainly, so nobody mistakes a green run for a correct site:

- **Whether the Arabic spelling stored for a name is the right spelling.** L0
  recomputes the total *from* that spelling. If the spelling is wrong the total
  is confidently wrong. 89 names are known to be in dispute; see
  `fix/flagged.json`.
- **Whether a meaning is true.** No lexicon is wired in. L5.2 counts the claims
  so they can be re-checked by hand.
- **Whether the Ilm ul Huroof readings are good.** That is editorial judgement.
- **Rendering.** Layout, CLS and mobile overflow need a browser; run those
  separately.
- **Anything only Search Console knows** — indexing, impressions, queries.
