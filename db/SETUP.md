# Turning the community layer on

Nothing below touches the site. Until step 4 the block is invisible to readers,
which is deliberate: an unconfigured deploy hides itself rather than sitting
there half-built.

## 1. Create the project
supabase.com, new project, pick the region closest to Pakistan or India, since
that is 46% of the traffic. Note the database password somewhere safe. You will
not need it again for this.

## 2. Run the schema
SQL Editor, then run these two in order and check each finishes clean:

  db/001_community.sql
  db/002_security.sql

The second one is the one that matters. It is what stops the public key in
step 4 from being able to read anyone's email, anyone's individual vote, or any
comment that has not been approved. If it errors, stop and fix it before going
further.

## 3. Turn on email codes, and turn off magic links
Authentication, then Providers, then Email:
  - Enable Email provider: on
  - Confirm email: on
  - Secure email change: on
Authentication, then Emails, then the OTP template. Supabase defaults to a
magic link. Replace the body with the six digit code token so people get a code
they type, not a link they click:

  Your AsrNaam code is {{ .Token }}. It expires in one hour.

Set OTP expiry to 3600 and OTP length to 6 under Authentication, Settings.

## 4. Wire the site
Project Settings, then API. Copy the Project URL and the anon public key into
asr-community-config.js, then deploy.

Paste the anon key. Never the service_role key. The anon key is meant to be
public and is safe because of step 2. The service_role key bypasses every
policy in that file and would hand a stranger the whole database.

## 5. Make yourself a moderator
Sign in once at /moderate/ so the account exists, then in the SQL editor:

  update public.profiles set is_moderator = true, display_name = 'YOUR NAME'
  where id = (select id from auth.users where email = 'you@example.com');

## 6. Before you tell anyone it is live
- Post a comment from a second account and confirm it does NOT appear on the
  page until you approve it at /moderate/.
- Confirm the anon key cannot read pending comments: open the site in a private
  window while a comment is pending and check it is absent.
- Update /privacy/ to say you now store an email address and a display name for
  people who comment, and how someone deletes theirs. You are storing personal
  data for the first time and you already serve EEA users under IAB TCF.

## What this costs
Free tier covers roughly 50,000 monthly active users and 500MB of database,
which is far beyond current traffic. The free tier pauses a project after seven
days with no requests; once real traffic arrives that stops being a risk, but
until then check in weekly.

## Deliberate design decisions you may want to overrule

**Trait voting is on axes where both ends are positive.** Gentle or bold, quiet
or outgoing, traditional or modern. Nobody can vote that a name belongs to an
untrustworthy or a stupid person. The feature asks what kind of person carries
a name; asked as an open field on a Muslim names site, that produces ethnic and
sectarian stereotyping, and it produces it beside live ad units. Fragrantica
votes on neutral axes too: longevity and sillage, never a judgement about who
wears a scent. Widening the axes is a one line change in trait_axes. I would
not.

**Aggregates hide below three votes.** With one vote, a public average is that
person's opinion, readable off the page and tied to their name.

**Comments are pre-moderated.** Nothing reaches a reader unread.

**No seeded comments, ever.** A comment section that opens with invented
comments under invented names is a fake review section, and I will not write
one. The votes work honestly from the first vote, which is why voting went on
every page and comments only went on the hundred that already have traffic.
