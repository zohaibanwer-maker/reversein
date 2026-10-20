# RuleWrite — Streamlit text editor

A runnable, original rule-based text editing app built around the reconstructed Turnitout-style JSON resources. No API key is needed.

## Start on Windows

Install Python 3.12, extract this folder, and open a terminal in it:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Or double-click `start_windows.bat` after installing Python. Open http://localhost:8501 if the browser does not open automatically.

## Start on Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run streamlit_app.py
```

## Deploy on Streamlit Community Cloud

1. Create your own GitHub repository and upload the **contents** of this folder, including `rules/`, `configs/`, and `.streamlit/`. Do not upload only the ZIP.
2. In Streamlit Community Cloud, choose **Create app** and select your repository and branch.
3. Set the main file path to `streamlit_app.py`.
4. Select Python 3.12 in advanced settings and deploy. No secrets are required.

Keep `requirements.txt` next to `streamlit_app.py`. If you upload this as a nested directory instead, use its full path (for example `turnitout-streamlit/streamlit_app.py`).

Deployment reference: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies

## Included behavior

- Paste text or upload a UTF-8 `.txt` / `.md` file, up to 100,000 characters.
- Apply single-pass phrase substitutions; optionally include synonym candidates.
- Set rewrite intensity, a repeatable random seed, and custom protected terms.
- Review replacement locations and a before/after diff.
- Download edited text and a JSON change report.
- Inspect the dictionary and academic taxonomy.
- No document writes to disk or external AI API calls. On Cloud, processing takes place on the server; session text remains in server memory while used.

The intensity controls the selection of eligible matches, not a percentage of total words changed. Results depend on the available dictionary. The same text and settings produce the same result.

## Scope

This is a new application, not the missing proprietary Turnitout core. It executes phrase rules and optional synonyms. Other original resource files are provided for future development; voice conversion, sentence fusion, automatic citations and detector scoring are not implemented.

TXT and basic Markdown are supported. DOCX, PDF, source-code files and full LaTeX documents are not supported. Recognized fenced code, inline code, basic math, quotes, Markdown links, URLs, numeric citations, headings, pipe-table lines, numbers and protected terms are left unchanged. Regex recognition is not a full document parser. Review wording and scientific meaning before using the output. No detector-bypass claim is made.

The seven reconstructed structural-stage settings remain disabled and are not consumed by this app. Sidebar controls govern the implemented editor. `RULES_NOTES.md` documents the provenance and limitations of the original resources; this application adds `rules/editor_protection.json`, bringing the resource count to 34.

## Verification

```bash
python validate_rules.py
python -m unittest discover -s . -p "test_*.py"
```

Tests cover resource integrity, duplicate-key handling, protected spans, custom terms, deterministic output, character offsets, size limits, and the Streamlit load-example/edit/clear flow. `validation_report.json` records resource validation, not integration with the absent upstream engine.
