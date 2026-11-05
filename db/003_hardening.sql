-- AsrNaam community hardening, v2 (6 Nov 2026). TESTED against a local PostgreSQL 16 with Supabase-style roles
-- (anon, authenticated), default Supabase table grants, and 001 + 002 applied first. Test file: db/tests/003_hardening_test.sql
-- STATUS: PROPOSED, NOT APPLIED to the live project. Only the project owner applies it (Supabase dashboard, SQL editor).
-- Run 001, 002, then this file. It is safe to run twice.
--
-- What the local test showed about 001 + 002 as they stand (all fixed below):
--  1. Anyone with the public anon key can read every profile column, including is_moderator, is_blocked, comment_count (DA-5.1).
--  2. A signed-in person can set their own comment_count to any number (DA-5.2), and can create their profile with
--     is_moderator = true, because the insert policy checks only the id.
--  3. Inserting a comment fails for everyone with "infinite recursion detected in policy for relation comments" (the
--     rate-limit sub-select reads the table the policy protects). Posting comments cannot work until this is replaced.
--  4. Default Supabase grants give anon and authenticated every privilege on every table; only RLS stood between the
--     public key and the data. This file moves to least privilege: grants that match what asr-community.js does.
-- Client: asr-community.js already reads only id and display_name from profiles (no change needed).

-- ---------------------------------------------------------------- helpers (no arguments, so they can only describe the caller)
create or replace function public.is_moderator() returns boolean
language sql security definer stable set search_path = public, pg_temp as $$
  select coalesce((select p.is_moderator from public.profiles p where p.id = auth.uid()), false);
$$;
create or replace function public.is_blocked() returns boolean
language sql security definer stable set search_path = public, pg_temp as $$
  select coalesce((select p.is_blocked from public.profiles p where p.id = auth.uid()), false);
$$;
create or replace function public.my_recent_comment_count() returns integer
language sql security definer stable set search_path = public, pg_temp as $$
  select count(*)::int from public.comments c where c.user_id = auth.uid() and c.created_at > now() - interval '10 minutes';
$$;
revoke execute on function public.is_moderator(), public.is_blocked(), public.my_recent_comment_count() from public;
grant  execute on function public.is_moderator(), public.is_blocked(), public.my_recent_comment_count() to anon, authenticated;

-- A signed-in person reads their own full profile through a function (column grants cannot be row-specific).
create or replace function public.get_my_profile()
returns table (id uuid, display_name text, created_at timestamptz, is_moderator boolean, is_blocked boolean, comment_count integer)
language sql security definer stable set search_path = public, pg_temp as $$
  select p.id, p.display_name, p.created_at, p.is_moderator, p.is_blocked, p.comment_count
  from public.profiles p where p.id = auth.uid();
$$;
revoke execute on function public.get_my_profile() from public, anon;
grant  execute on function public.get_my_profile() to authenticated;

-- ---------------------------------------------------------------- least-privilege grants
revoke all on public.profiles, public.comments, public.ratings, public.trait_votes, public.name_use_votes,
              public.comment_reports, public.trait_axes from anon, authenticated;
revoke all on public.name_rating_summary, public.name_trait_summary, public.name_use_summary from anon, authenticated;

-- public (anon and authenticated)
grant select (id, display_name) on public.profiles to anon, authenticated;
grant select on public.comments, public.trait_axes to anon, authenticated;       -- rows limited by RLS (approved only)
grant select on public.name_rating_summary, public.name_trait_summary, public.name_use_summary to anon, authenticated;

-- signed-in only; the sensitive columns (is_moderator, is_blocked, comment_count, created_at) have no insert or update grant
grant insert (id, display_name) on public.profiles to authenticated;
grant update (display_name)     on public.profiles to authenticated;
grant insert (name_slug, user_id, body, lang, reply_to) on public.comments to authenticated;   -- status stays 'pending', approved_by stays null
grant update (status, approved_at, approved_by)         on public.comments to authenticated;   -- reachable only through the moderator policy
grant delete on public.comments to authenticated;                                              -- own comments only (policy)
grant select, insert, update on public.ratings, public.trait_votes to authenticated;
grant select, insert, delete on public.name_use_votes to authenticated;
grant select, insert         on public.comment_reports to authenticated;

-- ---------------------------------------------------------------- policies rebuilt on the helpers
drop policy if exists "a person may edit their own profile" on public.profiles;
create policy "a person may edit their own profile"
  on public.profiles for update using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists "signed-in and unblocked people may comment" on public.comments;
create policy "signed-in and unblocked people may comment"
  on public.comments for insert
  with check (auth.uid() = user_id and status = 'pending' and not public.is_blocked() and public.my_recent_comment_count() < 5);

drop policy if exists "moderators may read everything" on public.comments;
create policy "moderators may read everything" on public.comments for select using (public.is_moderator());
drop policy if exists "moderators may set status" on public.comments;
create policy "moderators may set status" on public.comments for update using (public.is_moderator()) with check (public.is_moderator());

drop policy if exists "moderators read reports" on public.comment_reports;
create policy "moderators read reports" on public.comment_reports for select using (public.is_moderator());

-- a blocked person cannot vote or report either
drop policy if exists "a person may report a comment once" on public.comment_reports;
create policy "a person may report a comment once" on public.comment_reports
  for insert with check (auth.uid() = user_id and not public.is_blocked());

-- ---------------------------------------------------------------- DA-5.3: the counter trigger
create or replace function public.bump_comment_count() returns trigger
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  update public.profiles set comment_count = comment_count + 1 where id = new.user_id;
  return new;
end $$;
revoke execute on function public.bump_comment_count() from public, anon, authenticated;
