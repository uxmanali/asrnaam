# New interface wording on the redesigned Arabic name pages: for review

Written 22 Nov 2026 for `redesign/locale/ar.json`. These are the only strings on the redesigned Arabic pages that are not
already on the site. Everything else (section labels, headings, card labels, jump links, related-names heading)
is the page's own existing wording, moved, not rewritten. Change a string in the JSON file and rebuild; the check
(`redesign/np_check_loc.py`) fails on any text that is neither old page text, one of these labels, nor a content-file string.

| Key | Where it shows | New wording | English it stands for |
|---|---|---|---|
| `draft` | review tag | جديد، للمراجعة | New, for your review (tag on content added from the content file; not shown in the final build) |
| `dyk` | did-you-know strip | هل تعلم؟ | Did you know? |
| `source` | did-you-know strip | المصدر: | Source: |
| `jump_aria` | jump links (not visible) | في هذه الصفحة | On this page (screen-reader label of the jump links) |
| `mode_aria` | mode switch (not visible) | لمن تقرأ | Who are you reading for (screen-reader label of the switch) |
| `mode_me` | mode switch | هذا اسمي | This is my name |
| `mode_baby` | mode switch | أختار اسمًا لمولود | I'm naming a baby |
| `kit_kicker` | parent section label and jump link | للوالدين | For parents |
| `kit_h2` | parent section heading | إذا اخترتم اسم {name} لمولودكم | Parent kit: naming a baby {name} |
| `kit_teaser` | parent section | تختارون اسمًا لمولود؟ افتحوا قسم الوالدين: النطق، وتجربة الاسم مع اسم العائلة، وأسماء ذات صلة. | Naming a baby? Open the parent section: pronunciation, a surname test and related names. |
| `kit_open` | parent section button | افتح قسم الوالدين | Open parent view |
| `surname_h` | parent section, surname box | جرّب الاسم مع اسم العائلة | Try it with your surname |
| `surname_label` | parent section, surname box | اكتب اسم العائلة | Your surname |
| `surname_note` | parent section, surname box | ما تكتبه يبقى في هذه الصفحة ولا يُرسَل إلى أي مكان. | Nothing you type leaves this page. |
| `play` | hero play button (not visible) | استمع إلى النطق | Play pronunciation (screen-reader label of the play button) |
| `save` | hero and phone bar | حفظ | Save |
| `saved` | hero | تم الحفظ | Saved |
| `share` | hero and phone bar | مشاركة | Share |
| `search` | phone bar | ابحث عن اسم آخر | Search another name (phone bar) |

The last five (`play`, `save`, `saved`, `share`, `search`) are shown by the site script, which today writes them in English;
they appear only after the script change in `ur-ar-js-change.md` is applied.

## Reused, not new

- `bearers_kicker`: الحاملون (kicker of the bearers section on the Arabic pages). Used only when a content file adds bearers to a page that had no bearers section.
- `bearers_title`: من حمل هذا الاسم (heading of the bearers section on the Arabic pages). Used only when a content file adds bearers to a page that had no bearers section.
- `abjad`: القيمة العددية (wording of the FAQ question on every Arabic page (ما القيمة العددية لاسم ...)). Label of the abjad card, which the Arabic pages had only in English ("Abjad lucky number", written by the script).

## Taken from each page as it stands (listed so the mapping is visible, nothing to review)

Quick-fact labels the builder reads: المعنى المعجمي · الأصل · الجنس · الجذر العربي · الرسم الأردي · الرسم العربي · النطق اللاتيني · عدد الحروف · تفصيل الحروف · علم الحروف

