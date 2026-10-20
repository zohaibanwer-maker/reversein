# Reconstructed Turnitout rules package

Original resources created from the public documentation layout; not the author's missing files or a recovered copy of the closed-source engine.

## What you receive

- 33 rule/configuration JSON files with `__prompt__` metadata.
- 220 synonym keys, including explicitly inflected verb forms; 95 phrase rewrite pairs.
- Protected terms, determiners, conjunctions, hedges, qualifiers, auxiliary verbs, adverbs, adjective suffixes, transitions, discourse markers, nominalizations, voice verb records, appositives, keywords, and patterns.
- All 12 documented taxonomy filenames across five disciplines, containing 24 subfields.
- One global configuration file, a standalone Python loader, a validator, and four tests.
- A provenance manifest covering all 14 Markdown files reviewed, file-by-file schema confidence, and source commit.

## Run the checks

Requires Python 3.9 or newer; no pip packages or API keys.

```bash
cd turnitout-rules-pack
python validate_rules.py
python -m unittest discover -s . -p 'test_*.py'
python rules_loader.py
```

## Load the files

```python
from rules_loader import load_rule, load_academic_taxonomy

synonyms = load_rule('rules/synonyms.json')
phrases = load_rule('rules/phrases.json')
config = load_rule('configs/global_config.json')
taxonomy = load_academic_taxonomy()
```

The loader removes root `__prompt__` metadata and rejects duplicate JSON object keys. Taxonomy traversal is recursive and deterministic. The original engine's package name appears as both `textpipe` and `turnitout` in the docs; this loader avoids assuming either namespace.

## File contracts

| Resource | Payload after removing metadata |
|---|---|
| synonyms.json, determiners.json | Object mapping strings to lists of alternatives; documented shape |
| phrases.json | Array of `[regex, replacement]` pairs; documented shape |
| hedge_words.json, conjunctions.json, protected_terms.json | Array of strings; documented shape |
| qualifiers.json | Array of strings; array shape documented, content reconstructed |
| transitions.json, discourse_markers.json | Object of alternative lists; inferred integration schema |
| nominalizations.json, appositives.json | String-to-string object; inferred integration schema |
| voice_verbs.json | Verb-keyed morphology records; inferred integration schema |
| patterns.json | Regex/replacement pairs; filename documented, schema inferred |
| keywords.json | String list; filename documented, schema inferred |
| helper_verbs.json, adjective_suffixes.json, adverbs.json, fusion_connectors.json, sentence_split_patterns.json | Inferred filenames and schemas for resources described in prose |
| academic/general_topics.json | String list; constant is documented, path inferred |
| academic/taxonomy/*/*.json | Arrays of subfield records; outer fields documented, topic fields inferred |
| configs/global_config.json | Single settings object; mixture of documented and inferred keys |

Each list has a metadata object at index 0. Never pass that object to a word matcher. `manifest.json` and `validation_report.json` are package reports, not engine rule files.

## Integration limits and decisions

1. The inspected public commit has no Python engine, `rules/` directory, configuration JSON, dependency declaration, or application entry point. Adding this package will not make `streamlit run streamlit_app.py` work. The absent engine or a separately implemented application is required.
2. Exact upstream loader compatibility is unverified. Match these shapes against the real `rules.py` and `config.py` before integrating. Validation here covers the standalone package only.
3. `AGENTS.md` specifies `configs/global_config.json`; the changelog instead says `rules/global_config.json`. This package follows `AGENTS.md` and creates only one configuration. If the engine expects the other path, change its loader or move the file; do not maintain two drifting copies.
4. All seven documented stage rate values are included. Structural stages, synonym swaps, hedge insertion, determiner swaps, and citation insertion default to disabled pending contextual implementation. These choices differ from the guide's aggressive defaults. The standalone loader does not itself execute transformations or enforce protections.
5. Taxonomy `authors`, `journals`, and `references` arrays are deliberately empty. Topic keywords are classification hints, not evidence. Populate references with verified bibliographic records. Do not assemble fictional papers from author and journal pools.
6. `citations.json` is described as an output generated for a particular document. It is not a missing static dictionary, so no fabricated citation output is included.
7. These are practical starter dictionaries, not the claimed original 4,068+ rules. The extension guide requests additions to absent originals; its requested expansion counts are not evidence of the original contents. No claim is made to recover every undocumented rule filename.
8. Candidate alternatives are context-dependent. Preserve scientific uncertainty, causal relationships, negation, numbers, technical terms, quoted text, and references. The phrase/sentence regexes are not complete parsers for prose, LaTeX, code, or DOCX. For example, a sentence boundary regex can split abbreviations incorrectly.
9. Repository statements about detector internals, watermark removal, and guaranteed detector bypass were not validated and are not guarantees of this package. No detector performance was tested.
10. The original repository and documentation carry a proprietary license. They are not redistributed in this archive. Vocabulary and code here are newly authored; source paths and hashes are included for traceability only.

## Suggested integration order

Load resources and strip metadata; implement protected-span handling; add contextual, single-pass phrase matching; review grammar and meaning changes; then enable optional structural stages one at a time. Ensure replacements do not repeatedly rewrite their own output. DOCX, LaTeX, and code require dedicated parsers from the missing application.
