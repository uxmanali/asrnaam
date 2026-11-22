# Hindi name pages: labels written new for the redesign (for review)

Source of truth: `redesign/locale/hi.json`. Everything else on the migrated pages is the page's own wording, moved unchanged.

## Written new (no existing wording on the site)

| Where | Label | Meaning |
|---|---|---|
| Breadcrumb, screen-reader label (was the English word "Breadcrumb") | आप यहाँ हैं | You are here |
| Save button in the hero (shown once the script change is applied) | सहेजें | Save |
| Save button, after saving | सहेजा गया | Saved |
| Share button in the hero | साझा करें | Share |
| Play button, second line and screen-reader label | उच्चारण सुनें | Listen to the pronunciation |

The last four sit on the page as `data-l-*` attributes and are not visible until `asr-redesign.js` reads them (see `hi-tr-js-change.md`). Until then the buttons say Save and Share in English.

## Reused from wording already on the Hindi pages

| Where | Label | Taken from |
|---|---|---|
| Section tag 01 | इल्म-उल-हुरूफ़ | page text |
| Section tag, origin | अरबी मूल | the heading "… का अरबी मूल (जड़)" |
| Section tag, meaning | मतलब | the fact label |
| Jump link, letters | अक्षर | the fact label "अरबी अक्षर" |
| Jump link, origin | अरबी मूल | the heading |
| Jump link, meaning | मतलब | the fact label |
| Jump link, questions | सवाल | the heading "अक्सर पूछे जाने वाले सवाल" |
| Jump link, more names | और नाम | the line "… से शुरू होने वाले और नाम" |
| Jump bar, screen-reader label | इस पेज पर | hi/names/ index ("इस पेज पर क्या है?") |
