-- ============================================================================
-- AsrNaam community layer
-- Postgres / Supabase. Run once, in order, in the SQL editor.
--
-- Design notes that are not obvious from the column names:
--
-- 1. Trait voting is on BIPOLAR AXES WHERE BOTH POLES ARE POSITIVE
--    (gentle/bold, quiet/outgoing). This is deliberate and it is the most
--    important decision in this file. The feature asks people what kind of
--    person carries a name. Asked as free choice over arbitrary adjectives on
--    a Muslim names site, that produces ethnic and sectarian stereotyping, and
--    it produces it next to live AdSense units. Fragrantica votes on neutral
--    axes too: longevity and sillage, never "what kind of person wears this".
--    Constrain the axes and the feature stays warm. Open them and it will not.
--
-- 2. Individual votes are never publicly readable. Only the aggregate view is.
--    A vote reveals a real person's opinion tied to their account.
--
-- 3. Comments default to status 'pending'. Nothing reaches the page until a
--    moderator approves it.
-- ============================================================================

create extension if not exists "uuid-ossp";

-- ---------------------------------------------------------------- profiles
-- Supabase auth.users holds the email. This holds what the site displays.
create table if not exists public.profiles (
  id            uuid primary key references auth.users(id) on delete cascade,
  display_name  text not null check (char_length(display_name) between 2 and 32),
  created_at    timestamptz not null default now(),
  is_moderator  boolean not null default false,
  is_blocked    boolean not null default false,
  comment_count integer not null default 0
);

-- ---------------------------------------------------------------- comments
create table if not exists public.comments (
  id           uuid primary key default uuid_generate_v4(),
  name_slug    text not null,
  user_id      uuid not null references public.profiles(id) on delete cascade,
  body         text not null check (char_length(body) between 3 and 2000),
  lang         text not null default 'en' check (lang in ('en','ar','ur','hi')),
  status       text not null default 'pending'
                 check (status in ('pending','approved','rejected','spam')),
  created_at   timestamptz not null default now(),
  approved_at  timestamptz,
  approved_by  uuid references public.profiles(id),
  reply_to     uuid references public.comments(id) on delete cascade
);
create index if not exists comments_slug_approved_idx
  on public.comments (name_slug, created_at desc) where status = 'approved';
create index if not exists comments_pending_idx
  on public.comments (created_at) where status = 'pending';

-- ---------------------------------------------------------------- ratings
create table if not exists public.ratings (
  name_slug  text not null,
  user_id    uuid not null references public.profiles(id) on delete cascade,
  stars      smallint not null check (stars between 1 and 5),
  updated_at timestamptz not null default now(),
  primary key (name_slug, user_id)
);

-- ---------------------------------------------------------------- trait votes
-- Bipolar axes. -2 is the left pole, +2 the right pole, 0 is balanced.
-- Both poles are desirable qualities. See design note 1.
create table if not exists public.trait_axes (
  key        text primary key,
  left_pole  text not null,
  right_pole text not null,
  sort_order smallint not null
);
insert into public.trait_axes (key,left_pole,right_pole,sort_order) values
  ('temperament','Gentle','Bold',1),
  ('social','Quiet','Outgoing',2),
  ('era','Traditional','Modern',3),
  ('cast','Grounded','Dreaming',4),
  ('tone','Serious','Playful',5),
  ('sound','Soft to say','Strong to say',6)
on conflict (key) do nothing;

create table if not exists public.trait_votes (
  name_slug  text not null,
  axis      text not null references public.trait_axes(key),
  user_id   uuid not null references public.profiles(id) on delete cascade,
  value     smallint not null check (value between -2 and 2),
  updated_at timestamptz not null default now(),
  primary key (name_slug, axis, user_id)
);

-- ---------------------------------------------------------------- would-use
create table if not exists public.name_use_votes (
  name_slug  text not null,
  user_id    uuid not null references public.profiles(id) on delete cascade,
  choice     text not null check (choice in ('would_use','maybe','would_not','have_used','know_someone')),
  updated_at timestamptz not null default now(),
  primary key (name_slug, user_id, choice)
);

-- ---------------------------------------------------------------- reports
create table if not exists public.comment_reports (
  id         uuid primary key default uuid_generate_v4(),
  comment_id uuid not null references public.comments(id) on delete cascade,
  user_id    uuid not null references public.profiles(id) on delete cascade,
  reason     text not null check (reason in ('abuse','spam','off_topic','stereotyping','other')),
  note       text check (char_length(note) <= 500),
  created_at timestamptz not null default now(),
  unique (comment_id, user_id)
);
