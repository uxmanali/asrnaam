-- PROPOSED, NOT APPLIED. Written 4 Nov 2026 for deep-audit checks DA-5.1 to DA-5.3 (audit sections 7.1 to 7.3).
-- Apply in the Supabase SQL editor only after reading it, on a copy of the project first, then test with a
-- non-privileged signed-in account and with the anon key. It changes no site file.
-- Client change needed with it: asr-community.js line 216 reads the whole own profile with select('*');
-- switch that call to  sb.rpc('get_my_profile')  (defined below).

-- DA-5.1: the public may read only the display name (and id, which the comments join needs), not the flags or counters.
revoke select on public.profiles from anon, authenticated;
grant select (id, display_name) on public.profiles to anon, authenticated;

-- A signed-in person reads their own full row through a function, because column grants cannot be row-specific.
create or replace function public.get_my_profile()
returns table (id uuid, display_name text, created_at timestamptz, is_moderator boolean, is_blocked boolean, comment_count integer)
language sql security definer set search_path = public, pg_temp stable as $$
  select p.id, p.display_name, p.created_at, p.is_moderator, p.is_blocked, p.comment_count
  from public.profiles p where p.id = auth.uid();
$$;
revoke execute on function public.get_my_profile() from public, anon;
grant execute on function public.get_my_profile() to authenticated;

-- DA-5.2: a person may not set their own counter (or created_at). The old check already froze is_moderator and is_blocked.
drop policy if exists "a person may edit their own profile" on public.profiles;
create policy "a person may edit their own profile"
  on public.profiles for update using (auth.uid() = id)
  with check (
    auth.uid() = id
    and is_moderator  = (select p.is_moderator  from public.profiles p where p.id = auth.uid())
    and is_blocked    = (select p.is_blocked    from public.profiles p where p.id = auth.uid())
    and comment_count = (select p.comment_count from public.profiles p where p.id = auth.uid())
    and created_at    = (select p.created_at    from public.profiles p where p.id = auth.uid())
  );
-- Belt and braces: remove column-level UPDATE on the protected columns for signed-in people.
revoke update on public.profiles from authenticated;
grant update (display_name) on public.profiles to authenticated;

-- DA-5.3: harden the definer function.
create or replace function public.bump_comment_count() returns trigger
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  update public.profiles set comment_count = comment_count + 1 where id = new.user_id;
  return new;
end $$;
revoke execute on function public.bump_comment_count() from public, anon, authenticated;
