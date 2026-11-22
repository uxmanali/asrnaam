"""Build the published CSS for migrated name pages from redesign/np.css (the readable source).
  - the one rule that touches the site header goes into asr-redesign.css between the np markers;
  - everything else goes to /asr-np.css, which migrated pages load from the body, right after the site header.
    The header paints without waiting for it, and pages that are not migrated never download it.
usage: python3 redesign/np_css.py   (run from the repo root)"""
import re
CRIT = ['#asrNavLinks']   # the site header paints before /asr-np.css is reached, so its one rule stays in the main stylesheet
START, END = '/* np:first-screen:start (built by redesign/np_css.py from redesign/np.css, do not edit here) */', '/* np:first-screen:end */'


def rules(css):
    """top-level rules as (prelude, body or None, inner_css or None)"""
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find('{', i)
        if j < 0:
            break
        pre = css[i:j].strip()
        d, k = 1, j + 1
        while d and k < n:
            d += css[k] == '{'
            d -= css[k] == '}'
            k += 1
        out.append((pre, css[j + 1:k - 1]))
        i = k
    return out


def mini(x):
    x = re.sub(r'\s+', ' ', x)
    x = re.sub(r' ?([{};,]) ?', r'\1', x)
    x = re.sub(r': ', ':', x)
    return x.replace(';}', '}').strip()


def side(sel):
    parts = [p.strip() for p in sel.split(',')]
    c = [any(t in p for t in CRIT) for p in parts]
    return 'crit' if all(c) else 'late' if not any(c) else 'both'


def split(css):
    crit, late = [], []
    for pre, body in rules(css):
        if pre.startswith('@media'):
            a, b = split(body)
            if a:
                crit.append(pre + '{' + a + '}')
            if b:
                late.append(pre + '{' + b + '}')
            continue
        s = side(pre)
        r = pre + '{' + body.strip() + '}'
        if s in ('crit', 'both'):
            crit.append(r)
        if s in ('late', 'both'):
            late.append(r)
    return ''.join(mini(x) for x in crit), ''.join(mini(x) for x in late)


if __name__ == '__main__':
    import glob, os
    src = open('redesign/np.css', encoding='utf8').read()
    crit, late = split(src)
    main = open('asr-redesign.css', encoding='utf8').read()
    if START in main:
        main = main[:main.index(START)].rstrip('\n') + '\n' + main[main.index(END) + len(END):].lstrip('\n')
    main = main.rstrip('\n') + '\n' + START + '\n' + crit + '\n' + END + '\n'
    open('asr-redesign.css', 'w', encoding='utf8').write(main)
    open('asr-np.css', 'w', encoding='utf8').write('/* AsrNaam: sections of the redesigned name page. Built by redesign/np_css.py from redesign/np.css. */\n' + late + '\n')
    print('first-screen css', len(crit), 'bytes; asr-np.css', len(late), 'bytes')
    # one extra stylesheet per language family, loaded only by those pages, so English pages download nothing more
    for f in sorted(glob.glob('redesign/np-*.css')):
        a, b = split(open(f, encoding='utf8').read())
        out = 'asr-' + os.path.basename(f)
        open(out, 'w', encoding='utf8').write('/* AsrNaam: built by redesign/np_css.py from ' + f + '. */\n' + a + b + '\n')
        print(out, len(a + b), 'bytes')
