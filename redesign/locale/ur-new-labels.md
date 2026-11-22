# New interface wording on the redesigned Urdu name pages: for review

Written 22 Nov 2026 for `redesign/locale/ur.json`. These are the only strings on the redesigned Urdu pages that are not
already on the site. Everything else (section labels, headings, card labels, jump links, related-names heading)
is the page's own existing wording, moved, not rewritten. Change a string in the JSON file and rebuild; the check
(`redesign/np_check_loc.py`) fails on any text that is neither old page text, one of these labels, nor a content-file string.

| Key | Where it shows | New wording | English it stands for |
|---|---|---|---|
| `draft` | review tag | نیا، آپ کے جائزے کے لیے | New, for your review (tag on content added from the content file; not shown in the final build) |
| `dyk` | did-you-know strip | کیا آپ جانتے ہیں؟ | Did you know? |
| `source` | did-you-know strip | ماخذ: | Source: |
| `jump_aria` | jump links (not visible) | اس صفحے پر | On this page (screen-reader label of the jump links) |
| `mode_aria` | mode switch (not visible) | آپ کس کے لیے پڑھ رہے ہیں | Who are you reading for (screen-reader label of the switch) |
| `mode_me` | mode switch | یہ میرا نام ہے | This is my name |
| `mode_baby` | mode switch | بچے کا نام رکھنا ہے | I'm naming a baby |
| `kit_kicker` | parent section label and jump link | والدین کے لیے | For parents |
| `kit_h2` | parent section heading | بچے کا نام {name} رکھنا ہو تو | Parent kit: naming a baby {name} |
| `kit_teaser` | parent section | بچے کا نام رکھ رہے ہیں؟ والدین کا حصہ کھولیں: تلفظ، خاندانی نام کے ساتھ آزمائش اور متعلقہ نام۔ | Naming a baby? Open the parent section: pronunciation, a surname test and related names. |
| `kit_open` | parent section button | والدین کا حصہ کھولیں | Open parent view |
| `surname_h` | parent section, surname box | خاندانی نام کے ساتھ دیکھیں | Try it with your surname |
| `surname_label` | parent section, surname box | اپنا خاندانی نام لکھیں | Your surname |
| `surname_note` | parent section, surname box | آپ جو کچھ لکھتے ہیں وہ اسی صفحے پر رہتا ہے۔ | Nothing you type leaves this page. |
| `play` | hero play button (not visible) | تلفظ سنیں | Play pronunciation (screen-reader label of the play button) |
| `save` | hero and phone bar | محفوظ کریں | Save |
| `saved` | hero | محفوظ ہے | Saved |
| `share` | hero and phone bar | شیئر کریں | Share |
| `search` | phone bar | کوئی اور نام تلاش کریں | Search another name (phone bar) |

The last five (`play`, `save`, `saved`, `share`, `search`) are shown by the site script, which today writes them in English;
they appear only after the script change in `ur-ar-js-change.md` is applied.

## Reused, not new

- `bearers_kicker`: حاملین (kicker of the bearers section on the Urdu pages). Used only when a content file adds bearers to a page that had no bearers section.
- `bearers_title`: یہ نام کس نے اٹھایا (heading of the bearers section on the Urdu pages). Used only when a content file adds bearers to a page that had no bearers section.

## Taken from each page as it stands (listed so the mapping is visible, nothing to review)

Quick-fact labels the builder reads: لغوی معنی · اصل · صنف · عربی جذر · اردو املا · عربی املا · تلفظ · حروف کی تعداد · حروف · ابجد / خوش نصیب عدد

