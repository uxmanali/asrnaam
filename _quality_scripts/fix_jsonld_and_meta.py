#!/usr/bin/env python3
"""
Agent H - SEO structured-data repair (idempotent, validated before write).

1. JSON-LD repair: FAQPage blocks with unescaped double-quotes inside string
   values (e.g. an embedded Quran quotation) break JSON parsing -> Search
   Console "Unparsable structured data". Re-escape only the *stray* quotes
   (those not acting as JSON structural terminators); re-validate before write.
2. Meta leak: strip <span ...> markup leaked inside meta/og/twitter
   description content="..." attributes.
"""
import re, json, glob

LD_RE = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)

def repair_json_string_quotes(s):
    out=[]; in_str=False; i=0; n=len(s)
    while i<n:
        ch=s[i]
        if not in_str:
            out.append(ch)
            if ch=='"': in_str=True
            i+=1; continue
        if ch=='\\':
            out.append(ch)
            if i+1<n: out.append(s[i+1]); i+=2
            else: i+=1
            continue
        if ch=='"':
            j=i+1
            while j<n and s[j] in ' \t\r\n': j+=1
            nxt=s[j] if j<n else ''
            if nxt in (':',',','}',']',''):
                out.append(ch); in_str=False; i+=1
            else:
                out.append('\\"'); i+=1
            continue
        out.append(ch); i+=1
    return ''.join(out)

def fix_ld(content):
    changed=False
    def _sub(m):
        nonlocal changed
        head,body,tail=m.group(1),m.group(2),m.group(3)
        try: json.loads(body); return m.group(0)
        except Exception:
            rep=repair_json_string_quotes(body)
            try: json.loads(rep)
            except Exception: return m.group(0)
            changed=True; return head+rep+tail
    return LD_RE.sub(_sub,content),changed

META_RE=re.compile(r'(<meta[^>]*?(?:name="description"|property="og:description"|name="twitter:description")[^>]*?content=")([^"]*<[^"]*?)(")',re.I)
def fix_meta(content):
    changed=False
    def _clean(m):
        nonlocal changed
        pre,val,post=m.group(1),m.group(2),m.group(3)
        s=re.sub(r'<[^>]*>','',val); s=re.sub(r'<[^"]*$','',s); s=re.sub(r'\s{2,}',' ',s).strip()
        if s!=val: changed=True; return pre+s+post
        return m.group(0)
    return META_RE.sub(_clean,content),changed

def main():
    roots=['names/*/index.html','ar/names/*/index.html','ur/names/*/index.html',
           'blog/*/index.html','ilm-ul-huroof/*/index.html','letters/*/index.html']
    files=sorted(set(f for pat in roots for f in glob.glob(pat)))
    ld_fixed=[]; meta_fixed=[]; still_bad=[]
    for f in files:
        try: c=open(f,encoding='utf-8').read()
        except: continue
        orig=c
        c,ld_ch=fix_ld(c); c,meta_ch=fix_meta(c)
        if c!=orig:
            open(f,'w',encoding='utf-8').write(c)
            if ld_ch: ld_fixed.append(f)
            if meta_ch: meta_fixed.append(f)
    for f in files:
        try: c=open(f,encoding='utf-8').read()
        except: continue
        for m in LD_RE.finditer(c):
            try: json.loads(m.group(2))
            except Exception as e: still_bad.append((f,str(e)[:50]))
    print("JSON-LD fixed:",len(ld_fixed))
    print("Meta leaks fixed:",len(meta_fixed),meta_fixed)
    print("Remaining invalid JSON-LD:",len(still_bad))
    for f,e in still_bad[:10]: print("  STILL BAD:",f,e)

if __name__=='__main__': main()
