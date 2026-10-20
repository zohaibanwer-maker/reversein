import difflib
import hashlib
import json
import streamlit as st
from engine import MAX_CHARS, edit_text, resources
from rules_loader import load_academic_taxonomy

st.set_page_config(page_title='RuleWrite • Text Editor', page_icon='✍️', layout='wide')
st.title('RuleWrite')
st.caption('A rule-based writing editor • Powered by reconstructed Turnitout-style resources')

with st.sidebar:
    st.subheader('Editing options')
    intensity=st.slider('Rewrite intensity',0,100,100,step=10,help='Percentage of eligible matches selected using a fixed random seed.')
    synonyms=st.checkbox('Suggest synonym replacements',value=False,help='Synonyms can change nuance. Review every replacement.')
    seed=st.number_input('Random seed',min_value=0,max_value=2147483647,value=42)
    custom=st.text_area('Keep these terms unchanged',placeholder='One term per line',height=100)
    st.caption('Code blocks, basic math, links, quoted text and numbers are protected where recognized.')
    st.divider()
    st.caption('No API key required. The app makes no external AI calls and writes no document files to disk. Text is processed on the Streamlit server and held in the session.')

editor,rule_tab,about=st.tabs(['Editor','Rule library','About & setup'])
with editor:
    st.write('Paste text or upload a UTF-8 TXT/Markdown file. Review the suggested edits before downloading.')
    upload=st.file_uploader('Open a text file',type=['txt','md'])
    if upload is not None:
        content=upload.getvalue()
        signature=hashlib.sha256(content).hexdigest()
        if st.session_state.get('upload_signature')!=signature:
            try:
                decoded=content.decode('utf-8-sig')
                if len(decoded)>MAX_CHARS:
                    st.error(f'File exceeds {MAX_CHARS:,} characters.')
                else:
                    st.session_state['input_text']=decoded
                    st.session_state['upload_signature']=signature
                    st.session_state.pop('result',None)
            except UnicodeDecodeError:
                st.error('Please save the file using UTF-8 encoding and try again.')
    if 'input_text' not in st.session_state:
        st.session_state.input_text=''
    def example():
        st.session_state.input_text='In order to evaluate the method, we perform an analysis of the results. The results indicate that MQTT reduced latency by 12%. Further investigation is required.'
        st.session_state.pop('result',None)
    def clear():
        st.session_state.input_text=''
        st.session_state.pop('result',None)
    a,b,_=st.columns([1,1,5])
    a.button('Load example',on_click=example)
    b.button('Clear text',on_click=clear)
    text=st.text_area('Original text',key='input_text',height=260,max_chars=MAX_CHARS)
    terms=tuple(t.strip() for t in custom.splitlines() if t.strip())
    if st.button('Edit text',type='primary',disabled=not text.strip()):
        with st.spinner('Applying rules…'):
            st.session_state.result=edit_text(text,intensity,synonyms,int(seed),terms)
    result=st.session_state.get('result')
    if result:
        if result['original']!=text or result['settings']!={'intensity':intensity,'synonyms':synonyms,'seed':int(seed),'custom_terms':list(terms)}:
            st.info('The input or options changed. Click Edit text to refresh the result below.')
        cols=st.columns(3)
        cols[0].metric('Original words',len(result['original'].split()))
        cols[1].metric('Edited words',len(result['output'].split()))
        cols[2].metric('Replacements',len(result['changes']))
        st.text_area('Edited text',value=result['output'],height=260,disabled=True)
        if result['changes']:
            with st.expander('Review every replacement',expanded=True):
                st.dataframe(result['changes'],width='stretch',hide_index=True)
            with st.expander('Before / after diff'):
                diff='\n'.join(difflib.unified_diff(result['original'].splitlines(),result['output'].splitlines(),fromfile='original',tofile='edited',lineterm=''))
                st.code(diff,language='diff')
        else:
            st.info('No matching edits were applied. Try the example or adjust the options.')
        left,right=st.columns(2)
        left.download_button('Download edited text',result['output'],file_name='edited_text.txt',mime='text/plain')
        right.download_button('Download change report',json.dumps(result,ensure_ascii=False,indent=2),file_name='change_report.json',mime='application/json')
with rule_tab:
    phrases,vocabulary,protected,_,_=resources()
    left,right,third=st.columns(3)
    left.metric('Synonym entries',len(vocabulary));right.metric('Phrase rules',len(phrases));third.metric('Protected terms',len(protected))
    query=st.text_input('Search synonym dictionary').strip().lower()
    rows=[{'Word':k,'Alternatives':', '.join(v)} for k,v in vocabulary.items() if query in k.lower() or any(query in a.lower() for a in v)]
    st.dataframe(rows,width='stretch',hide_index=True)
    with st.expander('Academic taxonomy'):
        st.json(load_academic_taxonomy())
with about:
    st.markdown('''This is an original, runnable Streamlit editor built around the reconstructed JSON package. It is not the unavailable Turnitout core engine.

The app implements phrase rewrites and optional synonym substitutions. Structural transformations and automatic citations are not implemented. Taxonomy data is available for inspection.

Input support: plain text and basic Markdown. DOCX, PDF, source-code files and full LaTeX documents are not supported. Protected-span recognition is conservative but does not guarantee document syntax or meaning preservation. Review all edits.

This app does not provide an AI-detection score or guarantee detector bypass.''')
    st.code('python -m pip install -r requirements.txt\npython -m streamlit run streamlit_app.py',language='bash')
