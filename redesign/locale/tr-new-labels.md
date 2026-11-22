# Turkish name pages: labels written new for the redesign (for review)

Source of truth: `redesign/locale/tr.json`. Everything else on the migrated pages is the page's own wording, moved unchanged.

## Written new (no existing wording on the site)

| Where | Label | Meaning |
|---|---|---|
| Breadcrumb, screen-reader label (was the English word "Breadcrumb") | Sayfa yolu | Page path |
| Save button in the hero (shown once the script change is applied) | Kaydet | Save |
| Save button, after saving | Kaydedildi | Saved |
| Share button in the hero | Paylaş | Share |
| Play button, second line and screen-reader label | Telaffuzu dinle | Listen to the pronunciation |

The last four sit on the page as `data-l-*` attributes and are not visible until `asr-redesign.js` reads them (see `hi-tr-js-change.md`). Until then the buttons say Save and Share in English.

## Reused from wording already on the Turkish pages

| Where | Label | Taken from |
|---|---|---|
| Section tag 01 | Huruf ilmi | page text |
| Section tag, origin | Köken | the fact label |
| Section tag, meaning | Anlamı | the fact label |
| Jump links | Harf harf okuma, Kökeni, Sık sorulan sorular, Benzer isimler | the page headings, word for word |
| Jump link, meaning | Anlamı | the fact label |
| Jump bar, screen-reader label | Bu sayfada | tr/names/ index ("Bu sayfada 168 ismin …") |
