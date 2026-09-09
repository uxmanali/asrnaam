# Open items

Everything the audit suite still reports, and why it is still open.

## Six names whose Arabic spelling is genuinely disputed

The names index and the English page say one thing; the Urdu and Arabic pages
say another; and the name's own stated meaning does not settle it. Seventy-four
other names in this class were decided against their meaning and origin and are
recorded in `fix/spelling_decisions.py` with the reason for each. These six are
not guessable.

| Name | Why it is open |
|---|---|
| `aleena` | ألينا vs علينة. The gloss "soft, delicate" points at the root l-y-n, which neither spelling carries cleanly. |
| `alizeh` | الزہ is missing a letter; عليزه uses ʿayn for a Persian name. Both look wrong. |
| `alma` | Both stored forms use ʿayn, but the gloss says Bosnian/Spanish, which would be ألما. |
| `aqil` | عقيل is the classical name; عاقل is the adjective the gloss describes. Different words. |
| `cheikhou` | The West African Fula form is Cheikhou, which is neither شيخ nor الشيخ. |
| `ibrahima` | The Fula form is Ibrahima; one stored form is plain Ibrahim, the other uses Urdu letters. |

Deciding each one settles five checks at once: L0.1, L0.3, L0.4, L1.1 and L1.3.

`spelling-disputes.csv` holds the full working file, including the 74
already decided, with both candidate spellings and the abjad total each implies.

## One missing letter page

Dhal (ذ, abjad 700) is scored on 30 names but has no page of its own.
`/letters/dhal/` currently redirects to Dal (د, abjad 4), a different letter with
a different value. Ta marbuta (ة, 5) also has no page and currently borrows
Ha light (ه, 5), which is at least the right number and the right sound in pause.

## Claims with no oracle

- 24 popularity claims in the names data ("top 10 Pakistan", "most searched")
  that nothing on the site supports. Source them or remove them.
- 1,986 English pages carry a Quranic or prophetic attribution. A pass in
  August corrected 77 of these; the rest have never been checked against a
  lexicon, and the suite deliberately reports this rather than passing it.
