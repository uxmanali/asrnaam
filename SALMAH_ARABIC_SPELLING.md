## Salmah, Arabic spelling field appears to use U+06C6 (Kurdish O with V) in place of a final letter

**File:** `names/salmah/index.html`
**Current Arabic:** `سلمۆ` (s-l-m-ۆ)
**IUH text:** "Sin of secret opens, Lam of authority, Meem of love, Ha of presence. Peace made into love and presence."

The IUH text correctly cites four letters (Sin, Lam, Meem, Ha) but the Arabic field's final character is `ۆ` (U+06C6, Kurdish-script o-with-V), which is neither ه (ha-light) nor ة (taa marbuta) and does not belong in the standard Arabic form of Salmah. The correct Arabic spelling is most likely `سَلْمَى` (with alif maqsura ى) or `سَلْمَة` (with marbuta ة).

Recommend correcting the Arabic field upstream rather than rewriting the IUH text.
