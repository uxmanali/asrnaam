# Community database tests

`003_hardening_test.sql` checks `db/003_hardening.sql` against a throwaway PostgreSQL 16 with Supabase-style roles.

1. Create a scratch database. Create roles `anon`, `authenticated` (nologin), `service_role` (bypassrls), a minimal `auth` schema
   (`auth.users(id uuid primary key, email text)` and `auth.uid()` reading `current_setting('request.jwt.claim.sub', true)`), and
   Supabase's default grants (`alter default privileges in schema public grant all on tables to anon, authenticated, service_role`).
2. Apply `001_community.sql`, `002_security.sql`, `003_hardening.sql` in that order.
3. Run `003_hardening_test.sql` with psql. Every line must say PASS.

The same test run against 001 + 002 alone shows the problems the migration fixes (profile columns readable by anon, self-set
comment_count, self-created moderator profiles, and comment inserts failing with "infinite recursion detected in policy").
