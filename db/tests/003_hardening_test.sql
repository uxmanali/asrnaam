-- Local test for db/003_hardening.sql. Run after 001, 002, 003 and the seed block below, against a disposable PostgreSQL 16
-- with Supabase-style roles. Every line prints PASS or FAIL; a FAIL means the migration must not be applied.
-- Harness (run first on a throwaway database): see db/tests/README.md.
create schema if not exists t;
create or replace function t.chk(label text, expect text, who text, uid text, q text) returns void language plpgsql as $$
declare res text; n bigint := 0;
begin
  begin
    perform set_config('request.jwt.claim.sub', coalesce(uid,''), true);
    execute 'set local role ' || who;
    execute q; get diagnostics n = row_count; res := 'rows=' || n;
  exception when others then res := 'err';
  end;
  execute 'reset role';
  raise notice '% % (expected %, got %)', case when res = expect or (expect like 'rows>=%' and res like 'rows=%' and n >= substr(expect,7)::bigint) then 'PASS' else 'FAIL' end, label, expect, res;
end $$;
-- seed (as superuser)
truncate public.comments, public.ratings, public.trait_votes, public.name_use_votes, public.comment_reports, public.profiles cascade;
delete from auth.users;
insert into auth.users values ('00000000-0000-0000-0000-00000000000a','a@x'),('00000000-0000-0000-0000-00000000000b','b@x'),('00000000-0000-0000-0000-0000000000cc','m@x'),('00000000-0000-0000-0000-0000000000dd','blk@x'),('00000000-0000-0000-0000-0000000000ee','new@x');
insert into public.profiles(id,display_name,is_moderator,is_blocked) values
 ('00000000-0000-0000-0000-00000000000a','Alice',false,false),('00000000-0000-0000-0000-00000000000b','Bob',false,false),
 ('00000000-0000-0000-0000-0000000000cc','Mod',true,false),('00000000-0000-0000-0000-0000000000dd','Blocked',false,true);
insert into public.comments(name_slug,user_id,body,status) values ('aiman','00000000-0000-0000-0000-00000000000b','approved one','approved'),('aiman','00000000-0000-0000-0000-00000000000b','pending one','pending');
insert into public.ratings values ('aiman','00000000-0000-0000-0000-00000000000b',5,now());
\set A '00000000-0000-0000-0000-00000000000a'
\set B '00000000-0000-0000-0000-00000000000b'
\set M '00000000-0000-0000-0000-0000000000cc'
\set X '00000000-0000-0000-0000-0000000000dd'
\set N '00000000-0000-0000-0000-0000000000ee'
-- DA-5.1 profile exposure
select t.chk('anon reads id,display_name','rows=4','anon',null,'select id,display_name from public.profiles');
select t.chk('anon cannot read is_moderator','err','anon',null,'select is_moderator from public.profiles');
select t.chk('anon cannot select *','err','anon',null,'select * from public.profiles');
select t.chk('signed-in cannot read other flags','err','authenticated',:'A','select is_blocked from public.profiles');
select t.chk('get_my_profile works for signed-in','rows=1','authenticated',:'A','select * from public.get_my_profile()');
select t.chk('get_my_profile denied to anon','err','anon',null,'select * from public.get_my_profile()');
-- DA-5.2 self-service limits
select t.chk('own display_name update','rows=1','authenticated',:'A',format('update public.profiles set display_name=%L where id=%L','Alice2',:'A'));
select t.chk('cannot set own comment_count','err','authenticated',:'A',format('update public.profiles set comment_count=999 where id=%L',:'A'));
select t.chk('cannot make self moderator','err','authenticated',:'A',format('update public.profiles set is_moderator=true where id=%L',:'A'));
select t.chk('cannot unblock self','err','authenticated',:'X',format('update public.profiles set is_blocked=false where id=%L',:'X'));
select t.chk('cannot rename someone else','rows=0','authenticated',:'A',format('update public.profiles set display_name=%L where id=%L','hacked',:'B'));
select t.chk('new person creates own profile (id, display_name)','rows=1','authenticated',:'N',format('insert into public.profiles(id,display_name) values (%L,%L)',:'N','Newbie'));
select t.chk('cannot create profile as moderator','err','authenticated',:'N',format('insert into public.profiles(id,display_name,is_moderator) values (%L,%L,true)',:'N','Newbie2'));
select t.chk('cannot create profile for another id','err','authenticated',:'A',format('insert into public.profiles(id,display_name) values (%L,%L)',:'B','Imposter'));
select t.chk('upsert own profile (client does this)','rows=1','authenticated',:'A',format('insert into public.profiles(id,display_name) values (%L,%L) on conflict (id) do update set display_name=excluded.display_name',:'A','Alice3'));
-- comments
select t.chk('post a comment (pending)','rows=1','authenticated',:'A',format('insert into public.comments(name_slug,user_id,body,lang) values (%L,%L,%L,%L)','aiman',:'A','hello there','en'));
select t.chk('cannot post as approved','err','authenticated',:'A',format('insert into public.comments(name_slug,user_id,body,status) values (%L,%L,%L,%L)','aiman',:'A','sneaky','approved'));
select t.chk('cannot post as someone else','err','authenticated',:'A',format('insert into public.comments(name_slug,user_id,body) values (%L,%L,%L)','aiman',:'B','spoof'));
select t.chk('cannot set approved_by on insert','err','authenticated',:'A',format('insert into public.comments(name_slug,user_id,body,approved_by) values (%L,%L,%L,%L)','aiman',:'A','x y z',:'M'));
select t.chk('blocked person cannot comment','err','authenticated',:'X',format('insert into public.comments(name_slug,user_id,body) values (%L,%L,%L)','aiman',:'X','blocked post'));
select t.chk('cannot self-approve','rows=0','authenticated',:'A',format('update public.comments set status=%L where user_id=%L','approved',:'A'));
select t.chk('rate limit: three more comments ok','rows=3','authenticated',:'B','insert into public.comments(name_slug,user_id,body) select ''r'',auth.uid(),''rate test ''||g from generate_series(1,3) g');
select t.chk('rate limit: 6th refused','err','authenticated',:'B',format('insert into public.comments(name_slug,user_id,body) values (%L,%L,%L)','r',:'B','sixth'));
select t.chk('anon sees approved only','rows=1','anon',null,'select id from public.comments');
select t.chk('author sees own pending + approved','rows=2','authenticated',:'A','select id from public.comments where user_id = auth.uid() or status=''approved''');
select t.chk('moderator reads everything','rows>=6','authenticated',:'M','select id from public.comments');
select t.chk('moderator approves','rows=1','authenticated',:'M',format('update public.comments set status=%L, approved_at=now(), approved_by=%L where body=%L','approved',:'M','hello there'));
select t.chk('normal person cannot moderate','rows=0','authenticated',:'A',format('update public.comments set status=%L where body=%L','rejected','approved one'));
select t.chk('person deletes own comment','rows=1','authenticated',:'A',format('delete from public.comments where user_id=%L and body=%L',:'A','hello there'));
select t.chk('person cannot delete others comment','rows=0','authenticated',:'A',format('delete from public.comments where user_id=%L',:'B'));
-- votes stay private; summaries public
select t.chk('anon cannot read ratings','err','anon',null,'select * from public.ratings');
select t.chk('signed-in sees only own rating','rows=0','authenticated',:'A','select * from public.ratings');
select t.chk('rate a name (upsert)','rows=1','authenticated',:'A',format('insert into public.ratings(name_slug,user_id,stars) values (%L,%L,4) on conflict (name_slug,user_id) do update set stars=excluded.stars','aiman',:'A'));
select t.chk('anon cannot vote','err','anon',null,format('insert into public.ratings(name_slug,user_id,stars) values (%L,%L,5)','aiman',:'B'));
select t.chk('cannot vote as someone else','err','authenticated',:'A',format('insert into public.ratings(name_slug,user_id,stars) values (%L,%L,5)','zed',:'B'));
select t.chk('trait vote (upsert)','rows=1','authenticated',:'A',format('insert into public.trait_votes(name_slug,axis,user_id,value) values (%L,%L,%L,1) on conflict (name_slug,axis,user_id) do update set value=excluded.value','aiman','temperament',:'A'));
select t.chk('would-use vote then withdraw','rows=1','authenticated',:'A',format('delete from public.name_use_votes where user_id=%L',:'A')||' ; insert into public.name_use_votes(name_slug,user_id,choice) values (''aiman'',auth.uid(),''would_use'')');
select t.chk('summary views readable by anon','rows=0','anon',null,'select * from public.name_rating_summary');
select t.chk('axes readable by anon','rows>=1','anon',null,'select * from public.trait_axes');
select t.chk('anon cannot write axes','err','anon',null,'update public.trait_axes set left_pole=''x''');
select t.chk('report a comment','rows=1','authenticated',:'A',format('insert into public.comment_reports(comment_id,user_id,reason) select id,%L,%L from public.comments where body=%L',:'A','abuse','approved one'));
select t.chk('only moderators read reports','rows=0','authenticated',:'A','select * from public.comment_reports where user_id <> auth.uid()');
select t.chk('moderator reads reports','rows=1','authenticated',:'M','select * from public.comment_reports');
select t.chk('anon cannot truncate','err','anon',null,'truncate public.comments');
select t.chk('signed-in cannot truncate','err','authenticated',:'A','truncate public.profiles cascade');
-- counter still honest
select case when (select comment_count from public.profiles where id=:'B') >= 4 then 'PASS trigger bumps comment_count' else 'FAIL trigger comment_count' end;
