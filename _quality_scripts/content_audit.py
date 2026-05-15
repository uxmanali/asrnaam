"""
CHECK 4: identify thin content and structural inconsistencies.
- Counts thin pages (wc<800 or placeholder markers)
- Pages claiming 'no widely-attested' but actually well-known are flagged for review
- Syncs visible bearers into asr-namecard JSON when JSON is empty (15 pages)
- Most enrichment requires authoritative source review (no-fabrication policy)
"""
# See sibling extract.py for data extraction and gender_xlinks.py for cross-page fixes.
