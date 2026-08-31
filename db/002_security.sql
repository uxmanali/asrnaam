-- ============================================================================
-- AsrNaam community layer: row level security and public aggregates.
--
-- The anon key ships inside a public JavaScript file on a static site. Assume
-- every visitor has it. Everything below is written on that assumption: the
-- anon key must be able to read approved comments and aggregate numbers, and
-- nothing else. No individual vote, no email, no pending comment.
-- ============================================================================

alter table public.profiles        enable row level security;
alter table public.comments        enable row level security;
alter table public.ratings         enable row level security;
alter table public.trait_votes     enable row level security;
alter table public.name_use_votes  enable row level security;
alter table public.comment_reports enable row level security;
alter table public.trait_axes      enable row level security;

-- axes are reference data
create policy "axes are public" on public.trait_axes for select using (true);

-- ---------------------------------------------------------------- profiles
-- Display name is public because it appears next to a comment. Nothing else is.
create policy "display names are public"
  on public.profiles for select using (true);
create policy "a person may create their own profile"
  on public.profiles for insert with check (auth.uid() = id);
create policy "a person may edit their own profile"
  on public.profiles for update using (auth.uid() = id)
  with check (auth.uid() = id and is_moderator = (select is_moderator from public.profiles where id = auth.uid())
              and is_blocked = (select is_blocked from public.profiles where id = auth.uid()));

-- ---------------------------------------------------------------- comments
create policy "approved comments are public"
  on public.comments for select
  using (status = 'approved' or user_id = auth.uid());

create policy "signed-in and unblocked people may comment"
  on public.comments for insert
  with check (
    auth.uid() = user_id
    and status = 'pending'                                  -- cannot self-approve
    and not exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_blocked)
    -- rate limit: at most 5 comments in any 10 minutes
    and (select count(*) from public.comments c
         where c.user_id = auth.uid() and c.created_at > now() - interval '10 minutes') < 5
  );

create policy "a person may delete their own comment"
  on public.comments for delete using (auth.uid() = user_id);

create policy "moderators may read everything"
  on public.comments for select
  using (exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_moderator));
create policy "moderators may set status"
  on public.comments for update
  using (exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_moderator));

-- ---------------------------------------------------------------- votes
-- Deliberately NO public select. Individual votes stay private; the page reads
-- the aggregate views below instead.
create policy "a person may see their own rating"
  on public.ratings for select using (auth.uid() = user_id);
create policy "a person may cast their own rating"
  on public.ratings for insert with check (auth.uid() = user_id);
create policy "a person may change their own rating"
  on public.ratings for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "a person may see their own trait votes"
  on public.trait_votes for select using (auth.uid() = user_id);
create policy "a person may cast their own trait vote"
  on public.trait_votes for insert with check (auth.uid() = user_id);
create policy "a person may change their own trait vote"
  on public.trait_votes for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "a person may see their own use votes"
  on public.name_use_votes for select using (auth.uid() = user_id);
create policy "a person may cast their own use vote"
  on public.name_use_votes for insert with check (auth.uid() = user_id);
create policy "a person may withdraw their own use vote"
  on public.name_use_votes for delete using (auth.uid() = user_id);

create policy "a person may report a comment once"
  on public.comment_reports for insert with check (auth.uid() = user_id);
create policy "moderators read reports"
  on public.comment_reports for select
  using (exists (select 1 from public.profiles p where p.id = auth.uid() and p.is_moderator));

-- ============================================================================
-- Public aggregates. security_invoker = off so these read past RLS, which is
-- the point: the numbers are public, the votes behind them are not.
-- A minimum of 3 voters before an aggregate is exposed, so that a name with a
-- single vote cannot have that vote read back off the page.
-- ============================================================================

create or replace view public.name_rating_summary
with (security_invoker = off) as
  select name_slug,
         round(avg(stars)::numeric, 2) as avg_stars,
         count(*)::int                 as vote_count
  from public.ratings
  group by name_slug
  having count(*) >= 3;

create or replace view public.name_trait_summary
with (security_invoker = off) as
  select name_slug, axis,
         round(avg(value)::numeric, 2) as avg_value,
         count(*)::int                 as vote_count
  from public.trait_votes
  group by name_slug, axis
  having count(*) >= 3;

create or replace view public.name_use_summary
with (security_invoker = off) as
  select name_slug, choice, count(*)::int as vote_count
  from public.name_use_votes
  group by name_slug, choice
  having count(*) >= 3;

grant select on public.name_rating_summary to anon, authenticated;
grant select on public.name_trait_summary  to anon, authenticated;
grant select on public.name_use_summary    to anon, authenticated;

-- keep profiles.comment_count honest
create or replace function public.bump_comment_count() returns trigger
language plpgsql security definer as $$
begin
  update public.profiles set comment_count = comment_count + 1 where id = new.user_id;
  return new;
end $$;
drop trigger if exists comments_bump on public.comments;
create trigger comments_bump after insert on public.comments
  for each row execute function public.bump_comment_count();
