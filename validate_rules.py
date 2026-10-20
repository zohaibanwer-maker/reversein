"""Validate package contracts without third-party dependencies."""
import json
import re
from rules_loader import ROOT, load_rule, load_academic_taxonomy

def require(condition, message):
    if not condition:
        raise ValueError(message)

def strings(items):
    return isinstance(items, list) and all(isinstance(s, str) and s.strip() for s in items)

def validate():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    expected = {entry['path'] for entry in manifest['files']}
    actual = {p.relative_to(ROOT).as_posix() for folder in ('rules', 'configs') for p in (ROOT / folder).rglob('*.json')}
    require(actual == expected, 'Missing or unlisted resource files')
    patterns = 0
    for entry in manifest['files']:
        path, kind = entry['path'], entry['kind']
        raw = json.loads((ROOT / path).read_text())
        header = raw if isinstance(raw, dict) else raw[0]
        require(isinstance(header.get('__prompt__'), str) and bool(header['__prompt__']), f'{path}: missing prompt')
        data = load_rule(path)
        require(len(data) == entry['entries'], f'{path}: count differs from manifest')
        if kind == 'mapping':
            require(isinstance(data, dict), path)
            for key, values in data.items():
                require(isinstance(key, str) and strings(values) and len(values)>0, f'{path}: invalid mapping')
                require(len(values) == len(set(values)), f'{path}: repeated candidate')
                require(key not in values, f'{path}: identity replacement')
        elif kind in ('string_list', 'regex_list'):
            require(strings(data) and len(data) == len(set(data)), f'{path}: invalid or repeated strings')
            if kind == 'regex_list':
                for pattern in data: re.compile(pattern); patterns += 1
        elif kind == 'regex_pairs':
            require(isinstance(data, list), path)
            seen = set()
            for pair in data:
                require(strings(pair) and len(pair)==2, f'{path}: invalid pair')
                pattern, replacement = pair
                compiled = re.compile(pattern)
                require(not compiled.search(''), f'{path}: pattern matches empty text')
                require(pattern not in seen, f'{path}: duplicate pattern')
                seen.add(pattern)
                compiled.sub(replacement, 'Example sentence for replacement validation.')
                patterns += 1
        elif kind == 'string_mapping':
            require(isinstance(data,dict) and all(isinstance(k,str) and isinstance(v,str) and v for k,v in data.items()),path)
        elif kind == 'verb_records':
            for key, record in data.items():
                require(set(record)=={'base','past','past_participle','third_person','present_participle'},path)
                require(record['base']==key and all(isinstance(v,str) and v for v in record.values()),path)
        elif kind == 'taxonomy':
            for record in data:
                require(set(record)=={'subfield_id','subfield_name','topics'},path)
                require(isinstance(record['subfield_id'],str) and isinstance(record['subfield_name'],str),path)
                require(isinstance(record['topics'],list) and bool(record['topics']),path)
                for topic in record['topics']:
                    require(set(topic)=={'topic_id','topic_name','keywords','authors','journals','references'},path)
                    require(strings(topic['keywords']) and bool(topic['keywords']),path)
                    require(topic['authors']==[] and topic['journals']==[] and topic['references']==[],f'{path}: unverified bibliography')
        elif kind == 'protection':
            require(strings(data['patterns']), path)
            for pattern in data['patterns']:
                re.compile(pattern)
                patterns += 1
        elif kind == 'config':
            for key, value in data.items():
                if key.startswith('enable_') or key.startswith('protect_'): require(type(value) is bool, path)
                if key.endswith('_rate'): require(type(value) in (int,float) and 0 <= value <= 1,path)
            traffic = data['traffic_balancing']
            require(type(traffic['enable_offload']) is bool and 0 <= traffic['offload_percentage'] <= 100,path)
            require(strings(traffic['worker_nodes']),path)
        else:
            raise ValueError(f'Unknown resource type: {kind}')
    taxonomy = load_academic_taxonomy()
    ids = [r['subfield_id'] for r in taxonomy]
    require(len(ids)==len(set(ids)), 'Duplicate taxonomy subfields')
    report = {'status':'PASS','resource_files':len(expected),'compiled_regex_patterns':patterns,
              'synonym_entries':len(load_rule('rules/synonyms.json')),
              'phrase_rules':len(load_rule('rules/phrases.json')),
              'taxonomy_files':len(list((ROOT/'rules/academic/taxonomy').rglob('*.json'))),
              'taxonomy_subfields':len(taxonomy),
              'upstream_engine_integration_tested':False}
    return report

if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
