"""Standalone resource loader. This is not the unavailable Turnitout engine."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result

def load_rule(path):
    """Load UTF-8 JSON and remove root prompt metadata only."""
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    data = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_unique_object)
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if k != '__prompt__'}
    if isinstance(data, list):
        return [v for v in data if not (isinstance(v, dict) and set(v) == {'__prompt__'})]
    raise ValueError(f'Expected an object or array: {path}')

def load_academic_taxonomy(root=None):
    """Return records augmented with discipline and source path."""
    base = Path(root) if root is not None else ROOT / 'rules/academic/taxonomy'
    result = []
    for path in sorted(base.rglob('*.json')):
        for record in load_rule(path):
            result.append({**record, 'discipline': path.relative_to(base).parts[0],
                           'source_file': path.relative_to(base).as_posix()})
    return result

if __name__ == '__main__':
    print(f'Synonyms: {len(load_rule("rules/synonyms.json"))}')
    print(f'Phrase rules: {len(load_rule("rules/phrases.json"))}')
    print(f'Taxonomy subfields: {len(load_academic_taxonomy())}')
