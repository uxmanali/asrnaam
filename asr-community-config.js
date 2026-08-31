/* AsrNaam community layer configuration.
   Fill these two in from Supabase: Project Settings, then API.
   The anon key is designed to be public. It is safe here because every table
   is protected by row level security, see db/002_security.sql. The service_role
   key is NOT safe here and must never appear in this file or any other file in
   this repository. */
window.ASR_COMMUNITY = {
  url: '',            // https://xxxxxxxxxxxx.supabase.co
  anonKey: '',        // eyJhb...
  commentsEnabled: true,   // false turns off free text everywhere, voting stays
  minVotesToShow: 3        // must match the HAVING clause in the SQL views
};
