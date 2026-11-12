# AsrNaam Pinterest boards and how to upload

Nothing in this folder has been posted. The CSV and images are ready for review.

## This batch

- 100 name pins (50 boy, 50 girl) and 10 list pins, all 1000×1500 PNG
- Images: this folder, each file at `https://asrnaam.com/pins/<filename>.png`
- Bulk-upload file: `pins.csv` (the Media URL column is already the full public URL)
- Reproducible renderer: `render_pins.py` (kept with the generator; not published here)
- Names skipped, and why: `skipped.md` (same)

All pin links were checked live: HTTP 200, not a redirect stub, canonical spelling. Each link already has

`?utm_source=pinterest&utm_medium=social&utm_campaign=pins`

## Boards used in pins.csv

Create these five boards first in the Pinterest business account. Board names must match the CSV exactly:

| Board | What’s in it | Destination pages |
| --- | --- | --- |
| Muslim Girl Names | 50 girl name pins + the “girl names starting with A” list pin | `/names/<slug>/`, `/names/girls/a/` |
| Muslim Boy Names | 50 boy name pins + boy-name list pins | `/names/<slug>/`, `/names/boys/`, `/names/boys/a/` |
| Quranic Names | Quranic names, prophets, and angels list pins | `/names/quranic/`, `/names/prophets/`, `/names/angels/` |
| Names by Meaning | Light, beautiful | `/names/by-meaning/light/`, `/names/by-meaning/beautiful/` |
| Names by Region | Pakistani girl names, Turkish names | `/names/pakistani-girls/`, `/names/turkish/` |

## Suggested fuller board structure (later batches)

Keep the five boards above as the core, then grow by letter and theme so new pins have a natural home.

### By letter

One board per English initial, plus a parent board:

- Names A to Z → https://asrnaam.com/names/by-letter/
- Muslim Names Starting with A → https://asrnaam.com/names/by-letter/A/
- …through Z, including `/names/girls/A/` and `/names/boys/A/` style pins where useful

Optional Urdu-alphabet boards later, pointing at https://asrnaam.com/names/urdu-alphabet/ and the letter pages such as `/names/urdu-alphabet/alif/`.

### By theme

- Quranic Names (already in this batch)
- Names of the Prophets → `/names/prophets/`
- Angel Names in Islam → `/names/angels/`
- Scholars’ Names → `/names/scholars/`
- Names Meaning Light, Beautiful, Flower, Noble, Royal, Mercy, Brave, Faith, Paradise, Strength, Blessed, Gift, Wisdom, Love, Truth, Guidance, Patience → `/names/by-meaning/<theme>/`

### By region

- Arabic Names → `/names/by-region/arabic/`
- South Asian and Urdu Names → `/names/by-region/south-asian/`
- Pakistani Girl Names / Pakistani Boy Names → `/names/pakistani-girls/`, `/names/pakistani-boys/`
- Turkish Names → `/names/turkish/` or `/names/by-region/turkish/`
- Persian, Gulf, Levantine, North African, West African, Indonesian and Malay, Balkan, East African, Berber → the matching `/names/by-region/...` pages

Do not create a “Short Muslim names” board until a real list page exists on the site (there isn’t one now).

## How to upload (Pinterest needs public image URLs)

Pinterest’s bulk pin creator does not accept local files. These images are already in the site repo at `/pins/<filename>.png`, and every `Media URL` in `pins.csv` is already `https://asrnaam.com/pins/<filename>.png`. Do not prefix them again. The other columns are unchanged.

After this folder is on `main` and GitHub Pages has deployed, check that an image URL returns the PNG (for example `https://asrnaam.com/pins/name-aisha.png`). Then:

1. Create the five boards listed above in the Pinterest business account. Board names must match the CSV exactly.
2. Pinterest Business → Create → bulk create pins via CSV.
3. Upload `pins.csv`.

**Pinterest notes**

- Create the five boards before running a bulk upload.
- Business account is required for CSV bulk create.
- 1000×1500 (2:3) is the standard pin size; these PNGs are already that size.
- After a first batch performs, add letter and theme boards and generate the next set of names from the same renderer.
