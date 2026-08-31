/* ============================================================================
   AsrNaam community layer.

   Loads lazily, below the fold, and reserves its own height before it renders.
   That is not politeness: this site's Core Web Vitals were repaired by hand on
   a throttled phone, and a block that pops in after paint would undo it.

   Auth is email plus a six digit code. No passwords are set, stored or asked
   for, anywhere in this file.
   ============================================================================ */
(function () {
  'use strict';
  var CFG = window.ASR_COMMUNITY || {};
  // Until Supabase is configured the block must not sit on the page shimmering
  // at people forever. Hide it outright, so an unconfigured deploy is invisible
  // rather than broken.
  if (!CFG.url || !CFG.anonKey) {
    var pre = document.getElementById('asr-community');
    if (pre) pre.classList.add('failed');
    return;
  }

  var SLUG = (function () {
    var m = location.pathname.match(/^\/(?:ar\/|ur\/|hi\/)?names\/([^\/]+)\/?$/);
    return m ? m[1] : null;
  })();
  if (!SLUG) return;

  var LANG = document.documentElement.lang || 'en';
  var T = {
    en: { head:'This name, by the people who know it', rate:'Your rating', rated:'You rated this',
          ratings:'ratings', traits:'How this name reads', votes:'votes', use:'Would you use this name?',
          yes:'Would use', maybe:'Maybe', no:'Would not', know:'I know someone called this',
          comments:'Comments', none:'No comments on this name yet. Yours would be the first.',
          signin:'Sign in to add yours', email:'Your email', send:'Send me a code',
          code:'Six digit code', verify:'Verify', name:'Display name', save:'Save',
          write:'Share what you know about this name', post:'Post comment',
          pending:'Thank you. Your comment goes live once a moderator has read it.',
          sent:'Code sent. Check your email.', out:'Sign out', few:'Not enough votes yet',
          report:'Report', reported:'Reported. Thank you.',
          guide:'Please write about the name, not about any individual person.' },
    ur: { head:'یہ نام، ان لوگوں کی نظر میں جو اسے جانتے ہیں', rate:'آپ کی درجہ بندی', rated:'آپ نے درجہ دیا',
          ratings:'درجہ بندیاں', traits:'یہ نام کیسا لگتا ہے', votes:'ووٹ', use:'کیا آپ یہ نام رکھیں گے؟',
          yes:'ہاں', maybe:'شاید', no:'نہیں', know:'میں اس نام کا کوئی جاننے والا ہوں',
          comments:'تبصرے', none:'ابھی اس نام پر کوئی تبصرہ نہیں۔ پہلا آپ کا ہو سکتا ہے۔',
          signin:'تبصرے کے لیے سائن اِن کریں', email:'آپ کا ای میل', send:'مجھے کوڈ بھیجیں',
          code:'چھ ہندسوں کا کوڈ', verify:'تصدیق کریں', name:'ظاہر ہونے والا نام', save:'محفوظ کریں',
          write:'اس نام کے بارے میں اپنی بات لکھیے', post:'تبصرہ شائع کریں',
          pending:'شکریہ۔ منتظم کی نظرثانی کے بعد آپ کا تبصرہ شائع ہو گا۔',
          sent:'کوڈ بھیج دیا گیا۔ اپنا ای میل دیکھیے۔', out:'سائن آؤٹ', few:'ابھی کافی ووٹ نہیں',
          report:'رپورٹ', reported:'رپورٹ ہو گیا۔ شکریہ۔',
          guide:'براہ کرم نام کے بارے میں لکھیے، کسی فرد کے بارے میں نہیں۔' },
    ar: { head:'هذا الاسم، بعيون من يعرفونه', rate:'تقييمك', rated:'قيّمتَ هذا',
          ratings:'تقييمات', traits:'كيف يُقرأ هذا الاسم', votes:'أصوات', use:'هل تختار هذا الاسم؟',
          yes:'نعم', maybe:'ربما', no:'لا', know:'أعرف شخصًا بهذا الاسم',
          comments:'التعليقات', none:'لا تعليقات على هذا الاسم بعد. يمكن أن يكون تعليقك الأول.',
          signin:'سجّل الدخول لتضيف تعليقك', email:'بريدك الإلكتروني', send:'أرسل لي رمزًا',
          code:'رمز من ستة أرقام', verify:'تحقّق', name:'الاسم الظاهر', save:'حفظ',
          write:'اكتب ما تعرفه عن هذا الاسم', post:'انشر التعليق',
          pending:'شكرًا لك. يظهر تعليقك بعد مراجعة المشرف.',
          sent:'أُرسل الرمز. تفقّد بريدك.', out:'تسجيل الخروج', few:'الأصوات غير كافية بعد',
          report:'إبلاغ', reported:'تم الإبلاغ. شكرًا لك.',
          guide:'اكتب عن الاسم من فضلك، لا عن شخص بعينه.' },
    hi: { head:'यह नाम, उन लोगों की नज़र से जो इसे जानते हैं', rate:'आपकी रेटिंग', rated:'आपने रेट किया',
          ratings:'रेटिंग', traits:'यह नाम कैसा लगता है', votes:'वोट', use:'क्या आप यह नाम रखेंगे?',
          yes:'हाँ', maybe:'शायद', no:'नहीं', know:'मैं इस नाम का कोई व्यक्ति जानता हूँ',
          comments:'टिप्पणियाँ', none:'इस नाम पर अभी कोई टिप्पणी नहीं। पहली आपकी हो सकती है।',
          signin:'टिप्पणी के लिए साइन इन करें', email:'आपका ईमेल', send:'मुझे कोड भेजें',
          code:'छह अंकों का कोड', verify:'सत्यापित करें', name:'प्रदर्शित नाम', save:'सहेजें',
          write:'इस नाम के बारे में अपनी बात लिखें', post:'टिप्पणी करें',
          pending:'धन्यवाद। मॉडरेटर की समीक्षा के बाद आपकी टिप्पणी दिखेगी।',
          sent:'कोड भेजा गया। अपना ईमेल देखें।', out:'साइन आउट', few:'अभी पर्याप्त वोट नहीं',
          report:'रिपोर्ट', reported:'रिपोर्ट हो गई। धन्यवाद।',
          guide:'कृपया नाम के बारे में लिखें, किसी व्यक्ति के बारे में नहीं।' }
  }[LANG] || null;
  var t = T || {};

  var sb = null, me = null, profile = null, axes = [];
  var root = document.getElementById('asr-community');
  if (!root) return;

  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : s; return d.innerHTML; }
  function el(html) { var d = document.createElement('div'); d.innerHTML = html; return d.firstElementChild; }

  function loadSupabase() {
    return new Promise(function (res, rej) {
      if (window.supabase) return res();
      var s = document.createElement('script');
      s.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js';
      s.crossOrigin = 'anonymous';
      s.onload = res; s.onerror = rej;
      document.head.appendChild(s);
    });
  }

  // ---------------------------------------------------------------- rendering
  function stars(avg, count, mine) {
    var full = Math.round(avg || 0), out = '<div class="asrc-rate"><div class="asrc-stars" role="group" aria-label="' + esc(t.rate) + '">';
    for (var i = 1; i <= 5; i++) {
      out += '<button type="button" class="asrc-star' + (i <= (mine || full) ? ' on' : '') +
             '" data-stars="' + i + '" aria-label="' + i + '">' + (i <= (mine || full) ? '★' : '☆') + '</button>';
    }
    out += '</div><span class="asrc-rate-n">' + (count ? (avg + ' · ' + count + ' ' + esc(t.ratings)) : esc(t.few)) + '</span></div>';
    return out;
  }

  function axisRow(a, agg, mine) {
    var v = (agg && agg.avg_value != null) ? Number(agg.avg_value) : null;
    var pct = v == null ? 50 : ((v + 2) / 4) * 100;
    return '<div class="asrc-axis" data-axis="' + esc(a.key) + '">' +
      '<span class="asrc-pole">' + esc(a.left_pole) + '</span>' +
      '<span class="asrc-bar" role="img" aria-label="' + esc(a.left_pole + ' to ' + a.right_pole) + '">' +
        (v == null ? '<i class="asrc-fill empty"></i>' : '<i class="asrc-fill" style="left:' + pct.toFixed(1) + '%"></i>') +
      '</span>' +
      '<span class="asrc-pole">' + esc(a.right_pole) + '</span>' +
      '<span class="asrc-axis-n">' + (agg ? agg.vote_count + ' ' + esc(t.votes) : esc(t.few)) + '</span>' +
      '<span class="asrc-axis-vote">' + [-2,-1,0,1,2].map(function (n) {
        return '<button type="button" data-v="' + n + '"' + (mine === n ? ' class="on"' : '') +
               ' aria-label="' + (n < 0 ? esc(a.left_pole) : n > 0 ? esc(a.right_pole) : 'balanced') + '"></button>';
      }).join('') + '</span></div>';
  }

  function render(data) {
    var h = '<h2 class="asrc-head">' + esc(t.head) + '</h2>';
    h += stars(data.rating && data.rating.avg_stars, data.rating && data.rating.vote_count, data.mine && data.mine.stars);
    h += '<div class="asrc-traits"><p class="asrc-sub">' + esc(t.traits) + '</p>';
    axes.forEach(function (a) {
      h += axisRow(a, data.traits[a.key], data.mineTraits[a.key]);
    });
    h += '</div>';
    var uses = data.use || {};
    h += '<div class="asrc-use"><p class="asrc-sub">' + esc(t.use) + '</p><div class="asrc-use-row">' +
      [['would_use', t.yes], ['maybe', t.maybe], ['would_not', t.no], ['know_someone', t.know]].map(function (p) {
        var n = uses[p[0]] ? uses[p[0]].vote_count : 0;
        return '<button type="button" class="asrc-use-btn' + (data.mineUse[p[0]] ? ' on' : '') +
               '" data-choice="' + p[0] + '">' + esc(p[1]) + (n ? ' <b>' + n + '</b>' : '') + '</button>';
      }).join('') + '</div></div>';

    if (CFG.commentsEnabled !== false) {
      h += '<div class="asrc-comments"><p class="asrc-sub">' + esc(t.comments) +
           (data.comments.length ? ' (' + data.comments.length + ')' : '') + '</p>';
      h += data.comments.length ? data.comments.map(function (c) {
        return '<article class="asrc-c" data-id="' + esc(c.id) + '"><header><b>' +
          esc(c.profiles ? c.profiles.display_name : '') + '</b><time datetime="' + esc(c.created_at) + '">' +
          new Date(c.created_at).toLocaleDateString(LANG) + '</time></header><p>' + esc(c.body) +
          '</p><button type="button" class="asrc-report">' + esc(t.report) + '</button></article>';
      }).join('') : '<p class="asrc-empty">' + esc(t.none) + '</p>';
      h += '<div class="asrc-auth"></div></div>';
    }
    root.innerHTML = h;
    root.classList.add('ready');
    wire(data);
    if (CFG.commentsEnabled !== false) renderAuth();
  }

  // ---------------------------------------------------------------- auth
  function renderAuth() {
    var box = root.querySelector('.asrc-auth'); if (!box) return;
    if (!me) {
      box.innerHTML = '<form class="asrc-signin"><label>' + esc(t.email) +
        '<input type="email" name="email" required autocomplete="email" inputmode="email"></label>' +
        '<button type="submit">' + esc(t.send) + '</button></form>';
      box.querySelector('form').addEventListener('submit', function (e) {
        e.preventDefault();
        var email = e.target.email.value.trim();
        sb.auth.signInWithOtp({ email: email, options: { shouldCreateUser: true } }).then(function (r) {
          if (r.error) return note(box, r.error.message, true);
          box.innerHTML = '<form class="asrc-signin"><p class="asrc-ok">' + esc(t.sent) + '</p><label>' +
            esc(t.code) + '<input name="code" inputmode="numeric" pattern="[0-9]{6}" maxlength="6" required autocomplete="one-time-code"></label>' +
            '<button type="submit">' + esc(t.verify) + '</button></form>';
          box.querySelector('form').addEventListener('submit', function (e2) {
            e2.preventDefault();
            sb.auth.verifyOtp({ email: email, token: e2.target.code.value.trim(), type: 'email' })
              .then(function (r2) {
                if (r2.error) return note(box, r2.error.message, true);
                me = r2.data.user; ensureProfile().then(renderAuth);
              });
          });
        });
      });
      return;
    }
    if (!profile || !profile.display_name) {
      box.innerHTML = '<form class="asrc-signin"><label>' + esc(t.name) +
        '<input name="dn" required minlength="2" maxlength="32"></label><button type="submit">' + esc(t.save) + '</button></form>';
      box.querySelector('form').addEventListener('submit', function (e) {
        e.preventDefault();
        sb.from('profiles').upsert({ id: me.id, display_name: e.target.dn.value.trim() }).select().single()
          .then(function (r) { if (!r.error) { profile = r.data; renderAuth(); } else note(box, r.error.message, true); });
      });
      return;
    }
    box.innerHTML = '<form class="asrc-write"><p class="asrc-guide">' + esc(t.guide) + '</p>' +
      '<textarea name="body" required minlength="3" maxlength="2000" rows="3" placeholder="' + esc(t.write) + '"></textarea>' +
      '<div class="asrc-write-row"><button type="submit">' + esc(t.post) + '</button>' +
      '<button type="button" class="asrc-out">' + esc(t.out) + '</button></div></form>';
    box.querySelector('.asrc-out').addEventListener('click', function () {
      sb.auth.signOut().then(function () { me = null; profile = null; renderAuth(); });
    });
    box.querySelector('form').addEventListener('submit', function (e) {
      e.preventDefault();
      sb.from('comments').insert({ name_slug: SLUG, user_id: me.id, body: e.target.body.value.trim(), lang: LANG })
        .then(function (r) {
          if (r.error) return note(box, r.error.message, true);
          box.innerHTML = '<p class="asrc-ok">' + esc(t.pending) + '</p>';
        });
    });
  }

  function note(box, msg, bad) {
    var p = el('<p class="asrc-note' + (bad ? ' bad' : '') + '">' + esc(msg) + '</p>');
    box.appendChild(p); setTimeout(function () { p.remove(); }, 6000);
  }

  function ensureProfile() {
    return sb.from('profiles').select('*').eq('id', me.id).maybeSingle()
      .then(function (r) { profile = r.data; return profile; });
  }

  // ---------------------------------------------------------------- wiring
  function needAuth() {
    var box = root.querySelector('.asrc-auth');
    if (box) { box.scrollIntoView({ behavior: 'smooth', block: 'center' }); var i = box.querySelector('input'); if (i) i.focus(); }
    return !me;
  }

  function wire(data) {
    root.querySelectorAll('.asrc-star').forEach(function (b) {
      b.addEventListener('click', function () {
        if (needAuth()) return;
        var n = +b.dataset.stars;
        sb.from('ratings').upsert({ name_slug: SLUG, user_id: me.id, stars: n, updated_at: new Date().toISOString() })
          .then(function () { load(); });
      });
    });
    root.querySelectorAll('.asrc-axis-vote button').forEach(function (b) {
      b.addEventListener('click', function () {
        if (needAuth()) return;
        var axis = b.closest('.asrc-axis').dataset.axis;
        sb.from('trait_votes').upsert({ name_slug: SLUG, axis: axis, user_id: me.id, value: +b.dataset.v, updated_at: new Date().toISOString() })
          .then(function () { load(); });
      });
    });
    root.querySelectorAll('.asrc-use-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        if (needAuth()) return;
        var choice = b.dataset.choice;
        var on = b.classList.contains('on');
        var q = on ? sb.from('name_use_votes').delete().match({ name_slug: SLUG, user_id: me.id, choice: choice })
                   : sb.from('name_use_votes').upsert({ name_slug: SLUG, user_id: me.id, choice: choice });
        q.then(function () { load(); });
      });
    });
    root.querySelectorAll('.asrc-report').forEach(function (b) {
      b.addEventListener('click', function () {
        if (needAuth()) return;
        sb.from('comment_reports').insert({ comment_id: b.closest('.asrc-c').dataset.id, user_id: me.id, reason: 'abuse' })
          .then(function () { b.textContent = t.reported; b.disabled = true; });
      });
    });
  }

  // ---------------------------------------------------------------- data
  function load() {
    var q = [
      sb.from('name_rating_summary').select('*').eq('name_slug', SLUG).maybeSingle(),
      sb.from('name_trait_summary').select('*').eq('name_slug', SLUG),
      sb.from('name_use_summary').select('*').eq('name_slug', SLUG),
      CFG.commentsEnabled === false ? Promise.resolve({ data: [] })
        : sb.from('comments').select('id,body,created_at,profiles(display_name)')
            .eq('name_slug', SLUG).eq('status', 'approved').order('created_at', { ascending: false }).limit(50)
    ];
    if (me) {
      q.push(sb.from('ratings').select('stars').eq('name_slug', SLUG).eq('user_id', me.id).maybeSingle());
      q.push(sb.from('trait_votes').select('axis,value').eq('name_slug', SLUG).eq('user_id', me.id));
      q.push(sb.from('name_use_votes').select('choice').eq('name_slug', SLUG).eq('user_id', me.id));
    }
    return Promise.all(q).then(function (r) {
      var traits = {}; (r[1].data || []).forEach(function (x) { traits[x.axis] = x; });
      var use = {}; (r[2].data || []).forEach(function (x) { use[x.choice] = x; });
      var mineTraits = {}; if (r[5]) (r[5].data || []).forEach(function (x) { mineTraits[x.axis] = x.value; });
      var mineUse = {}; if (r[6]) (r[6].data || []).forEach(function (x) { mineUse[x.choice] = true; });
      render({ rating: r[0].data, traits: traits, use: use, comments: r[3].data || [],
               mine: r[4] ? r[4].data : null, mineTraits: mineTraits, mineUse: mineUse });
    });
  }

  function start() {
    loadSupabase().then(function () {
      sb = window.supabase.createClient(CFG.url, CFG.anonKey);
      return sb.auth.getUser();
    }).then(function (r) {
      me = (r && r.data && r.data.user) || null;
      return sb.from('trait_axes').select('*').order('sort_order');
    }).then(function (r) {
      axes = r.data || [];
      return me ? ensureProfile() : null;
    }).then(load).catch(function (e) {
      root.innerHTML = ''; root.classList.add('failed');
      if (window.console) console.warn('[asr-community]', e);
    });
  }

  // below the fold, so do not compete with LCP
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      if (es[0].isIntersecting) { io.disconnect(); start(); }
    }, { rootMargin: '300px' });
    io.observe(root);
  } else { start(); }
})();
