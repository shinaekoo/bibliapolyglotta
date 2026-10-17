import sys, json, re
sys.path.insert(0, '/tmp/claude-0/-home-claude/a31ef8c1-bdb9-5849-acf2-9254bcc7b397/scratchpad')
import words
from gen1_annot import LEMMA, D, O, MANUAL, NOTE
W = re.compile(r'[^\W\d_]+')
text = json.load(open('/home/claude/bible3/data/la00.json'))[0]

CASE = {'NOM': '주격', 'GEN': '속격', 'DAT': '여격', 'ACC': '대격', 'ABL': '탈격', 'VOC': '호격', 'LOC': '처격'}
NUM = {'S': '단수', 'P': '복수'}
GEN = {'M': '남성', 'F': '여성', 'N': '중성'}
TENSE = {'PRES': '현재', 'IMPF': '미완료', 'FUT': '미래', 'PERF': '완료', 'PLUP': '과거완료', 'FUTP': '미래완료'}
VOICE = {'ACTIVE': '능동', 'PASSIVE': '수동'}
MOOD = {'IND': '직설법', 'SUB': '접속법', 'IMP': '명령법', 'INF': '부정사'}
POSK = {'N': '명사', 'ADJ': '형용사', 'V': '동사', 'VPAR': '분사', 'PREP': '전치사', 'CONJ': '접속사', 'ADV': '부사',
        'PRON': '대명사', 'NUM': '수사', 'INTERJ': '감탄사'}

def gmatch(spec, cand):
    sp = spec.split(); ip = sp[0]; f = sp[1:]
    if cand['kind'] == 'unique':
        return False
    if cand['ipos'] != ip:
        return False
    g = cand['gram']
    if ip in ('CONJ', 'INTERJ'):
        return True
    if ip == 'ADV':
        return True
    for i, x in enumerate(f):
        if i >= len(g):
            return False
        y = g[i]
        if x == '?' or x == y:
            continue
        # gender slot: candidate X / C are wildcards
        if y in ('X', 'C') and x in ('M', 'F', 'N', 'C'):
            continue
        if ip == 'PRON' and i == 2:
            continue
        if ip == 'ADJ' and i == 3 and x == 'POS' and y == 'X':
            continue
        return False
    return True

def lemma_ok(lem, cand):
    _, _, hint, filt, _, _ = LEMMA[lem]
    if hint and not any(h in cand['mean'] for h in hint.split('|')):
        return False
    if filt:
        if all(t.isdigit() for t in filt):
            if cand['info'][:len(filt)] != filt: return False
        elif not all(t in cand['info'] for t in filt):
            return False
    return True

def gram_ko(c, e_info, dpos):
    ip = c['ipos']; g = c['gram']
    if ip == 'N':
        parts = [CASE[g[0]], NUM[g[1]]]
        if len(e_info) > 2 and e_info[2] in GEN: parts.append(GEN[e_info[2]])
        return POSK['N'], parts
    if ip in ('ADJ', 'PRON', 'NUM'):
        parts = [CASE.get(g[0], g[0]), NUM.get(g[1], g[1])]
        if len(g) > 2 and g[2] in GEN: parts.append(GEN[g[2]])
        if ip == 'ADJ' and len(g) > 3 and g[3] in ('COMP', 'SUPER'): parts.append({'COMP': '비교급', 'SUPER': '최상급'}[g[3]])
        if ip == 'NUM' and len(g) > 3: parts.append({'CARD': '기수', 'ORD': '서수'}.get(g[3], ''))
        return POSK[ip], [p for p in parts if p]
    if ip == 'V':
        t, v, m, pe, n = g[:5]
        parts = [TENSE[t]]
        if 'DEP' in e_info: parts.append('수동형(디포넌트: 뜻은 능동)')
        else: parts.append(VOICE[v])
        parts.append(MOOD[m])
        if pe != '0': parts.append(pe + '인칭')
        if n in NUM: parts.append(NUM[n])
        return POSK['V'], parts
    if ip == 'VPAR':
        cs, n, gd, t, v = g[:5]
        kind = {'PRES': '현재분사', 'PERF': '완료분사(수동)', 'FUT': '미래분사'}[t]
        if t == 'FUT' and v == 'PASSIVE': kind = '동형사(동명사)'
        parts = [kind, CASE[cs], NUM[n]] + ([GEN[gd]] if gd in GEN else [])
        return '동사 분사', parts
    if ip == 'PREP':
        return POSK['PREP'], ['+' + CASE[g[0]]]
    if ip == 'CONJ':
        return POSK['CONJ'], []
    if ip == 'ADV':
        return POSK['ADV'], []
    if ip == 'INTERJ':
        return POSK['INTERJ'], []
    return ip, g


# ---- 어간·어미 뜻풀이 ----
CASEFN = {'NOM': "주어 '~이/가'", 'GEN': "'~의'", 'DAT': "'~에게, ~을 위해'", 'ACC': "목적어 '~을/를'",
          'ABL': "'~로, ~에서, ~에(때)'", 'VOC': "부르는 말 '~여'", 'LOC': "'~에서'"}
PREPKO = {('in', 'ABL'): "'~안에, ~에(서)'", ('in', 'ACC'): "'~안으로, ~로'", ('super', 'ACC'): "'~위에, ~위로'",
          ('sub', 'ABL'): "'~아래에'", ('ab', 'ABL'): "'~로부터'", ('ad', 'ACC'): "'~으로, ~에 따라'",
          ('juxta', 'ACC'): "'~에 따라'", ('secundum', 'ACC'): "'~에 따라, ~대로'"}
PERS = {('1', 'S'): '내가', ('2', 'S'): '네가', ('3', 'S'): '그가(그것이)', ('1', 'P'): '우리가', ('2', 'P'): '너희가', ('3', 'P'): '그들이(그것들이)'}
TMA = {('PRES', 'IND'): '~한다', ('IMPF', 'IND'): '~하고 있었다', ('PERF', 'IND'): '~했다', ('PLUP', 'IND'): '(그 전에 이미) ~했었다',
       ('FUT', 'IND'): '~할 것이다', ('PRES', 'SUB'): '~하게 하라, ~하기를', ('IMPF', 'SUB'): '~하도록, ~한다는 것 (과거 시점)',
       ('PRES', 'IMP'): '~하라'}
TMP = {('PRES', 'IND'): '~된다, ~해진다', ('IMPF', 'IND'): '~되고 있었다, ~해지고 있었다', ('PRES', 'SUB'): '~되게 하라, ~되기를',
       ('PRES', 'IMP'): '~되라, ~해지라'}
TMS = {('PRES', 'IND'): '~이다, 있다', ('IMPF', 'IND'): '~이었다, 있었다', ('PRES', 'SUB'): '~이게 하라, 있게 하라',
       ('IMPF', 'SUB'): '~이었다는 것, ~이도록'}
STEMK = {1: '현재 어간', 2: '현재 어간', 3: '완료 어간', 4: '완료분사 어간'}
def head(lem):
    return LEMMA[lem][0].split(',')[0].split(' (')[0].strip()
def gloss(lem):
    import re as _re
    return _re.split(r'[,;·]', LEMMA[lem][1])[0].strip()
def explain(c, lem, split, gram_ko_str, prep):
    """split = [stem, ending, (enclitic)] -> list of [text, role, meaning]"""
    ip = c['ipos']; g = c['gram']; parts = []
    stem = split[0]; end = split[1] if len(split) > 1 else ''
    enc = c.get('enclitic')
    if enc and split and split[-1] == enc:
        end = split[1] if len(split) > 2 else ''
    # stem
    if ip in ('V', 'VPAR', 'SUPINE'):
        if lem == 'sum' or (stem == '' ):
            pass
        elif lem == 'praesum':
            parts.append([stem, 'stem', "prae(앞에) + sum(있다) — '앞에 서다, 다스리다'"])
        else:
            parts.append([stem, 'stem', f"{STEMK.get(c.get('key'), '어간')} · '{gloss(lem)}'"])
    elif ip in ('N', 'ADJ', 'PRON', 'NUM'):
        parts.append([stem, 'stem', f"어간 · '{gloss(lem)}'"])
    # ending
    if ip in ('N', 'ADJ', 'PRON', 'NUM') and not end:
        cs = g[0]
        fn = (f"{prep[0]} + {CASE[cs]}: {PREPKO.get(prep, '')}" if prep and prep[1] == cs else CASEFN.get(cs, ''))
        parts = [[stem, 'whole', f"{head(lem)} · '{gloss(lem)}' — 어미 없이 쓰는 꼴 · {gram_ko_str.replace(' · ', ' ')} → {fn}"]]
    if ip in ('N', 'ADJ', 'PRON', 'NUM') and end:
        cs = g[0]; nm = {'S': '단수', 'P': '복수'}[g[1]]
        gk = gram_ko_str.replace(' · ', ' ')
        if prep and prep[1] == cs:
            fn = f"{prep[0]} + {CASE[cs]}: {PREPKO.get(prep, '')}"
        elif ip == 'ADJ' or (ip == 'NUM') or lem in ('suus', 'noster', 'omnis', 'universus', 'cunctus'):
            fn = '꾸미는 말과 성·수·격을 맞춤' + (f" ({CASEFN[cs]})" if cs in CASEFN else '')
        else:
            fn = CASEFN.get(cs, '')
        parts.append([end, 'end', f"{gk} → {fn}"])
    elif ip == 'V':
        t, v, m, pe, n = g[:5]
        dep = 'DEP' in c['info']
        if lem == 'sum' or lem == 'praesum':
            mean = TMS.get((t, m), '')
            if lem == 'praesum': mean = TMA.get((t, m), '')
        elif v == 'PASSIVE' and not dep:
            mean = TMP.get((t, m), TMA.get((t, m), ''))
        else:
            mean = TMA.get((t, m), '')
        who = PERS.get((pe, n), '')
        if m == 'IMP': who = {'S': '너는', 'P': '너희는'}[n]
        label = gram_ko_str.replace(' · ', ' ')
        txt = f"{label} → {who} {mean}".strip()
        if lem == 'sum' or stem == '':
            parts = [[(stem or '') + end, 'whole', f"sum의 불규칙 꼴 · {txt}"]]
        else:
            parts.append([end, 'end', txt])
    elif ip == 'VPAR':
        cs, n, gd, t, v = g[:5]
        if t == 'PRES': kind = "현재분사 '~하는'"
        elif t == 'PERF': kind = "완료수동분사 '~된'" + (" (est와 함께 '~되었다')" if lem == 'fio' else '')
        else: kind = "동명사 '~하기'"
        if prep and prep[1] == cs: fn = f"{prep[0]} + {CASE[cs]}: {PREPKO.get(prep, '')}"
        else: fn = CASEFN.get(cs, '')
        nmk = {'S': '단수', 'P': '복수'}[n]; csk = CASE[cs]
        parts.append([end, 'end', f"{kind} · {nmk} {csk} → {fn}" if t != 'FUT' else f"{kind} · {csk} → {fn}"])
    if not parts:
        parts.append(['·'.join(x for x in split if x), 'whole', f"변하지 않는 말 · '{gloss(lem)}'"])
    if enc:
        parts.append([enc, 'enc', {'que': "'그리고' — 앞 낱말 끝에 붙는 접속 접어", 'ne': "의문 접어 '~인가?'", 've': "'또는' — 접어"}.get(enc.lower(), '접어')])
    return parts

out_v = []; used = {}; problems = []; en_of = {}
for vi, v in enumerate(text, 1):
    toks = W.findall(v); row = []; occ = {}; prep = None; since = 9
    for i, w in enumerate(toks):
        lw = w.lower(); occ[lw] = occ.get(lw, 0) + 1
        sel = O.get(f'{vi}:{lw}#{occ[lw]}') or O.get(f'{vi}:{lw}') or D.get(lw)
        if not sel:
            problems.append((vi, i, w, 'no spec')); row.append(None); continue
        lem, spec = sel[0], sel[1]
        gover = sel[2] if len(sel) > 2 else None
        note = NOTE.get(f'{vi}:{lw}', '')
        used[lem] = True
        if spec == 'MANUAL':
            m = MANUAL[lw]
            row.append([lem, m['split'], m['pos'], m['gram'], m['note'] if not note else note, m['parts']]); since += 1; continue
        cands = [c for c in words.analyze(w) if gmatch(spec, c) and lemma_ok(lem, c)]
        if not cands:
            # relax part of speech among ADJ / PRON / NUM
            sp = spec.split()
            for alt in ('ADJ', 'PRON', 'NUM', 'N'):
                if alt == sp[0]: continue
                cands = [c for c in words.analyze(w) if gmatch(' '.join([alt] + sp[1:]), c) and lemma_ok(lem, c)]
                if cands: break
        if not cands:
            problems.append((vi, i, w, lem, spec)); row.append(None); continue
        c = dict(cands[0])
        sf = spec.split()[1:]
        c['gram'] = [x if (k < len(sf) and sf[k] not in ('?',) and x not in ('?',) and c['ipos'] not in ('PREP',)) and False else x for k, x in enumerate(c['gram'])]
        if c['ipos'] in ('PRON', 'ADJ', 'NUM', 'VPAR') and len(sf) > 2 and sf[2] in ('M', 'F', 'N'):
            c['gram'] = list(c['gram']); c['gram'][2] = sf[2]
        if c['ipos'] == 'PRON' and len(sf) > 2 and sf[2] == '?':
            c['gram'] = list(c['gram']); c['gram'][2] = 'X'
        pos, parts = gram_ko(c, c['info'], c['dpos'])
        split = [c['stem'], c['ending']] + ([c['enclitic']] if c.get('enclitic') else [])
        split = [x for x in split if x != ''] or [w]
        en_of.setdefault(lem, c['mean'])
        gstr = gover or ' · '.join(parts)
        if c['ipos'] == 'PREP':
            prep = (lem, c['gram'][0]); since = 0
        else:
            since += 1
        ctx_prep = prep if (prep and since <= 3 and c['ipos'] != 'PREP') else None
        ex = explain(c, lem, split, gstr, ctx_prep)
        if c['ipos'] == 'V': prep = None
        import full_lx as _F
        row.append([lem, split, pos, gstr, note, ex, c['idx'], _F.gcode(cands[0]), c['ipos']])
    out_v.append(row)

for p in problems: print('PROBLEM', p)
L = {}
for lem in used:
    d, ko, hint, filt, ls, en = LEMMA[lem]
    L[lem] = {'d': d, 'ko': ko, 'en': en or en_of.get(lem, ''), 'ls': ls}
json.dump({'v': out_v, 'L': L}, open('/tmp/claude-0/lx_draft.json', 'w'), ensure_ascii=False, indent=0)
# print review table
for vi, row in enumerate(out_v, 1):
    toks = W.findall(text[vi - 1])
    print(f'## {vi}: ' + ' '.join(f'{t}[{r[0] if r else "??"}:{"·".join(r[1]) if r else ""}:{r[3] if r else ""}]' for t, r in zip(toks, row)))
