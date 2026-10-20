"""Original conservative text editor consuming reconstructed JSON resources."""
import random
import re
from functools import lru_cache
from rules_loader import load_rule

MAX_CHARS = 100_000

@lru_cache(maxsize=1)
def resources():
    return (load_rule('rules/phrases.json'), load_rule('rules/synonyms.json'),
            load_rule('rules/protected_terms.json'), load_rule('configs/global_config.json'),
            load_rule('rules/editor_protection.json'))

def match_case(original, replacement):
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement

def edit_text(text, intensity=100, synonyms=False, seed=42, custom_terms=()):
    if not isinstance(text, str):
        raise TypeError('Text must be a string.')
    if len(text)>MAX_CHARS:
        raise ValueError(f'Please use at most {MAX_CHARS:,} characters.')
    if not 0 <= intensity <= 100:
        raise ValueError('Intensity must be between 0 and 100.')
    phrases, vocabulary, terms, config, protection = resources()
    terms = sorted(set(terms) | {t.strip() for t in custom_terms if t.strip()}, key=lambda s: (-len(s), s))
    # Protected spans are copied directly, never replaced with user-visible tokens.
    patterns = list(protection['patterns'])
    if terms:
        patterns.append(r'(?<!\w)(?:'+'|'.join(re.escape(t) for t in terms)+r')(?!\w)')
    protected = re.compile('|'.join('(?:'+p+')' for p in patterns),re.MULTILINE|re.IGNORECASE)
    candidates = [(re.compile(p,re.IGNORECASE), replacement, 'phrase') for p,replacement in phrases]
    if synonyms:
        candidates.extend((re.compile(r'(?<!\w)'+re.escape(k)+r'(?!\w)',re.IGNORECASE), v, 'synonym') for k,v in vocabulary.items())
    rng = random.Random(seed)
    changes = []
    def transform(segment, offset):
        matches = []
        for priority,(pattern, replacement, kind) in enumerate(candidates):
            for m in pattern.finditer(segment):
                matches.append((m.start(), -(m.end()-m.start()), priority, m, replacement, kind))
        cursor = 0
        out = []
        for _,_,_,m,replacement,kind in sorted(matches,key=lambda x:x[:3]):
            if m.start()<cursor:
                continue
            # Consume the match even when skipped: avoid falling back to nested rewrites.
            out.append(segment[cursor:m.start()])
            original=m.group()
            if rng.random()*100 < intensity:
                chosen = rng.choice(replacement) if isinstance(replacement,list) else replacement
                revised=match_case(original,chosen)
            else:
                revised=original
            out.append(revised)
            if revised!=original:
                changes.append({'start':offset+m.start(),'end':offset+m.end(),'before':original,'after':revised,'rule':kind})
            cursor=m.end()
        out.append(segment[cursor:])
        return ''.join(out)
    cursor=0
    result=[]
    for m in protected.finditer(text):
        result.extend((transform(text[cursor:m.start()],cursor),m.group()))
        cursor=m.end()
    result.append(transform(text[cursor:],cursor))
    return {'original':text,'output':''.join(result),'changes':changes,
            'settings':{'intensity':intensity,'synonyms':synonyms,'seed':seed,'custom_terms':list(custom_terms)}}
