/* ============================================================
   AsrNaam — Save reading as image (canvas card + QR)
   Loaded on per-name pages via asr-enhance.js.
   ============================================================ */
(function(){
  'use strict';

  var QR_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js';
  var FONT_LOAD_ATTEMPTED = false;

  function loadScript(src){
    return new Promise(function(resolve, reject){
      if(window.qrcode){ resolve(); return; }
      var existing = document.querySelector('script[data-asr-qr]');
      if(existing){
        existing.addEventListener('load', resolve);
        existing.addEventListener('error', reject);
        return;
      }
      var s = document.createElement('script');
      s.src = src; s.async = true; s.dataset.asrQr = '1';
      s.onload = resolve; s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function ensureFonts(){
    if(FONT_LOAD_ATTEMPTED) return;
    FONT_LOAD_ATTEMPTED = true;
    // Pull Nastaliq just-in-time so the card has it.
    if(!document.querySelector('link[data-asr-nastaliq]')){
      var l = document.createElement('link');
      l.rel = 'stylesheet';
      l.href = 'https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@500;700&family=Noto+Naskh+Arabic:wght@500;700&display=swap';
      l.dataset.asrNastaliq = '1';
      document.head.appendChild(l);
    }
  }

  function readPageData(){
    var slug = (location.pathname.match(/\/names\/([^\/]+)/) || [])[1] || '';
    if(!slug) return null;
    var data = { slug: slug, name: '', arabic: '', urdu: '', meaning: '', url: '' };
    data.url = 'https://asrnaam.com/names/' + slug + '/';

    // 1) Try structured JSON namecard (most authoritative)
    var card = document.getElementById('asr-namecard');
    if(card){
      try{
        var j = JSON.parse(card.textContent);
        data.name = j.english || '';
        data.arabic = j.arabic || '';
        data.urdu = j.urdu || '';
        if(j.meaning){
          data.meaning = j.meaning.dict || j.meaning.iuh || '';
        }
      }catch(e){}
    }

    // 2) Fallbacks
    if(!data.name){
      var bc = document.querySelector('.asr-breadcrumb .current');
      if(bc) data.name = bc.textContent.trim();
      if(!data.name){
        var h = document.querySelector('h1');
        if(h) data.name = h.textContent.trim();
      }
    }
    if(!data.arabic){
      var ar = document.querySelector('.hero .arabic-name, .arabic-name');
      if(ar) data.arabic = ar.textContent.trim();
    }
    if(!data.meaning){
      var meta = document.querySelector('meta[name="description"]');
      if(meta) data.meaning = (meta.content || '').trim();
    }

    return data;
  }

  function wrapText(ctx, text, x, y, maxWidth, lineHeight, maxLines){
    if(!text) return 0;
    var words = String(text).split(/\s+/);
    var line = '', lines = [];
    for(var i=0;i<words.length;i++){
      var test = line ? line + ' ' + words[i] : words[i];
      if(ctx.measureText(test).width > maxWidth && line){
        lines.push(line);
        line = words[i];
        if(lines.length === maxLines - 1){
          var rem = words.slice(i).join(' ');
          while(rem.length && ctx.measureText(rem + '…').width > maxWidth){
            rem = rem.slice(0, -1);
          }
          if(rem !== words.slice(i).join(' ')) rem += '…';
          lines.push(rem);
          line = '';
          break;
        }
      } else {
        line = test;
      }
    }
    if(line && lines.length < maxLines) lines.push(line);
    for(var j=0;j<lines.length;j++){
      ctx.fillText(lines[j], x, y + j * lineHeight);
    }
    return lines.length;
  }

  function buildQR(url, size){
    var qr = window.qrcode(0, 'M');
    qr.addData(url);
    qr.make();
    var modules = qr.getModuleCount();
    var cell = size / modules;
    var c = document.createElement('canvas');
    c.width = size; c.height = size;
    var ctx = c.getContext('2d');
    ctx.fillStyle = '#FAFAF8';
    ctx.fillRect(0, 0, size, size);
    ctx.fillStyle = '#2A2A20';
    for(var r=0;r<modules;r++){
      for(var col=0;col<modules;col++){
        if(qr.isDark(r, col)){
          ctx.fillRect(col * cell, r * cell, cell + 0.6, cell + 0.6);
        }
      }
    }
    return c;
  }

  function render(data){
    var W = 1080, H = 1350;
    var canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H;
    var ctx = canvas.getContext('2d');

    // Sage-green vertical gradient
    var bg = ctx.createLinearGradient(0, 0, 0, H);
    bg.addColorStop(0,    '#3F4E3F');
    bg.addColorStop(0.55, '#4A5944');
    bg.addColorStop(1,    '#2C3829');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);

    // Subtle paper grain
    ctx.globalAlpha = 0.045;
    ctx.fillStyle = '#F5ECD7';
    for(var i=0;i<220;i++){
      ctx.fillRect(Math.random()*W, Math.random()*H, 1.3, 1.3);
    }
    ctx.globalAlpha = 1;

    // Gold accent border
    ctx.strokeStyle = '#C9930A';
    ctx.lineWidth = 6;
    ctx.strokeRect(30, 30, W - 60, H - 60);
    ctx.strokeStyle = 'rgba(212,160,23,0.38)';
    ctx.lineWidth = 1;
    ctx.strokeRect(48, 48, W - 96, H - 96);

    // Top eyebrow
    ctx.fillStyle = 'rgba(245,236,215,0.78)';
    ctx.font = '600 22px Cinzel, Georgia, serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText('A S R   ·   N A A M', W / 2, 92);

    ctx.fillStyle = '#C9930A';
    ctx.fillRect(W / 2 - 36, 130, 72, 1.4);

    ctx.fillStyle = 'rgba(245,236,215,0.55)';
    ctx.font = '500 13px Cinzel, Georgia, serif';
    ctx.fillText('I L M   U L   H U R O O F   ·   T H E   R E A D I N G', W / 2, 148);

    // English name (Cinzel-ish)
    ctx.fillStyle = '#F5ECD7';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    var nameSize = 120;
    ctx.font = '500 ' + nameSize + 'px Cinzel, Georgia, serif';
    while(ctx.measureText(data.name).width > W - 200 && nameSize > 56){
      nameSize -= 4;
      ctx.font = '500 ' + nameSize + 'px Cinzel, Georgia, serif';
    }
    var nameY = 280;
    ctx.fillText(data.name, W / 2, nameY);

    // Divider
    var dy = nameY + nameSize / 2 + 38;
    ctx.fillStyle = '#C9930A';
    ctx.fillRect(W / 2 - 70, dy, 140, 2);

    // Arabic
    var arY = dy + 92;
    if(data.arabic){
      ctx.fillStyle = '#F5ECD7';
      ctx.font = '500 80px "Noto Naskh Arabic", "Amiri", "Scheherazade New", serif';
      ctx.textBaseline = 'middle';
      ctx.fillText(data.arabic, W / 2, arY);
    }

    // Urdu
    var urY = arY + 100;
    if(data.urdu && data.urdu !== data.arabic){
      ctx.fillStyle = 'rgba(245,236,215,0.88)';
      ctx.font = '500 60px "Noto Nastaliq Urdu", "Noto Naskh Arabic", "Amiri", serif';
      ctx.fillText(data.urdu, W / 2, urY);
    } else {
      urY = arY;
    }

    // Mid divider
    var dy2 = urY + 78;
    ctx.fillStyle = 'rgba(212,160,23,0.55)';
    ctx.fillRect(W / 2 - 36, dy2, 72, 1);

    // Meaning (2–3 lines)
    var quote = (data.meaning || '').trim();
    if(quote){
      ctx.fillStyle = 'rgba(245,236,215,0.94)';
      ctx.font = 'italic 600 36px Georgia, "Cormorant Garamond", serif';
      ctx.textBaseline = 'top';
      wrapText(ctx, '"' + quote + '"', W / 2, dy2 + 44, W - 220, 50, 3);
    }

    // QR + asrnaam.com at bottom
    var qrSize = 240;
    var qrX = W / 2 - qrSize / 2;
    var qrY = H - qrSize - 130;

    if(window.qrcode){
      try{
        var qc = buildQR(data.url, qrSize);
        var pad = 18, rad = 12;
        var bx = qrX - pad, by = qrY - pad;
        var bw = qrSize + pad * 2, bh = qrSize + pad * 2;
        ctx.fillStyle = '#FAFAF8';
        ctx.beginPath();
        ctx.moveTo(bx + rad, by);
        ctx.lineTo(bx + bw - rad, by);
        ctx.quadraticCurveTo(bx + bw, by, bx + bw, by + rad);
        ctx.lineTo(bx + bw, by + bh - rad);
        ctx.quadraticCurveTo(bx + bw, by + bh, bx + bw - rad, by + bh);
        ctx.lineTo(bx + rad, by + bh);
        ctx.quadraticCurveTo(bx, by + bh, bx, by + bh - rad);
        ctx.lineTo(bx, by + rad);
        ctx.quadraticCurveTo(bx, by, bx + rad, by);
        ctx.closePath();
        ctx.fill();
        ctx.drawImage(qc, qrX, qrY);
      }catch(e){ /* ignore QR errors */ }
    }

    ctx.fillStyle = '#C9930A';
    ctx.font = '600 26px Cinzel, Georgia, serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText('asrnaam.com', W / 2, qrY + qrSize + 34);

    ctx.fillStyle = 'rgba(245,236,215,0.5)';
    ctx.font = '500 14px Cinzel, Georgia, serif';
    ctx.fillText('S C A N   T O   R E A D   T H E   L E T T E R S', W / 2, qrY + qrSize + 70);

    return canvas;
  }

  function downloadCanvas(canvas, filename){
    if(canvas.toBlob){
      canvas.toBlob(function(blob){
        if(!blob) return;
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url; a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function(){
          URL.revokeObjectURL(url);
          a.remove();
        }, 250);
      }, 'image/png');
    } else {
      var dataUrl = canvas.toDataURL('image/png');
      var a2 = document.createElement('a');
      a2.href = dataUrl; a2.download = filename;
      document.body.appendChild(a2);
      a2.click();
      a2.remove();
    }
  }

  async function saveCardFlow(data, btn){
    var labelEl = btn.querySelector('.cta-label');
    var orig = labelEl ? labelEl.textContent : '';
    if(labelEl) labelEl.textContent = 'Composing card…';
    btn.disabled = true;
    btn.classList.add('busy');
    try{
      ensureFonts();
      await loadScript(QR_CDN);
      if(document.fonts && document.fonts.ready){
        try{ await document.fonts.ready; }catch(e){}
      }
      // Tiny delay so loaded Noto fonts paint into canvas
      await new Promise(function(r){ setTimeout(r, 60); });
      var canvas = render(data);
      downloadCanvas(canvas, data.slug + '-reading.png');
      if(labelEl) labelEl.textContent = 'Saved ✓';
      setTimeout(function(){
        if(labelEl) labelEl.textContent = orig;
        btn.disabled = false;
        btn.classList.remove('busy');
      }, 1800);
    }catch(e){
      if(labelEl) labelEl.textContent = 'Try again';
      btn.disabled = false;
      btn.classList.remove('busy');
    }
  }

  function injectCTA(data){
    if(document.querySelector('.asr-save-card-cta')) return;
    var hero = document.querySelector('.hero');
    if(!hero) return;
    var wrap = document.createElement('div');
    wrap.className = 'asr-save-card-wrap';
    wrap.innerHTML =
      '<button type="button" class="asr-save-card-cta" aria-label="Save this reading as an image">' +
        '<span class="cta-icon" aria-hidden="true">' +
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
            '<rect x="3" y="3" width="18" height="18" rx="2"/>' +
            '<circle cx="8.5" cy="8.5" r="1.5"/>' +
            '<path d="M21 15l-5-5L5 21"/>' +
          '</svg>' +
        '</span>' +
        '<span class="cta-body">' +
          '<span class="cta-label">Save reading as image</span>' +
          '<span class="cta-hint">1080 × 1350 · with QR · ready for Instagram &amp; Threads</span>' +
        '</span>' +
        '<span class="cta-arrow" aria-hidden="true">→</span>' +
      '</button>';
    if(hero.nextSibling){
      hero.parentNode.insertBefore(wrap, hero.nextSibling);
    } else {
      hero.parentNode.appendChild(wrap);
    }
    wrap.querySelector('.asr-save-card-cta').addEventListener('click', function(){
      saveCardFlow(data, this);
    });
  }

  function injectShareExtras(data){
    var row = document.querySelector('.asr-share-hero-row');
    if(!row || row.querySelector('.asr-share-btn.ig')) return;

    var msg = data.name + ' — ' + (data.meaning || 'Islamic name meaning').split('.')[0];
    var url = data.url;

    // Instagram — triggers card save + copies caption (IG has no web-share intent)
    var ig = document.createElement('button');
    ig.type = 'button';
    ig.className = 'asr-share-btn ig';
    ig.setAttribute('aria-label','Save card and copy caption for Instagram');
    ig.innerHTML =
      '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
      '<path d="M7.5 2h9A5.5 5.5 0 0 1 22 7.5v9A5.5 5.5 0 0 1 16.5 22h-9A5.5 5.5 0 0 1 2 16.5v-9A5.5 5.5 0 0 1 7.5 2zm0 2A3.5 3.5 0 0 0 4 7.5v9A3.5 3.5 0 0 0 7.5 20h9a3.5 3.5 0 0 0 3.5-3.5v-9A3.5 3.5 0 0 0 16.5 4h-9zM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6zm5.5-3.25a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5z"/>' +
      '</svg>Instagram';
    var igOrig = ig.innerHTML;
    ig.addEventListener('click', function(){
      var saveBtn = document.querySelector('.asr-save-card-cta');
      if(saveBtn) saveBtn.click();
      try{
        if(navigator.clipboard) navigator.clipboard.writeText(msg + '\n' + url);
      }catch(e){}
      ig.innerHTML = '✓ Card saved · caption copied';
      setTimeout(function(){ ig.innerHTML = igOrig; }, 2600);
    });

    // Threads — has a public intent endpoint
    var th = document.createElement('a');
    th.className = 'asr-share-btn th';
    th.target = '_blank';
    th.rel = 'noopener';
    th.href = 'https://www.threads.net/intent/post?text=' + encodeURIComponent(msg + '\n' + url);
    th.setAttribute('aria-label','Share on Threads');
    th.innerHTML =
      '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
      '<path d="M12.18 21.95h-.05c-3.3-.02-5.85-1.13-7.57-3.3C3.05 16.74 2.27 14.05 2.3 11.07c0-3 .81-5.59 2.4-7.49C6.42 1.49 8.93.48 12.12.48h.05c2.43.02 4.47.61 6.03 1.76 1.47 1.08 2.5 2.63 3.07 4.59l-1.78.5c-.94-3.27-3.16-4.97-6.6-5h-.04c-2.5 0-4.37.78-5.57 2.32-1.13 1.45-1.72 3.54-1.72 6.21 0 2.66.59 4.74 1.74 6.18 1.2 1.51 3.07 2.29 5.55 2.31h.04c2.24-.02 3.72-.55 4.94-1.79.7-.71 1.07-1.46 1.18-2.36-.42-.23-.93-.4-1.5-.5-.96-.16-2-.03-2.85.38-.61.29-1.06.74-1.27 1.25-.18.44-.21.96-.07 1.46.13.46.42.86.81 1.15-.7.2-1.55.18-2.23-.28-.79-.53-1.27-1.45-1.31-2.52-.06-1.45.62-2.78 1.88-3.66 1.34-.93 3.21-1.32 5.27-1.1.74.08 1.43.27 2.07.55-.06-.75-.27-1.34-.65-1.79-.45-.53-1.13-.79-2.06-.79-.06 0-.12 0-.18.01-.84.02-1.62.31-2.13.79l-1.27-1.32c.92-.86 2.13-1.3 3.41-1.33h.27c1.46 0 2.62.49 3.46 1.46.79.91 1.18 2.19 1.16 3.81 1.4.7 2.42 1.74 2.96 3.04.51 1.22.62 2.65.32 4.12-.43 2.06-1.55 3.72-3.27 4.83-1.42.92-3.16 1.38-5.17 1.38z"/>' +
      '</svg>Threads';

    row.appendChild(ig);
    row.appendChild(th);
  }

  function init(){
    var data = readPageData();
    if(!data || !data.name) return;
    injectCTA(data);
    injectShareExtras(data);
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
